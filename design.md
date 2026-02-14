# System Design & Architecture - Aira

## 1. High-Level Architecture
The system follows a **Serverless, Event-Driven Architecture** built entirely on AWS. This ensures zero idle costs and infinite scalability, essential for a student-focused public impact project.

## Architecture Diagram (Mermaid)
```mermaid
graph TD
    User((Student)) -->|Voice Note| WA[WhatsApp API / Client]
    WA -->|Webhook| API[Amazon API Gateway]
    API -->|Trigger| Lambda[Orchestrator Lambda]
    
    subgraph "Data Layer"
        S3[Amazon S3 - Audio/PDFs]
        DB[Amazon DynamoDB - User State]
    end
    
    subgraph "AI Services (The Brain)"
        Transcribe[Amazon Transcribe\n(Auto-Language Detect)]
        Bedrock[Amazon Bedrock\n(Claude 3 Haiku)]
        Polly[Amazon Polly\n(Indian Neural Voices)]
    end
    
    Lambda <--> S3
    Lambda <--> DB
    Lambda --> Transcribe
    Transcribe -->|Text| Lambda
    Lambda -->|Prompt + Context| Bedrock
    Bedrock -->|Response + Critique| Lambda
    Lambda -->|Text Response| Polly
    Polly -->|Audio Stream| Lambda
    Lambda -->|Response| API
```

## 2. Component Breakdown

### 2.1 Frontend Layer (WhatsApp Client)
- **WhatsApp Business API**: Handles incoming voice notes and text messages
- **Twilio/Meta SDK**: Converts voice messages to WAV format
- **Webhook Handler**: Receives and routes messages to backend

### 2.2 Orchestration Layer (Lambda)
- **Main Entry Point**: Processes all incoming requests
- **State Management**: Tracks interview session (question index, user language, scores)
- **Error Handling**: Graceful fallbacks for API failures

### 2.3 AI Services
- **Amazon Transcribe**: 
  - Supports 10+ Indian languages
  - Auto-detects code-switching (Hindi + English mix)
  - Real-time streaming for low-latency feedback
  
- **Amazon Bedrock (Claude 3 Haiku)**: 
  - Lightweight LLM optimized for cost
  - Evaluates technical accuracy
  - Generates better phrasings
  - Scores responses (1-10 scale)
  
- **Amazon Polly**: 
  - Indian English, Hindi, Tamil, Telugu neural voices
  - Converts feedback text to speech
  - Caches common phrases for faster delivery

### 2.4 Data Layer
- **S3 Buckets**: 
  - Stores user audio recordings (encrypted, lifecycle = 30 days)
  - Stores uploaded resumes (temporary, PII redacted)
  - Stores generated audio responses
  
- **DynamoDB Tables**: 
  - `UserProfiles`: userId, language, target_role, resume_keywords
  - `InterviewSessions`: session_id, answers, scores, progress
  - `Feedback`: question, user_answer, ai_evaluation, correction

## 3. Data Flow Walkthrough

### Use Case: User Answers a Technical Question

1. **Input**: User sends voice note via WhatsApp
2. **API Gateway**: Receives webhook, passes to Lambda
3. **Transcribe**: Converts audio to text (auto-detects language)
4. **Bedrock**: 
   - Receives user's answer + question context
   - Analyzes technical accuracy
   - Generates score (1-10)
   - Creates a corrected phrasing
5. **Polly**: Converts feedback to audio
6. **S3**: Stores user recording + AI feedback
7. **DynamoDB**: Updates session with score
8. **Response**: Sends back audio feedback via WhatsApp

## 4. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|----------|
| **Frontend** | WhatsApp API (Twilio/Meta) | Maximum reach in India |
| **Backend** | AWS Lambda (Python 3.11) | Serverless, cost-effective |
| **API Gateway** | Amazon API Gateway | Manages HTTP/Webhook traffic |
| **Speech-to-Text** | Amazon Transcribe | Native multilingual support |
| **LLM** | Amazon Bedrock (Claude 3 Haiku) | Per-token pricing, low latency |
| **Text-to-Speech** | Amazon Polly | Indian accents available |
| **Database** | DynamoDB | Serverless, fast reads/writes |
| **Storage** | S3 | Encrypted, lifecycle policies |
| **Monitoring** | CloudWatch | Real-time logs and metrics |

## 5. Latency Optimization

1. **Audio Streaming**: Use WebSocket for real-time transcription
2. **Lambda Concurrency**: Set reserved concurrency for predictable performance
3. **DynamoDB Caching**: Cache frequently accessed user profiles
4. **Polly Caching**: Pre-generate common phrases (e.g., "Good job, but...", "Let me help")
5. **Bedrock Batching**: Queue multiple evaluations for cost optimization

## 6. Security & Privacy Architecture

### 6.1 Data Encryption
- **In Transit**: TLS 1.2+ for all API calls
- **At Rest**: S3 SSE-KMS, DynamoDB encryption enabled

### 6.2 PII Handling
- **Resume Redaction**: Lambda function masks phone, email, address before sending to Bedrock
- **Audio Retention**: CloudWatch Logs retention = 7 days, S3 records = 30 days

### 6.3 Authentication
- **WhatsApp**: Meta-signed webhooks verified using HMAC-SHA256
- **User Identification**: Phone number + consent flow

## 7. Scalability & Cost Model

### 7.1 Handling 1,000+ Concurrent Users
- **Lambda**: Scales to 1,000+ concurrent executions (adjustable limit)
- **DynamoDB**: Auto-scaling with on-demand billing
- **S3**: Unlimited throughput, regional redundancy optional

### 7.2 Cost Breakdown (per user per month, assuming 10 interviews)
- Lambda: $0.20 (compute)
- Transcribe: $1.00 (audio minutes)
- Bedrock: $0.15 (token usage)
- Polly: $0.10 (synthesis)
- S3/DynamoDB: $0.05
- **Total**: ~$1.50/user/month

## 8. Error Handling & Fallbacks

- **Transcribe Failure**: Retry with exponential backoff
- **Bedrock Timeout**: Return pre-generated feedback template
- **Polly Error**: Send text feedback via WhatsApp
- **Network Issues**: Queue messages in DynamoDB for async processing

## 9. Future Enhancements

- **Video Interview**: Add Amazon Rekognition for body language analysis
- **Interview Repository**: Index past Q&As for personalized recommendations
- **Gamification**: Leaderboards, achievement badges in Lambda
- **Analytics Dashboard**: Use QuickSight for insights
