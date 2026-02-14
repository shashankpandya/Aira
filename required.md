# Requirements Document - Aira

## 1. Introduction

### 1.1 Project Overview
**Aira** is a voice-first, multilingual technical interview coach designed to bridge the employability gap for students in Tier-2/3 cities across India. The system leverages AWS Generative AI services to provide real-time, oral feedback on technical correctness and communication skills in "Hinglish" and other vernacular languages.

### 1.2 Problem Statement
Over 100 million students in India's Tier-2/3 cities possess strong technical skills but struggle with English fluency during interviews. Traditional interview prep platforms are:
- Text-heavy and English-centric
- Expensive (₹5,000-₹50,000 per course)
- Require high-bandwidth internet
- Not accessible via mobile-first interfaces

### 1.3 Solution
Aira provides a WhatsApp-based, voice-first interview coach that:
- Accepts answers in vernacular languages
- Provides real-time feedback on technical accuracy
- Teaches professional phrasing in English
- Costs <₹120/month per user
- Works on 2G/3G networks

### 1.4 Success Metrics
- **Reach**: 10,000+ active users in first 6 months
- **Engagement**: Average 5+ sessions per user per month
- **Improvement**: 30%+ increase in interview confidence scores
- **Placement**: 20%+ of users report successful job placements

## 2. User Personas
* **The Aspirant (Primary):** A final-year college student from a rural or semi-urban area. Good at coding logic but struggles with English fluency. Uses a low-end Android smartphone with 4G/3G data.
* **The Recruiter (Secondary):** Looking for candidates with strong technical logic, willing to train them on communication if the core skills are there.

## 3. Functional Requirements

### 3.1 User Onboarding & Profiling
* **FR-01:** System must allow users to register via WhatsApp or Web using a phone number.
* **FR-02:** User must be able to select their "Comfort Language" (e.g., Hindi, Tamil, Telugu) and "Target Job Role" (e.g., Java Developer, Sales Executive).
* **FR-03:** System must accept a PDF resume upload and extract key skills (e.g., "Python," "React") to customize the interview.

### 3.2 Interview Simulation (Core)
* **FR-04:** System must generate relevant technical interview questions based on the uploaded resume and target role.
* **FR-05:** System must convert text questions into natural-sounding speech (TTS) using Indian accents.
* **FR-06:** System must record user voice responses and transcribe them to text (STT), supporting code-switching (mixed English + Native language).
* **FR-07:** The AI must analyze the response for:
    * **Technical Accuracy:** Is the logic correct?
    * **Communication Style:** Confidence, hesitation, and clarity.

### 3.3 Feedback & Coaching
* **FR-08:** System must provide a "Better Phrasing" audio clip, teaching the user how to rephrase their vernacular answer into professional English.
* **FR-09:** System must generate a numerical score (1-10) for every answer to track progress.
* **FR-10:** Users must be able to replay their own recording and the AI's corrected version for comparison.

## 4. Non-Functional Requirements (NFRs)

### 4.1 Performance & Latency
* **NFR-01:** Audio-to-Audio response latency should be under 5 seconds to maintain a conversational flow.
* **NFR-02:** System must handle concurrent requests from 1,000+ users without degradation (leveraging Serverless architecture).

### 4.2 Accessibility & Usability
* **NFR-03:** The application must function on low-bandwidth networks (2G/3G) by compressing audio files.
* **NFR-04:** The User Interface (WhatsApp/Web) must require zero training to use.

### 4.3 Security & Privacy
* **NFR-05:** All PII (Personally Identifiable Information) from resumes must be redacted before passing to the LLM.
* **NFR-06:** User audio recordings must be stored in encrypted S3 buckets and deleted after a set retention period (default 30 days).

## 5. Technical Constraints

### 5.1 Platform Requirements
* **TC-01:** Must use AWS Bedrock for LLM inference (hackathon requirement)
* **TC-02:** All infrastructure must be serverless (Lambda, DynamoDB, S3)
* **TC-03:** Primary interface is WhatsApp (via Twilio or Meta API) to maximize reach
* **TC-04:** Must support offline-first architecture for low-connectivity scenarios

### 5.2 Compliance Requirements
* **TC-05:** Data residency in AWS Asia Pacific (Mumbai) region
* **TC-06:** GDPR-compliant data handling (consent, deletion, portability)
* **TC-07:** No PII sent to third-party LLMs without redaction

## 6. User Stories

### 6.1 Core User Flows

**US-01: First-Time User Onboarding**
```
As a student from a Tier-3 city,
I want to register using just my phone number,
So that I can start practicing without complex sign-ups.
```

**US-02: Resume-Based Question Generation**
```
As a job seeker,
I want to upload my resume and get relevant questions,
So that I can practice for my specific target role.
```

**US-03: Voice-Based Interview Practice**
```
As a Hindi-speaking student,
I want to answer questions in Hinglish,
So that I can focus on logic without worrying about perfect English.
```

**US-04: Real-Time Feedback**
```
As a learner,
I want to hear how to rephrase my answer professionally,
So that I can improve my communication skills.
```

**US-05: Progress Tracking**
```
As a motivated student,
I want to see my improvement over time,
So that I stay motivated to practice regularly.
```

## 7. API Requirements

### 7.1 WhatsApp Webhook Endpoints
* **POST /webhook/whatsapp**: Receive incoming messages
* **GET /webhook/whatsapp**: Verify webhook signature

### 7.2 Interview Session APIs
* **POST /api/session/start**: Initialize new interview session
* **POST /api/session/answer**: Submit voice answer
* **GET /api/session/{id}/feedback**: Retrieve AI feedback
* **GET /api/session/{id}/progress**: Get session progress

### 7.3 User Management APIs
* **POST /api/user/register**: Create new user profile
* **PUT /api/user/profile**: Update language/role preferences
* **POST /api/user/resume**: Upload and parse resume

## 8. Data Models

### 8.1 User Profile (DynamoDB)
```json
{
  "userId": "string (PK)",
  "phoneNumber": "string",
  "comfortLanguage": "string",
  "targetRole": "string",
  "resumeKeywords": ["string"],
  "createdAt": "timestamp",
  "lastActiveAt": "timestamp"
}
```

### 8.2 Interview Session (DynamoDB)
```json
{
  "sessionId": "string (PK)",
  "userId": "string (GSI)",
  "questions": [
    {
      "questionId": "string",
      "questionText": "string",
      "userAnswer": "string",
      "audioUrl": "string",
      "score": "number",
      "feedback": "string",
      "betterPhrasing": "string"
    }
  ],
  "status": "in_progress | completed",
  "createdAt": "timestamp"
}
```

## 9. Acceptance Criteria

### 9.1 Functional Acceptance
- [ ] User can register via WhatsApp in <30 seconds
- [ ] System transcribes Hinglish audio with >90% accuracy
- [ ] AI provides feedback within 5 seconds of answer submission
- [ ] User can replay their answer and AI's correction
- [ ] Progress dashboard shows improvement trends

### 9.2 Non-Functional Acceptance
- [ ] System handles 1,000 concurrent users without degradation
- [ ] Audio files compressed to <500KB for 2G compatibility
- [ ] All PII redacted before LLM processing
- [ ] 99.9% uptime over 30-day period
- [ ] Cost per user remains under $2/month

## 10. Out of Scope (V1)

- Video interview simulation
- Live mentor connections
- Mobile native apps (iOS/Android)
- Group interview practice
- Resume building tools
- Job application tracking

## 11. Dependencies & Risks

### 11.1 External Dependencies
- WhatsApp Business API availability
- AWS Bedrock model access (Claude 3 Haiku)
- Twilio/Meta webhook reliability

### 11.2 Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Bedrock quota limits | High | Request quota increase, implement queuing |
| Transcription accuracy for regional accents | Medium | Fine-tune with custom vocabulary |
| WhatsApp API costs | Medium | Optimize message frequency, use caching |
| User adoption in rural areas | High | Partner with colleges, offer free tier |

---

**Document Version**: 1.0  
**Last Updated**: February 14, 2026  
**Maintained By**: Aira Product Team  
**Approved By**: [Stakeholder Name]
