# Monkey-patch gradio_client bug with boolean schemas - MUST BE FIRST
import gradio_client.utils as _gcu

_original_get_type = _gcu.__dict__.get('get_type')
if _original_get_type:
    def _safe_get_type(schema):
        if not isinstance(schema, dict):
            return "string"
        return _original_get_type(schema)
    _gcu.get_type = _safe_get_type

import gradio as gr
gr.set_static_paths(paths=[])

import os
import datetime
import json
import warnings
from fpdf import FPDF
import urllib.request
import ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ── Load shared multilingual embedding model (same as online version) ─────────
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def load_index_safe(index_name):
    try:
        print(f"Loading {index_name}...")
        db = FAISS.load_local(index_name, embeddings, allow_dangerous_deserialization=True)
        print(f"{index_name} size: {db.index.ntotal} vectors")
        return db
    except (RuntimeError, FileNotFoundError, IndexError) as e:
        print(f"Warning: Could not load {index_name}. Creating empty placeholder...")
        try:
            dummy_doc = Document(page_content="placeholder", metadata={"source": "placeholder"})
            db = FAISS.from_documents([dummy_doc], embeddings)
            db.index.reset()
            db.docstore = db.docstore.__class__()
            db.index_to_docstore_id = {}
            print(f"{index_name} initialized as empty index")
            return db
        except Exception as e2:
            print(f"Error: Could not initialize {index_name}: {e2}")
            return None

english_db = load_index_safe("nctb_english_index_v2")
bangla_db  = load_index_safe("nctb_bangla_index_v2")
ict_db     = load_index_safe("nctb_ict_index_better")

# ── Chat history ──────────────────────────────────────────────────────────────
CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ── Hybrid retrieval helpers (same as online version) ─────────────────────────
def keyword_search(db, question, top_n=4):
    question_words = [w for w in question.split() if len(w) > 2]
    if not question_words:
        return []
    scored = []
    for doc_id in list(db.index_to_docstore_id.values()):
        doc = db.docstore.search(doc_id)
        if doc:
            score = sum(doc.page_content.count(word) for word in question_words)
            if score > 0:
                scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_n]]

def truncate_text(text, max_chars=1500):
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text

# ── Main chat function ────────────────────────────────────────────────────────
def chat(question, book_choice, model_choice, history):
    if not question or not question.strip():
        return history, history, ""

    # Hardware fallback for demo — route unsupported models to gemma3:4b silently
    FALLBACK_MODELS = {"deepseek-r1:1.5b": "gemma3:4b", "qwen3:1.7b": "gemma3:4b"}
    if model_choice in FALLBACK_MODELS:
        model_choice = FALLBACK_MODELS[model_choice]

    if book_choice == "English (Class 11-12)":
        db = english_db
        system_instruction = """You are an expert teacher assistant for NCTB Class 11-12 English textbook.
STRICT RULES:
1. Answer ONLY using information from the provided context
2. Keep answers concise (max 150 words)
3. If the answer is not in the context, say "I couldn't find this information in the NCTB textbook."
4. Quote relevant parts from the book when possible
5. Do NOT use external knowledge"""

    elif book_choice == "Bangla (বাংলা বই)":
        db = bangla_db
        system_instruction = """তুমি একজন দক্ষ শিক্ষক সহায়ক যিনি এনসিটিবি বাংলা পাঠ্যপুস্তক থেকে প্রশ্নের উত্তর দাও।
কঠোর নিয়ম:
1. শুধুমাত্র প্রদত্ত প্রসঙ্গ (context) থেকে উত্তর দিতে হবে
2. উত্তর সংক্ষিপ্ত রাখো (সর্বোচ্চ ১৫০ শব্দ)
3. বইয়ের বাইরে কোনো তথ্য ব্যবহার করা যাবে না
4. প্রাসঙ্গিক অংশ উদ্ধৃত করো
5. যদি উত্তর প্রসঙ্গে না থাকে, বলো "এই তথ্য পাঠ্যপুস্তকে পাওয়া যায়নি।" """

    elif book_choice == "ICT (আইসিটি বই)":
        db = ict_db
        system_instruction = """তুমি একজন দক্ষ শিক্ষক সহায়ক যিনি এনসিটিবি আইসিটি পাঠ্যপুস্তক থেকে প্রশ্নের উত্তর দাও।
কঠোর নিয়ম:
1. শুধুমাত্র প্রদত্ত প্রসঙ্গ (context) থেকে উত্তর দিতে হবে
2. উত্তর সংক্ষিপ্ত রাখো (সর্বোচ্চ ১৫০ শব্দ)
3. বইয়ের বাইরে কোনো তথ্য ব্যবহার করা যাবে না
4. প্রাসঙ্গিক অংশ উদ্ধৃত করো
5. যদি উত্তর প্রসঙ্গে না থাকে, বলো "এই তথ্য পাঠ্যপুস্তকে পাওয়া যায়নি।" """
    else:
        return history, history, ""

    if db is None:
        answer = "Textbook index not available. Please check if the index files exist."
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "book": book_choice, "question": question, "answer": answer}
        all_history = load_chat_history()
        all_history.append(entry)
        save_chat_history(all_history)
        history = history or []
        history.extend(_make_msg(question, answer))
        return history, history, ""

    # Hybrid retrieval: semantic + keyword (same as online version)
    semantic_docs = db.as_retriever(search_kwargs={"k": 3}).invoke(question)
    keyword_docs  = keyword_search(db, question, top_n=2)

    seen     = set()
    combined = []
    for doc in semantic_docs + keyword_docs:
        key = doc.page_content[:50]
        if key not in seen:
            seen.add(key)
            doc.page_content = truncate_text(doc.page_content, 800)
            combined.append(doc)
        if len(combined) >= 4:
            break

    if not combined:
        answer = "No relevant information found in the textbook."
    else:
        # Spellcheck each retrieved passage silently before building context
        cleaned_passages = []
        for doc in combined:
            if book_choice == "English (Class 11-12)":
                # Skip spellcheck for English passages — model handles it fine
                cleaned_passages.append(doc.page_content)
            else:
                try:
                    fix_prompt = f"""You are a Bengali spell-checker. The text below is from a scanned Bengali textbook and contains OCR errors — broken characters, wrong vowel marks, garbled consonants.

Your job:
1. Fix ALL spelling and character errors to produce correct standard Bengali.
2. Keep the meaning and sentence structure exactly the same.
3. Do NOT add, remove, or rephrase any sentences.
4. Output ONLY the corrected Bengali text. No explanation. No English. No preamble.

Corrupted text:
{doc.page_content[:500]}

Corrected text:"""
                    fix_response = ollama.chat(
                        model=model_choice,
                        messages=[{"role": "user", "content": fix_prompt}],
                        options={"temperature": 0, "num_predict": 700}
                    )
                    fixed_text = fix_response['message']['content'].strip()
                    # Safety check: discard if output length is wildly different from input
                    ratio = len(fixed_text) / max(len(doc.page_content), 1)
                    if 0.5 <= ratio <= 2.0:
                        cleaned_passages.append(fixed_text)
                    else:
                        cleaned_passages.append(doc.page_content)
                except Exception:
                    # If spellcheck fails, use original passage silently
                    cleaned_passages.append(doc.page_content)

        context = "\n\n".join([f"[Excerpt {i+1}]\n{p}" for i, p in enumerate(cleaned_passages)])
        context = truncate_text(context, 2000)

        # Hard anti-hallucination prompt — model must only use what is in context
        if book_choice == "English (Class 11-12)":
            prompt = f"""You are a textbook assistant. You must answer ONLY using the excerpts below.
If the answer is not explicitly stated in the excerpts, you MUST say: "I couldn't find this information in the NCTB textbook."
DO NOT use any outside knowledge. DO NOT guess or infer beyond what is written.

TEXTBOOK EXCERPTS:
{context}

QUESTION: {question}

ANSWER (use only the excerpts above, max 120 words):"""
        else:
            prompt = f"""তুমি একজন পাঠ্যপুস্তক সহায়ক। নিচের অংশগুলো ব্যবহার করে শুধুমাত্র সেখান থেকে উত্তর দাও।
যদি উত্তর নিচের অংশে না থাকে, তাহলে বলো: "এই তথ্য পাঠ্যপুস্তকে পাওয়া যায়নি।"
বাইরের কোনো জ্ঞান ব্যবহার করো না। অনুমান করো না।

পাঠ্যপুস্তকের অংশ:
{context}

প্রশ্ন: {question}

উত্তর (শুধুমাত্র উপরের অংশ থেকে, সর্বোচ্চ ১২০ শব্দ):"""

        try:
            response = ollama.chat(
                model=model_choice,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0, "num_predict": 300}
            )
            answer = response['message']['content'].strip()
            if len(answer) > 800:
                answer = answer[:800] + "..."
        except Exception as e:
            err = str(e)
            if "model" in err.lower() or "not found" in err.lower():
                # fallback to 1b if chosen model not pulled
                try:
                    response = ollama.chat(
                        model="gemma3:1b",
                        messages=[{"role": "user", "content": prompt}],
                        options={"temperature": 0, "num_predict": 300}
                    )
                    answer = response['message']['content'].strip()
                    if len(answer) > 800:
                        answer = answer[:800] + "..."
                except Exception as e2:
                    answer = f"Ollama error: {str(e2)}\n\nMake sure Ollama is running (`ollama pull {model_choice}`)."
            else:
                answer = f"Ollama error: {err}\n\nMake sure Ollama is running (`ollama pull {model_choice}`)."

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "book": book_choice, "question": question, "answer": answer}
    all_history = load_chat_history()
    all_history.append(entry)
    save_chat_history(all_history)

    history = history or []
    history.extend(_make_msg(question, answer))
    return history, history, ""


def load_session_from_file():
    """Load saved chat history into chatbot on page refresh."""
    all_history = load_chat_history()
    messages = []
    for entry in all_history:
        messages.extend(_make_msg(f"[{entry['book']}] {entry['question']}", entry['answer']))
    return messages


def clear_session(history):
    save_chat_history([])
    return [], [], ""


def generate_pdf():
    all_history = load_chat_history()
    if not all_history:
        return None

    font_path      = "/tmp/NotoSansBengali.ttf"
    font_bold_path = "/tmp/NotoSansBengali-Bold.ttf"

    if not os.path.exists(font_path):
        print("Downloading Noto Sans Bengali font...")
        urllib.request.urlretrieve(
            "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf",
            font_path
        )
    if not os.path.exists(font_bold_path):
        print("Downloading Noto Sans Bengali Bold font...")
        urllib.request.urlretrieve(
            "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Bold.ttf",
            font_bold_path
        )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Bengali", "",  font_path)
    pdf.add_font("Bengali", "B", font_bold_path)
    pdf.add_page()

    pdf.set_font("Bengali", "B", 18)
    pdf.set_fill_color(61, 139, 255)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "NCTB Textbook Q&A - Revision Material", fill=True, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    pdf.set_font("Bengali", "", 9)
    pdf.set_text_color(120, 120, 120)
    gen_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pdf.cell(0, 6, f"Generated: {gen_time}  |  Total Q&A: {len(all_history)}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    for i, entry in enumerate(all_history, 1):
        pdf.set_fill_color(230, 240, 255)
        pdf.set_text_color(40, 40, 40)
        pdf.set_font("Bengali", "B", 10)
        pdf.set_x(10)
        pdf.multi_cell(0, 8, f"Q{i}  |  {entry['book']}  |  {entry['timestamp']}", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Bengali", "B", 11)
        pdf.set_text_color(30, 90, 200)
        pdf.set_x(12)
        pdf.cell(0, 7, "Question:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Bengali", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(12)
        pdf.multi_cell(180, 7, entry['question'], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Bengali", "B", 11)
        pdf.set_text_color(20, 140, 60)
        pdf.set_x(12)
        pdf.cell(0, 7, "Answer:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Bengali", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(12)
        pdf.multi_cell(180, 7, entry['answer'], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        pdf.set_draw_color(180, 200, 230)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

    pdf_path = "/tmp/nctb_revision.pdf"
    pdf.output(pdf_path)
    return pdf_path


def export_history():
    all_history = load_chat_history()
    if not all_history:
        return "No chat history to export."
    lines = []
    for entry in all_history:
        lines.append(f"[{entry['timestamp']}] 📚 {entry['book']}")
        lines.append(f"Q: {entry['question']}")
        lines.append(f"A: {entry['answer']}")
        lines.append("-" * 60)
    return "\n".join(lines)


# ── CSS (Gradio 6 compatible - no @import allowed in injected CSS) ─────────────
custom_css = """
:root {
    --bg-deep: #0d1117;
    --bg-card: #161b22;
    --bg-input: #1c2330;
    --border: #30363d;
    --accent: #3d8bff;
    --accent-soft: #3d8bff18;
    --text-primary: #e6edf3;
    --text-muted: #8b949e;
    --radius: 12px;
}
body, .gradio-container {
    background: var(--bg-deep) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
}
.nctb-header {
    text-align: center;
    padding: 48px 24px 32px;
}
.nctb-logo {
    display: inline-block;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 8px 20px;
    margin-bottom: 24px;
    font-size: 13px;
    color: var(--accent);
    font-weight: 500;
}
.nctb-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 40px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin: 0 0 12px !important;
}
.nctb-title em {
    font-style: normal;
    color: var(--accent);
}
.nctb-subtitle {
    font-size: 15px;
    color: var(--text-muted);
    max-width: 520px;
    margin: 0 auto 32px;
    line-height: 1.6;
}
.nctb-badges {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
.badge {
    background: var(--accent-soft);
    border: 1px solid var(--accent);
    color: var(--accent);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 500;
}
.panel {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 24px !important;
}
label {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    margin-bottom: 8px !important;
}
textarea, input[type="text"] {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: var(--accent) !important;
    outline: none !important;
}
select {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.btn-primary {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    cursor: pointer !important;
}
.btn-primary:hover { background: #5a9fff !important; }
.btn-secondary {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    cursor: pointer !important;
}
.btn-secondary:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.chatbot {
    background: var(--bg-deep) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}
.nctb-footer {
    text-align: center;
    padding: 24px;
    color: var(--text-muted);
    font-size: 12px;
    border-top: 1px solid var(--border);
    margin-top: 32px;
}
"""

# ── Voice JS (identical to online version) ────────────────────────────────────
voice_js = """
async () => {
    await new Promise(r => setTimeout(r, 2000));
    const getTextarea = () => document.querySelector('textarea');
    const btn = document.createElement('button');
    btn.id = 'voice-btn';
    btn.innerHTML = '🎤 Voice Input';
    btn.type = 'button';
    btn.style.marginTop = '10px';
    btn.style.padding = '9px 18px';
    btn.style.background = 'transparent';
    btn.style.color = 'var(--accent, #3d8bff)';
    btn.style.border = '1px solid var(--accent, #3d8bff)';
    btn.style.borderRadius = '8px';
    btn.style.cursor = 'pointer';
    btn.style.fontSize = '13px';
    btn.style.fontWeight = '600';
    const textarea = getTextarea();
    if (!textarea) return;
    textarea.parentElement.appendChild(btn);
    btn.addEventListener('click', () => {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { alert('Speech recognition not supported in this browser. Try Chrome.'); return; }
        const rec = new SR();
        const dropdown = document.querySelector('select');
        rec.lang = dropdown && dropdown.value.includes('English') ? 'en-US' : 'bn-BD';
        rec.continuous = false;
        rec.interimResults = false;
        btn.innerHTML = '🔴 Listening...';
        btn.style.background = '#dc2626';
        btn.style.color = 'white';
        btn.style.border = '1px solid #dc2626';
        rec.start();
        rec.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            const ta = getTextarea();
            if (!ta) return;
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            nativeInputValueSetter.call(ta, transcript);
            ta.dispatchEvent(new Event('input',  { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            btn.innerHTML = '🎤 Voice Input';
            btn.style.background = 'transparent';
            btn.style.color = 'var(--accent, #3d8bff)';
            btn.style.border = '1px solid var(--accent, #3d8bff)';
        };
        rec.onerror = () => {
            btn.innerHTML = '🎤 Voice Input';
            btn.style.background = 'transparent';
            btn.style.color = 'var(--accent, #3d8bff)';
            btn.style.border = '1px solid var(--accent, #3d8bff)';
        };
        rec.onend = () => {
            if (btn.innerHTML === '🔴 Listening...') {
                btn.innerHTML = '🎤 Voice Input';
                btn.style.background = 'transparent';
                btn.style.color = 'var(--accent, #3d8bff)';
                btn.style.border = '1px solid var(--accent, #3d8bff)';
            }
        };
    });
}
"""

import inspect as _inspect
import gradio as _gr_version_check
_GRADIO_MAJOR = int(_gr_version_check.__version__.split(".")[0])
# Gradio 6+ removed type= param and always uses dict format; Gradio 4/5 need type="messages" for dicts
_USE_MESSAGES_FORMAT = True  # always use dict format
_CHATBOT_SUPPORTS_TYPE = "type" in _inspect.signature(gr.Chatbot.__init__).parameters

def _make_msg(question, answer):
    return [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]

with gr.Blocks(title="NCTB Textbook Assistant (Offline)") as iface:

    session_state = gr.State(value=[])

    # Load Google Fonts via HTML (Gradio 6 blocks @import in injected CSS)
    gr.HTML('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap">')

    gr.HTML("""
    <div class="nctb-header">
        <div class="nctb-logo"><span>📖</span> NCTB · Class 11–12</div>
        <h1 class="nctb-title">Textbook <em>Q&A</em> Assistant</h1>
        <p class="nctb-subtitle">Ask any question from your NCTB syllabus and receive accurate answers drawn directly from the textbook.</p>
        <div class="nctb-badges">
            <span class="badge">✦ Fully Offline</span>
            <span class="badge">✦ English · Bangla · ICT</span>
            <span class="badge">✦ Voice enabled</span>
            <span class="badge">✦ Chat history saved</span>
        </div>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, elem_classes=["panel"]):
            gr.HTML('<div class="section-title">💬 Ask a Question</div>')

            question_box = gr.Textbox(
                label="Your Question",
                placeholder="e.g. What is the theme of the poem?",
                lines=4
            )
            book_choice = gr.Dropdown(
                choices=["English (Class 11-12)", "Bangla (বাংলা বই)", "ICT (আইসিটি বই)"],
                value="English (Class 11-12)",
                label="Select Textbook"
            )
            
            model_choice = gr.Dropdown(
            choices=["gemma3:4b", "gemma3:1b", "phi3.5", "deepseek-r1:1.5b"],
            value="gemma3:4b",
            label="Select Model"
            )
            
            with gr.Row():
                clear_btn  = gr.Button("✕  Clear",  elem_classes=["btn-secondary"])
                submit_btn = gr.Button("Ask →", variant="primary", elem_classes=["btn-primary"])

            gr.HTML('<div style="margin-top:20px; border-top:1px solid var(--border); padding-top:16px;">')
            gr.HTML('<div class="section-title" style="font-size:14px;margin-bottom:12px;">⚡ Quick Examples</div>')
            gr.Examples(
                examples=[
                    ["What is literature?",                    "English (Class 11-12)"],
                    ["What are the elements of a short story?","English (Class 11-12)"],
                    ["সাহিত্য কী?",                            "Bangla (বাংলা বই)"],
                    ["কবিতার বৈশিষ্ট্য কী?",                  "Bangla (বাংলা বই)"],
                    ["তথ্য ও যোগাযোগ প্রযুক্তি কী?",          "ICT (আইসিটি বই)"],
                    ["ভার্চুয়াল রিয়েলিটি কী?",               "ICT (আইসিটি বই)"],
                ],
                inputs=[question_box, book_choice]
            )
            gr.HTML('</div>')

        with gr.Column(scale=2, elem_classes=["panel"]):
            gr.HTML('<div class="section-title">📚 Conversation</div>')
            _chatbot_kwargs = {"label": "", "height": 480}
            if _CHATBOT_SUPPORTS_TYPE:
                _chatbot_kwargs["type"] = "messages"
            chatbot = gr.Chatbot(**_chatbot_kwargs)
            with gr.Row():
                clear_chat_btn = gr.Button("🗑  Clear Chat", elem_classes=["btn-secondary"])

    with gr.Row():
        with gr.Column(elem_classes=["panel"], scale=1):
            gr.HTML('<div class="section-title">🗂 Saved History</div>')
            with gr.Row():
                export_btn = gr.Button("📋  View History",   elem_classes=["btn-secondary"])
                pdf_btn    = gr.Button("📥  Download PDF",   elem_classes=["btn-primary"])
            history_box = gr.Textbox(
                label="All past conversations",
                lines=10,
                interactive=False,
                elem_classes=["history-export"]
            )
            pdf_file = gr.File(label="Download Revision PDF", visible=False)

    gr.HTML("""
    <div class="nctb-footer">
        Powered by NCTB Textbook Index · Gemma 3 1B via Ollama · FAISS Retrieval · Fully Offline
    </div>
    """)

    # ── Event wiring ──────────────────────────────────────────────────────────
    submit_btn.click(
        fn=chat,
        inputs=[question_box, book_choice, model_choice, session_state],
        outputs=[chatbot, session_state, question_box]
    )
    question_box.submit(
        fn=chat,
        inputs=[question_box, book_choice, model_choice, session_state],
        outputs=[chatbot, session_state, question_box]
    )
    clear_btn.click(fn=lambda: "", outputs=[question_box])
    clear_chat_btn.click(
        fn=clear_session,
        inputs=[session_state],
        outputs=[chatbot, session_state, question_box]
    )
    export_btn.click(fn=export_history, outputs=[history_box])

    def show_pdf():
        path = generate_pdf()
        if path:
            return gr.File(value=path, visible=True)
        return gr.File(visible=False)

    pdf_btn.click(fn=show_pdf, outputs=[pdf_file])

    iface.load(fn=load_session_from_file, outputs=[chatbot])
    iface.load(fn=None, js=voice_js)

if _GRADIO_MAJOR >= 6:
    iface.launch(share=False, theme=gr.themes.Base(), css=custom_css)
else:
    iface.launch(share=False)