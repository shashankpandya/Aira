import json
import urllib.request
import urllib.error
import boto3
import uuid
import time
import os

# --- 1. AWS CLIENTS ---
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')
polly = boto3.client('polly', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)
transcribe = boto3.client('transcribe', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# --- 2. CONFIGURATION (FROM ENVIRONMENT VARIABLES) ---
BUCKET_OUT = os.environ.get('BUCKET_OUT')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN')
META_PHONE_ID = os.environ.get('META_PHONE_ID')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'aira_sessions')

# Initialize DynamoDB table
table = dynamodb.Table(DYNAMODB_TABLE)

# --- 3. HELPER FUNCTIONS ---
def send_whatsapp_message(to_number, text=None, audio_link=None, buttons=None):
    url = f"https://graph.facebook.com/v18.0/{META_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}", "Content-Type": "application/json"}
    
    if buttons:
        data = {"messaging_product": "whatsapp", "to": to_number, "type": "interactive", "interactive": {"type": "button", "body": {"text": text}, "action": {"buttons": buttons}}}
    elif audio_link:
        data = {"messaging_product": "whatsapp", "to": to_number, "type": "audio", "audio": {"link": audio_link}}
    elif text:
        data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}}
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Meta Error: {e}")

def ask_gemini(system_instruction, prompt_text, expect_json=True):
    models = ["gemini-2.5-flash", "gemini-2.0-flash"]
    last_error = ""
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        data = {"systemInstruction": {"parts": [{"text": system_instruction}]}, "contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json" if expect_json else "text/plain"}}
        
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    if "content" not in result["candidates"][0]:
                        raise Exception(f"Google AI Blocked Response (Safety/Filter)")
                    raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if expect_json:
                        return json.loads(raw_text.replace("```json\n", "").replace("```", "").strip())
                    return raw_text
            except urllib.error.HTTPError as e:
                error_body = e.read().decode()
                last_error = f"HTTP {e.code}: {error_body}"
                if e.code == 429:
                    time.sleep(3)
                    continue
                elif e.code == 404:
                    break
                raise Exception(f"Google API Error: {last_error}")
    
    raise Exception(f"Google Failed. Reason: {last_error}")

def generate_and_send_polly_audio(user_phone, text):
    polly_response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Kajal", Engine="neural")
    audio_key = f"aira_audio_{uuid.uuid4().hex}.mp3"
    s3.put_object(Bucket=BUCKET_OUT, Key=audio_key, Body=polly_response['AudioStream'].read(), ContentType="audio/mpeg")
    presigned_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_OUT, 'Key': audio_key}, ExpiresIn=3600)
    send_whatsapp_message(user_phone, audio_link=presigned_url)

# --- 4. MAIN EVENTBRIDGE HANDLER ---
def lambda_handler(event, context):
    try:
        job_name = event['detail']['TranscriptionJobName']
        status = event['detail']['TranscriptionJobStatus']
        
        try:
            user_phone = job_name.split('_')[1]
        except IndexError:
            return
        
        if status == 'FAILED':
            send_whatsapp_message(user_phone, text="⚠ The audio was too distorted to process. Please try again with clearer audio.")
            return
        
        job_info = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        transcript_uri = job_info['TranscriptionJob']['Transcript']['TranscriptFileUri']
        
        with urllib.request.urlopen(transcript_uri) as res:
            student_answer = json.loads(res.read().decode('utf-8'))['results']['transcripts'][0]['transcript']
        
        if len(student_answer.strip()) < 2:
            send_whatsapp_message(user_phone, text="⚠ I couldn't clearly hear your answer. Could you please try again?")
            return {"statusCode": 200}
        
        db_response = table.get_item(Key={'phone_number': user_phone})
        history = db_response.get('Item', {}).get('history', '')
        current_question = db_response.get('Item', {}).get('current_question', 'Please introduce yourself.')
        preference = db_response.get('Item', {}).get('preference', 'both')
        last_score = int(db_response.get('Item', {}).get('last_score', 5))
        
        if any(word in student_answer.lower() for word in ['end interview', 'stop', 'bye']):
            send_whatsapp_message(user_phone, text="📊 I heard you say 'End Interview'. Generating your report...")
            try:
                prompt = f"Review this interview history and provide a final summary with 3 strengths and 3 areas for improvement:\n{history}"
                report = ask_gemini("You are an expert recruiter.", prompt, expect_json=False)
                send_whatsapp_message(user_phone, text=f"🏆 *FINAL REPORT CARD*\n\n{report}")
                table.delete_item(Key={'phone_number': user_phone})
            except Exception as e:
                send_whatsapp_message(user_phone, text=f"⚠ Report failed: {str(e)}")
            return {"statusCode": 200}
        
        prompt = f"""You are Aira, a highly advanced, human-like AGI technical interview coach.

CRITICAL TASK: First, analyze the User Input. Is it a genuine attempt to answer the technical question, or is it a conversational command/chat?

RULE 1 (Conversational/Command): If the user is just chatting or giving a command, YOU MUST NOT GRADE IT. Set "is_technical": false, and provide a friendly response in "professional_rephrasing", then ask the next question.

RULE 2 (Technical Answer): If they are actively attempting to answer the technical question, YOU MUST GRADE IT. Set "is_technical": true, provide a score (1-10), clean the answer (remove filler words like "uh", "um", "matlab"), and provide professional rephrasing.

ADAPTIVE DIFFICULTY: The user's last score was {last_score}/10. Adjust the next question difficulty accordingly.

History: {history}
Current Question: {current_question}
User Input: {student_answer}

Respond ONLY in valid JSON: {{"is_technical": true/false, "cleaned_answer": "...", "technical_score": 0-10, "professional_rephrasing": "...", "next_question": "..."}}"""
        
        try:
            eval_json = ask_gemini("You are Aira.", prompt)
        except Exception as e:
            send_whatsapp_message(user_phone, text=f"⚠ Aira Error: {str(e)}")
            return {"statusCode": 200}
        
        is_tech = eval_json.get('is_technical', True)
        new_score = int(eval_json.get('technical_score', 0)) if is_tech else last_score
        cleaned_text = eval_json.get('cleaned_answer', student_answer)
        new_history = history + f" | Q: {current_question} A: {cleaned_text}"
        
        table.put_item(Item={'phone_number': user_phone, 'current_question': eval_json.get('next_question', ''), 'history': new_history, 'preference': preference, 'last_score': new_score})
        
        if is_tech:
            text_summary = f"*Score: {new_score}/10*\n\n*(You said: \"{cleaned_text}\")*\n\n*Correction:* {eval_json.get('professional_rephrasing', '')}\n\n*Next Question:* {eval_json.get('next_question', '')}"
            tts_script = f"You scored {new_score}. {eval_json.get('professional_rephrasing', '')} Next question: {eval_json.get('next_question', '')}"
        else:
            text_summary = f"*{eval_json.get('professional_rephrasing', '')}*\n\n*Next Question:* {eval_json.get('next_question', '')}"
            tts_script = f"{eval_json.get('professional_rephrasing', '')} {eval_json.get('next_question', '')}"
        
        send_whatsapp_message(user_phone, text=text_summary, buttons=[{"type": "reply", "reply": {"id": "hint", "title": "💡 Hint"}}, {"type": "reply", "reply": {"id": "text_only", "title": "📝 Text Only"}}, {"type": "reply", "reply": {"id": "end_interview", "title": "🛑 End Interview"}}])
        
        if preference != 'text':
            generate_and_send_polly_audio(user_phone, tts_script)
        
        return {"statusCode": 200, "body": "SUCCESS"}
    
    except Exception as e:
        print(f"Error Processing Audio: {e}")
        return {"statusCode": 500}
