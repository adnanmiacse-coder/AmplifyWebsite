import gradio as gr
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

print("Loading English index...")
english_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
english_db = FAISS.load_local("nctb_english_index", english_embeddings, allow_dangerous_deserialization=True)

print("Loading Bangla index...")
bangla_embeddings = HuggingFaceEmbeddings(model_name="sagorsarker/bangla-bert-base")
bangla_db = FAISS.load_local("nctb_bangla_index", bangla_embeddings, allow_dangerous_deserialization=True)

print("Loading ICT index...")
ict_embeddings = HuggingFaceEmbeddings(model_name="sagorsarker/bangla-bert-base")
ict_db = FAISS.load_local("nctb_ict_index", ict_embeddings, allow_dangerous_deserialization=True)
print(f"ICT index size: {ict_db.index.ntotal} vectors")  # add this line

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=os.getenv("GROQ_API_KEY"))

def chat(question, book_choice):
    if book_choice == "English (Class 11-12)":
        db = english_db
        system_instruction = """You are an expert teacher assistant for NCTB Class 11-12 English textbook.

STRICT RULES:
1. Answer ONLY using information from the provided context
2. If the answer is not in the context, say "I couldn't find this information in the NCTB textbook."
3. Quote relevant parts from the book when possible
4. Keep answers clear and educational
5. Do NOT use external knowledge - stick to the textbook content only"""

    elif book_choice == "Bangla (বাংলা বই)":
        db = bangla_db
        system_instruction = """তুমি একজন দক্ষ শিক্ষক সহায়ক যিনি এনসিটিবি বাংলা পাঠ্যপুস্তক থেকে প্রশ্নের উত্তর দাও।

কঠোর নিয়ম:
1. শুধুমাত্র প্রদত্ত প্রসঙ্গ (context) থেকে উত্তর দিতে হবে
2. বইয়ের বাইরে কোনো তথ্য ব্যবহার করা যাবে না
3. প্রাসঙ্গিক অংশ উদ্ধৃত করো
4. উত্তর স্পষ্ট ও শিক্ষামূলক হতে হবে
5. যদি উত্তর প্রসঙ্গে না থাকে, বলো "এই তথ্য পাঠ্যপুস্তকে পাওয়া যায়নি।" """

    elif book_choice == "ICT (আইসিটি বই)":
        db = ict_db
        system_instruction = """তুমি একজন দক্ষ শিক্ষক সহায়ক যিনি এনসিটিবি আইসিটি পাঠ্যপুস্তক থেকে প্রশ্নের উত্তর দাও।

কঠোর নিয়ম:
1. শুধুমাত্র প্রদত্ত প্রসঙ্গ (context) থেকে উত্তর দিতে হবে
2. বইয়ের বাইরে কোনো তথ্য ব্যবহার করা যাবে না
3. প্রাসঙ্গিক অংশ উদ্ধৃত করো
4. উত্তর স্পষ্ট ও শিক্ষামূলক হতে হবে
5. যদি উত্তর প্রসঙ্গে না থাকে, বলো "এই তথ্য পাঠ্যপুস্তকে পাওয়া যায়নি।" """

    retriever = db.as_retriever(search_kwargs={"k": 10})
    docs = retriever.invoke(question)

    if not docs:
        return "No relevant information found in the textbook."

    context = "\n\n---\n\n".join([f"[Passage {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs)])

    prompt = f"""{system_instruction}

Context from NCTB Textbook:
{context}

Student Question: {question}

Answer (based strictly on the textbook):"""

    response = llm.invoke(prompt)

    if hasattr(response, 'content'):
        return response.content
    elif isinstance(response, str):
        return response
    else:
        return str(response)

iface = gr.Interface(
    fn=chat,
    inputs=[
        gr.Textbox(
            label="📝 Your Question",
            placeholder="Example: What is the definition of literature? / সাহিত্য কী? / ICT কী?",
            lines=3
        ),
        gr.Dropdown(
            choices=["English (Class 11-12)", "Bangla (বাংলা বই)", "ICT (আইসিটি বই)"],
            value="English (Class 11-12)",
            label="📚 Select Textbook"
        )
    ],
    outputs=gr.Textbox(label="💡 Answer from Textbook", lines=10),
    title="🎓 NCTB Textbook Q&A Assistant",
    description="""Ask questions from NCTB Class 11-12 textbooks and get answers directly from the book content.

**Features:**
- ✅ Answers strictly from textbook material
- ✅ Supports English, Bangla and ICT books
- ✅ Educational and accurate responses""",
    examples=[
        ["What is literature?", "English (Class 11-12)"],
        ["What are the elements of a short story?", "English (Class 11-12)"],
        ["সাহিত্য কী?", "Bangla (বাংলা বই)"],
        ["কবিতার বৈশিষ্ট্য কী?", "Bangla (বাংলা বই)"],
        ["তথ্য ও যোগাযোগ প্রযুক্তি কী?", "ICT (আইসিটি বই)"],
        ["ডেটাবেস কী?", "ICT (আইসিটি বই)"]
    ],
    cache_examples=False,  # add this line
    theme="soft"
)

iface.launch()