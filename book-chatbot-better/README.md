---
title: NCTB Textbook Q&A Assistant
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
---

# 🎓 NCTB Textbook Q&A Assistant

An intelligent question-answering system for NCTB Class 11-12 textbooks powered by RAG (Retrieval Augmented Generation).

## 📖 Available Books
- **English** (Class 11-12)
- **Bangla** (বাংলা বই)

## ✨ Features
- ✅ Answers strictly from textbook content
- ✅ Retrieves relevant passages from the books
- ✅ Supports both English and Bangla
- ✅ Educational and contextually accurate responses
- ✅ Powered by Llama 3.1 via Groq

## 🚀 Setup Instructions

### For Hugging Face Spaces:
1. Upload all files to your Space
2. Go to **Settings** → **Repository Secrets**
3. Add a new secret:
   - **Name:** `GROQ_API_KEY`
   - **Value:** Your Groq API key (get free at https://console.groq.com/)
4. Save and wait for the Space to build (~2-3 minutes)

## 🔧 Technology Stack
- **Framework:** Gradio
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2, bangla-bert-base)
- **Vector Store:** FAISS
- **LLM:** Llama 3.1 8B (via Groq)
- **RAG Chain:** LangChain

## 📝 Example Questions

**English:**
- What is literature?
- What are the elements of a short story?
- Explain the theme of the poem

**Bangla:**
- সাহিত্য কী?
- কবিতার বৈশিষ্ট্য কী?
- গল্পের উপাদান কী কী?

## ⚠️ Important Notes
- The system only answers from textbook content
- If information is not in the book, it will say so
- Responses are educational and curriculum-aligned

## 📜 License
MIT License - Free to use for educational purposes
