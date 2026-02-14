# Requirements Document - Aira

## 1. Introduction
**Aira** is a voice-first, multilingual technical interview coach designed to bridge the employability gap for students in Tier-2/3 cities in India. The system leverages AWS Generative AI services to provide real-time, oral feedback on technical correctness and communication skills in "Hinglish" and other vernacular languages.

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
* **Platform:** Must rely on AWS Bedrock for LLM inference to comply with hackathon rules.
* **Client:** Primary interface is WhatsApp (via Twilio or Meta API) to maximize reach.
