# 🎙️ Aira - AI Interview Coach

> Empowering students in Tier-2/3 cities across India with voice-first, multilingual technical interview preparation

[![AWS](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Overview

Aira is a serverless, voice-first interview coaching platform that helps students from rural and semi-urban India practice technical interviews in their comfort language. Built entirely on AWS, it provides real-time feedback on both technical accuracy and communication skills, bridging the employability gap through accessible AI-powered coaching.

## 🎯 Key Features

- **🗣️ Multilingual Support**: Practice in Hindi, Tamil, Telugu, or Hinglish (code-switching supported)
- **📱 WhatsApp Integration**: Zero-friction access via WhatsApp - no app installation required
- **🤖 AI-Powered Feedback**: Real-time evaluation using Amazon Bedrock (Claude 3 Haiku)
- **🎧 Voice-First Experience**: Natural conversation flow with Indian accent TTS
- **📊 Progress Tracking**: Detailed scoring and improvement metrics
- **💰 Cost-Effective**: Serverless architecture ensures ~$1.50/user/month
- **🔒 Privacy-First**: PII redaction and encrypted storage

## 🏗️ Architecture

Built on AWS serverless services for infinite scalability and zero idle costs:

- **Frontend**: WhatsApp Business API (Twilio/Meta)
- **Backend**: AWS Lambda (Python 3.11)
- **AI Services**: Amazon Transcribe, Bedrock, Polly
- **Storage**: Amazon S3, DynamoDB
- **API**: Amazon API Gateway

See [design.md](design.md) for detailed architecture diagrams and technical specifications.

## 🚀 Getting Started

### Prerequisites

- AWS Account with Bedrock access
- WhatsApp Business API credentials (Twilio or Meta)
- Python 3.11+
- AWS CLI configured

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/aira.git
cd aira

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Deploy infrastructure
./deploy.sh
```

## 📖 Documentation

- [Requirements Document](required.md) - Detailed functional and non-functional requirements
- [System Design](design.md) - Architecture, data flow, and technical decisions
- [API Documentation](docs/api.md) - Coming soon
- [Deployment Guide](docs/deployment.md) - Coming soon

## 🎓 Use Cases

1. **Technical Interview Prep**: Practice DSA, system design, and domain-specific questions
2. **Communication Training**: Learn to articulate technical concepts in professional English
3. **Resume-Based Coaching**: Get personalized questions based on your skills
4. **Progress Tracking**: Monitor improvement over multiple sessions

## 💡 Why Aira?

- **Accessibility**: Works on low-bandwidth networks (2G/3G)
- **Inclusivity**: Supports vernacular languages and code-switching
- **Scalability**: Handles 1,000+ concurrent users
- **Privacy**: No PII stored, encrypted data, 30-day retention
- **Impact**: Targets 100M+ students in underserved regions

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Speech-to-Text | Amazon Transcribe |
| LLM | Amazon Bedrock (Claude 3 Haiku) |
| Text-to-Speech | Amazon Polly |
| Compute | AWS Lambda |
| Database | Amazon DynamoDB |
| Storage | Amazon S3 |
| API Gateway | Amazon API Gateway |
| Monitoring | Amazon CloudWatch |

## 📊 Cost Breakdown

Per user per month (assuming 10 interview sessions):
- Lambda: $0.20
- Transcribe: $1.00
- Bedrock: $0.15
- Polly: $0.10
- Storage: $0.05
- **Total**: ~$1.50/user/month

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for AWS Generative AI Hackathon
- Inspired by the need to democratize interview preparation in India
- Special thanks to students from Tier-2/3 cities who provided feedback

## 📧 Contact

For questions or feedback, reach out at [your-email@example.com]

---

**Made with ❤️ for students across India**
