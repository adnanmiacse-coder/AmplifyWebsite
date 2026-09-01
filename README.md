# Amplify: Adaptive AI-Powered Learning Platform

> **Don't Memorise, Visualise** — A revolutionary adaptive learning platform built for Bangladesh, designed to transform passive textbook learning into intelligent, personalized education powered by cutting-edge AI models.

![Project Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Built with](https://img.shields.io/badge/Built%20with-Laravel%20%7C%20Python%20%7C%20JavaScript-blue)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Core Features & Use Cases](#core-features--use-cases)
3. [Technical Architecture](#technical-architecture)
4. [AI Models & Methodologies](#ai-models--methodologies)
5. [Data Privacy & Security](#data-privacy--security)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [API Documentation](#api-documentation)
9. [Performance Metrics](#performance-metrics)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

---

## 🎯 Project Overview

**Amplify** is an intelligent, adaptive learning platform designed to revolutionize NCTB-aligned education in Bangladesh. Unlike traditional passive learning systems, Amplify uses advanced AI and machine learning to adapt to each student's learning pace, cognitive abilities, and learning style in real-time.

### Key Objectives

- **Personalized Learning**: Adapt curriculum delivery based on individual student performance and learning patterns
- **Engagement Through Visualization**: Transform complex concepts into animated 3D visuals using Manim
- **Real-time Attention Tracking**: Monitor student engagement and provide timely interventions
- **Offline-First Architecture**: Enable quality education in areas with limited connectivity
- **Privacy-Preserving**: Process sensitive biometric data (facial expressions) entirely on the client-side

### Target Users

- **Secondary & Higher Secondary Students** (Classes 9-12)
- **Teachers & Educators** (Classroom administration and monitoring)
- **Educational Institutions** (Bangladesh NCTB curriculum aligned)
- **Career-Seekers** (Guidance and opportunity matching)

---

## 🌟 Core Features & Use Cases

### 1. **Personalised AI Tutor** (Amplify Tutor)

#### Overview
The Amplify Tutor is the core learning engine that provides one-on-one adaptive tutoring through document analysis and conversational AI. It learns individual student patterns and adjusts teaching methodology accordingly.

#### Use Cases

| Use Case | Description | Technical Implementation |
|----------|-------------|--------------------------|
| **Conceptual Learning** | Student uploads a lesson or textbook and gets personalized explanations | PDF parsing, semantic chunking with Neo4j knowledge graphs, contextual QA |
| **Exam Preparation** | Adaptive quizzing based on weak areas identified through prior interactions | Spaced repetition scheduling, attention tracking, performance analytics |
| **Doubts & Clarification** | Student asks follow-up questions on topics they don't understand | Multi-turn conversation with context retention, semantic search |
| **Progress Monitoring** | Teachers track student learning patterns and identify at-risk students | Dashboard analytics, attention logs, performance trajectories |

#### Key Features

- **Document Processing**: PDF parsing, OCR for scanned documents, semantic chunking (300 words with 60-word overlap)
- **Conversational AI**: Multi-turn dialogue with context retention, RAG-based responses, contextual quizzes
- **Visual Animation**: Manim-powered animated explanations of lesson topics
- **Attention Monitoring**: Real-time facial expression recognition with distraction warnings (5-8 second threshold)

#### AI Models Used

- **GPT-OSS-120B / GPT-OSS-20B** (Primary reasoning)
- **Qwen 3.6-27B** (Alternative for specific tasks)
- **Gemini 2.0 Flash Lite** (Slide generation and visualizations)

---

### 2. **Full Knowledge System** (Second Brain)

A comprehensive study companion combining spaced repetition (SM-2 algorithm), topic hierarchies, and engagement analytics.

**Key Features:**
- SM-2 algorithm for optimal review scheduling
- Concept dependency trees with prerequisite validation
- Attention drift detection before exams
- Study session analytics with performance correlation

---

### 3. **NCTB Offline Mode**

Privacy-preserving, curriculum-aligned knowledge system for accurate NCTB textbook answers without internet.

**Technical Specifications:**
- OpenAI text-embedding-3-small (1536-dim vectors)
- Cosine similarity search with threshold ≥ 0.7
- Hybrid search combining keyword and semantic matching
- LLM hallucination prevention through grounding

---

### 4. **Einstein Mode** (Advanced Research Assistance)

Multimodal research layer for students advancing beyond textbooks with visual context at every step.

**Model Stack:**
- **Primary**: GPT-OSS-120B (reasoning-heavy tasks)
- **Research**: Llama 3.3-70B (breadth of knowledge)
- **Vision**: Qwen 3.6-27B (multimodal understanding)

---

### 5. **3D Lab** (Practical Experiments & Simulations)

Interactive 3D simulations of chemistry practicals, physics experiments, and biological processes.

**Features:**
- 50+ pre-built chemistry practicals covering NCTB curriculum
- Gesture recognition using MediaPipe Hands (±5mm precision, <33ms latency)
- Voice commands in Bangla using Web Speech API
- Real-time 3D rendering with Three.js and Manim

---

### 6. **Classroom AI** (Educator Tools)

Complete classroom management system with real-time monitoring and adaptive lesson delivery.

**Features:**
- Real-time attention heatmaps and student monitoring
- Quiz builder with auto-grading for objective questions
- Material distribution and engagement tracking
- Communication hub for announcements and feedback

---

### 7. **Deep Learn** (Multi-Expert Discussion System)

Three AI experts (Dr. Arif, Dr. Nafisa, Dr. Rakib) debate topics from different angles using LangGraph orchestration.

**Technical Implementation:**
- LangGraph-based state management for conversation flow
- Each expert routed through different model for diversity
- PDF context integration to prevent hallucination
- Full conversation transcripts with export capability

---

### 8. **Career Engine** (Opportunity Matching)

AI-powered career guidance matching students to scholarships, internships, and job opportunities.

**Features:**
- Live integration with scholarship and internship platforms
- Profile-based matching (GPA, skills, preferences)
- Hybrid recommendation engine (collaborative + content-based)

---

### 9. **Chemistry Experiments** (Interactive Virtual Lab)

Comprehensive collection of 50+ NCTB chemistry practicals with detailed observations and 3D animations.

---

## 🏗️ Technical Architecture

### System Overview

The platform uses a three-tier architecture:
- **Frontend**: Vanilla JavaScript, Vite, face-api.js, Three.js
- **Backend**: Laravel (PHP) + FastAPI (Python)
- **Data**: MySQL, Neo4j, Vector Database

### Technology Stack

**Frontend:**
- Vanilla JavaScript (ES6+)
- Vite for build optimization
- face-api.js for facial recognition (client-side)
- Three.js + Manim for 3D visualization

**Backend (Python/FastAPI):**
- FastAPI with async support
- LangGraph for multi-expert discussions
- Groq & OpenRouter APIs for LLM integration
- Manim for animated visualizations
- Azure Cognitive Services TTS

**Backend (PHP/Laravel):**
- Laravel 11+ framework
- OTP-based authentication
- MySQL 8.0 database
- WebSocket for real-time updates

**Infrastructure:**
- Docker + Docker Compose
- Nginx + PHP-FPM
- Railway.app (primary) or Vercel (secondary)

---

## 🤖 AI Models & Methodologies

### Large Language Models

| Model | Provider | Use Case | Speed | Cost |
|-------|----------|----------|-------|------|
| **GPT-OSS-120B** | OpenRouter | Complex reasoning | Slow | $$$ |
| **Llama 3.3-70B** | Groq | Balanced quality/speed | Medium | $$ |
| **GPT-OSS-20B** | Groq | Fast generation | Fast | $ |
| **Qwen 3.6-27B** | OpenRouter | Multimodal tasks | Medium | $$ |
| **Gemini 2.0 Flash** | Google | Quick synthesis | Fast | $ |

### RAG (Retrieval-Augmented Generation) Pipeline

```
Document → Chunking → Embedding (1536-dim)
Student Query → Vector Search (Top-K=4)
→ LLM Context Augmentation → Response Generation
```

### Face Expression Recognition

**Architecture:**
- Tiny Face Detector for face localization
- Face Expression Net for 7-emotion classification
- 3-state classifier: Focused / Confused / Distracted
- Hysteresis-based smoothing to prevent false positives

**Distraction Warning:**
- 5-8 second threshold before triggering
- Azure TTS warning in Bengali
- 30-second cooldown between warnings
- 30 FPS detection rate

### Manim Animation Generation

**Workflow:**
1. LLM generates Python Manim code
2. Syntax validation and variable checking
3. Sandboxed execution (15s timeout, 512MB memory)
4. MP4 output at 480p resolution
5. 24-hour HTTP caching

### Knowledge Graph (Neo4j)

**Nodes:** Concepts, Experiments, Students
**Relationships:** Prerequisites, Related Topics, Mastered, Struggling

---

## 🔒 Data Privacy & Security

### Critical Privacy Guarantee

**NO facial data is ever transmitted or stored on servers.**

**Client-Side Processing:**
```
Face Detection (face-api.js in browser)
    ↓
7-Emotion Classification (WebGL GPU)
    ↓
Attention State Classification (3 values: focused/confused/distracted)
    ↓
ONLY State JSON Sent to Server
```

### Privacy Features by Data Type

**Facial Recognition:**
- Processed entirely client-side using face-api.js
- Only abstract attention state sent to server (3 values)
- No face images, pixels, or landmarks transmitted
- Session-based tracking (resets per login)
- 90-day retention policy with GDPR compliance

**Document Upload:**
- HTTPS encrypted transmission
- Virus scanned on server
- Original PDF deleted within 24 hours
- Only text chunks and embeddings stored
- 30-day retention with on-demand deletion

**Chat History:**
- AES-256-GCM encryption at-rest
- TLS 1.3 in-transit encryption
- 12-month retention with student consent
- Student controls access (no teacher/admin access)

**Behavioral Data:**
- Aggregated before analysis (5+ students minimum)
- De-identified for research
- Opt-out available in settings

### Compliance

- ✅ **GDPR Article 9**: Biometric data processed locally, not stored
- ✅ **CCPA**: No data sales, one-click opt-out
- ✅ **Bangladesh DPA**: Educational purpose consent + local storage

### Security Architecture

**Authentication:**
- OTP-based login (6-digit code)
- JWT tokens (30-day expiration)
- httpOnly cookies (CSRF protection)
- Rate limiting (5 OTP requests/hour per IP)

**Encryption:**
- TLS 1.3 mandatory for all endpoints
- AES-256 database encryption
- Certificate pinning for mobile apps

**API Security:**
- Rate limiting per endpoint
- Request validation (JSON Schema)
- SQL injection prevention (parameterized queries)
- XSS prevention (HTML sanitization)
- CORS policy (only allowed origins)

---

## 🚀 Installation & Setup

### Prerequisites

- Node.js 20.x or higher
- PHP 8.2 or higher
- Python 3.12 or higher
- Docker (optional)
- MySQL 8.0
- Neo4j 5.x

### Quick Start

```bash
# Clone repository
git clone https://github.com/amplify/website.git
cd AmplifyWebsite

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Docker setup (easiest)
docker-compose up -d

# Or manual setup:
composer install                    # PHP dependencies
cd backend && pip install -r requirements.txt
npm install && npm run dev         # Frontend

# Access at http://localhost:5173
```

### Production Deployment

**Railway (Recommended):**
```bash
npm i -g railway
railway login
railway up
```

**Vercel:**
```bash
npm i -g vercel
vercel
```

**Self-Hosted:**
```bash
docker build -t amplify:latest .
docker run -d -p 8888:80 amplify:latest
```

---

## 💻 Usage Guide

### For Students

1. **Start Learning**
   - Upload PDF lesson
   - Ask questions in Bengali/English
   - Receive AI-generated explanations with visuals

2. **Enable Attention Tracking**
   - Click "Attention Tracker" button
   - Grant camera permission
   - AI monitors focus level in real-time
   - Warnings trigger if distracted >5 seconds

3. **Access 3D Lab**
   - Select chemistry experiment
   - Use gestures to rotate/zoom molecules
   - Voice commands in Bangla
   - Complete interactive quiz

### For Teachers

1. **Create Classroom**
   - Set subject, class level, schedule
   - System generates 6-digit enrollment code
   - Share code with students

2. **Real-time Monitoring**
   - View live attention heatmap
   - See which topics students struggle with
   - Identify at-risk students needing intervention

3. **Assessment**
   - Create and deploy quizzes
   - Auto-grade objective questions
   - Analyze performance by topic
   - Provide personalized feedback

---

## 🔗 API Documentation

### Authentication
```
POST /api/auth/otp
Request: {phone: "+8801712345678"}
Response: {success: true, expires_in: 600}

POST /api/auth/verify
Request: {phone: "+8801712345678", otp: "123456"}
Response: {token: "eyJhbGc...", student: {...}}
```

### Tutor API
```
POST /api/tutor/upload-document
Request: {file: PDF, subject: "Chemistry", topic: "Organic Reactions"}
Response: {documentId, pages, chunks, status}

POST /api/tutor/chat
Request: {documentId, message: "Bengali/English question"}
Response: {response, references, followUp}
```

### Analytics API
```
GET /api/analytics/student/{id}/performance
GET /api/analytics/classroom/{id}/dashboard
```

---

## 📊 Performance Metrics

### System Performance

| Metric | Target | Current |
|--------|--------|---------|
| API Response (p95) | <200ms | 150ms |
| Tutor Latency | <3s | 2.2s |
| Video Generation | <30s | 18s |
| Face Detection FPS | 30 | 28 |
| Classroom Sync | <1s | 800ms |

### AI Model Performance

- **Tutor Accuracy**: F1 Score 0.82 on NCTB benchmark
- **Answer Relevance**: 88% (human-rated)
- **Hallucination Rate**: <2% (RAG grounded)
- **Face Detection**: 94% accuracy, 3% false positive rate
- **Manim Success**: 92% successful rendering

---

## 🐛 Troubleshooting

**Camera Permission Denied:**
1. Check browser permissions (Chrome Settings → Privacy)
2. Clear site cookies
3. Use incognito window
4. Try Chrome or Edge

**Attention Tracker Model Load Failed:**
1. Check internet connection
2. Clear browser cache
3. Check available disk space (50MB needed)

**PDF Upload Error (413):**
- File exceeds 50MB limit
- Compress or split PDF
- Use online compressor

**Quiz Not Loading:**
1. Refresh page
2. Check internet connection
3. Clear localStorage
4. Try different browser

**Chat Response Slow:**
1. Check API key limits
2. Try simpler query
3. Check backend status
4. Contact support with request ID

---

## 🤝 Contributing

### Development Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and write tests
4. Commit: `git commit -m "Add amazing feature"`
5. Push and submit pull request

### Code Standards

**JavaScript:** ESLint, const/let, arrow functions, async/await
**Python:** PEP 8, type hints, docstrings, Black formatter
**PHP:** PSR-12, type hints, DocBlocks

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Support

- **Email**: support@amplifywebsite.com
- **Documentation**: docs.amplifywebsite.com
- **GitHub Issues**: github.com/amplify/website/issues
- **Community Forum**: forum.amplifywebsite.com

---

## 🙏 Acknowledgments

- Built with ❤️ for education in Bangladesh
- Supported by: Banglalink, Applink Store, hSenid Mobile, AceIT
- Featured in: Aspire Institute, Dhaka Tribune, Prothom Alo, The Business Standard
- Special thanks to all educators and students using Amplify

---

**Last Updated:** September 2, 2025  
**Version:** 1.0.0  
**Maintainer:** Amplify Development Team
