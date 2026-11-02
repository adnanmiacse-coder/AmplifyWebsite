from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio, ast, html, json, logging, os, re, subprocess, sys, time, uuid
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
SCENES_DIR = os.path.join(BASE_DIR, "scenes")


def resolve_frontend_dir() -> str | None:
    candidates = [
        os.getenv("FRONTEND_DIR"),
        os.path.join(BASE_DIR, "frontend"),
        os.path.join(os.getcwd(), "frontend"),
        os.path.join(PROJECT_ROOT, "frontend"),
        os.path.join(BASE_DIR, "..", "frontend"),
    ]
    seen = set()
    for candidate in candidates:
        if not candidate:
            continue
        path = os.path.abspath(candidate)
        if path in seen:
            continue
        seen.add(path)
        if os.path.isdir(path):
            print(f"Using frontend directory: {path}")
            return path

    checked = ", ".join(sorted(seen))
    try:
        base_contents = os.listdir(BASE_DIR)
    except OSError:
        base_contents = []
    print(
        "Warning: frontend directory not found; static files disabled. "
        f"Checked: {checked}. BASE_DIR={BASE_DIR} contents={base_contents}"
    )
    return None


FRONTEND_DIR = resolve_frontend_dir()

# ── LangGraph (Deep Learn feature) ──
from langgraph.graph import StateGraph, END, START
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Annotated, List, TypedDict
import operator
import shutil


def parse_env_list(name: str, default=None) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default or []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item is not None]
    except Exception:
        return [part.strip() for part in value.split(',') if part.strip()]
    return default or []


OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
API_KEYS = None
GROQ_KEYS = None
_clients = None


def get_api_keys() -> list[str]:
    global API_KEYS
    if API_KEYS is None:
        API_KEYS = parse_env_list('OPENROUTER_API_KEYS')
        if not API_KEYS:
            raise RuntimeError('OPENROUTER_API_KEYS must be configured in backend/.env or Vercel environment variables.')
    return API_KEYS


def get_groq_keys() -> list[str]:
    global GROQ_KEYS
    if GROQ_KEYS is None:
        GROQ_KEYS = parse_env_list('GROQ_KEYS')
        if not GROQ_KEYS:
            raise RuntimeError('GROQ_KEYS must be configured in backend/.env or Vercel environment variables.')
    return GROQ_KEYS


def get_clients() -> list[OpenAI]:
    global _clients
    if _clients is None:
        _clients = [
            OpenAI(
                api_key=key,
                base_url=OPENROUTER_BASE_URL,
                default_headers={
                    'HTTP-Referer': 'http://localhost:5173',
                    'X-Title': 'Amplify'
                }
            )
            for key in get_api_keys()
        ]
    return _clients


def manim_available() -> bool:
    """Return True if Manim module is runnable in current Python env."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "manim", "--version"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


app = FastAPI()
application = app
handler = app

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True)

@app.middleware("http")
async def no_cache_static_assets(request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()
    if (
        path.endswith((".js", ".css", ".html", ".svg", ".json"))
        or path.startswith("/src/")
        or path.startswith("/assets/")
        or path.startswith("/api/config")
    ):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.get("/health")
async def root_health():
    return {"status": "ok"}


# ══════════════════════════════════════════
#  LANGGRAPH — Expert Discussion (deeplearn)
# ══════════════════════════════════════════

EXPERT_SYSTEMS = {
  'expert1': """তুমি ড. আরিফ, বিষয় বিশেষজ্ঞ।
নিয়ম:
- সরাসরি বিষয়ের কথা দিয়ে শুরু করো। কোনো পরিচয় দিও না।
- "আমি ড. আরিফ", "আমি বলব", "আমি মনে করি যে" — এই ধরনের বাক্য সম্পূর্ণ নিষিদ্ধ।
- প্রথম বাক্যেই মূল বক্তব্য শুরু হবে।
- মোট ২-৩টি সম্পূর্ণ বাক্য লিখবে। প্রতিটি বাক্য দাঁড়ি (।) দিয়ে শেষ করবে।
- বাক্য যেন মাঝপথে না কাটে।
- বাংলা বানান: "হল" লিখতে হবে "হলো" হিসেবে, "বল" লিখতে হবে "বলো" হিসেবে, "কর" লিখতে হবে "করো" হিসেবে।""",

  'expert2': """তুমি ড. নাফিসা, বিশ্লেষক।
নিয়ম:
- সরাসরি বিশ্লেষণ দিয়ে শুরু করো। কোনো পরিচয় দিও না।
- "আমি ড. নাফিসা", "আমি বলব", "আমি মনে করি যে" — এই ধরনের বাক্য সম্পূর্ণ নিষিদ্ধ।
- প্রথম বাক্যেই মূল বক্তব্য শুরু হবে।
- মোট ২-৩টি সম্পূর্ণ বাক্য লিখবে। প্রতিটি বাক্য দাঁড়ি (।) দিয়ে শেষ করবে।
- বাক্য যেন মাঝপথে না কাটে।
- বাংলা বানান: "হল" লিখতে হবে "হলো" হিসেবে, "বল" লিখতে হবে "বলো" হিসেবে, "কর" লিখতে হবে "করো" হিসেবে।""",

  'expert3': """তুমি ড. রাকিব, সমালোচক।
নিয়ম:
- সরাসরি প্রশ্ন বা চ্যালেঞ্জ দিয়ে শুরু করো। কোনো পরিচয় দিও না।
- "আমি ড. রাকিব", "আমি বলব", "আমি মনে করি যে" — এই ধরনের বাক্য সম্পূর্ণ নিষিদ্ধ।
- প্রথম বাক্যেই মূল বক্তব্য শুরু হবে।
- মোট ২-৩টি সম্পূর্ণ বাক্য লিখবে। প্রতিটি বাক্য দাঁড়ি (।) দিয়ে শেষ করবে।
- বাক্য যেন মাঝপথে না কাটে।
- বাংলা বানান: "হল" লিখতে হবে "হলো" হিসেবে, "বল" লিখতে হবে "বলো" হিসেবে, "কর" লিখতে হবে "করো" হিসেবে।""",
}

NUMERIC_FORMAT_INSTRUCTION = (
    "CRITICAL NUMERIC FORMATTING RULE: Do not ever mention or use any fractional digits or fraction notation "
    "(such as 1/2, 3/4, or fractions). If a fractional digit or fraction appears, ensure it is converted to and "
    "written as a decimal number (for example, write 1/2 as 0.5, 3/4 as 0.75, 1/4 as 0.25; use approximate decimals "
    "for repeating values). Never output fractions or fractional digits; express all fractional values strictly as "
    "decimal numbers throughout your response."
)

EXPERT_NAMES = {
  'expert1': 'ড. আরিফ',
  'expert2': 'ড. নাফিসা',
  'expert3': 'ড. রাকিব',
}

EXPERT_MODELS = {
  'expert1': 'openai/gpt-oss-120b',
  'expert2': 'llama-3.3-70b-versatile',
  'expert3': 'openai/gpt-oss-20b',
}

# ── State definition ──────────────────────────
class DiscussionState(TypedDict):
    topic:       str
    phase:       str
    pdf_context: str
    dialogue:    Annotated[List[dict], operator.add]
    expert_id:   str
    reply:       str



EXPERT_INSTRUCTIONS = {
    'expert1': 'তুমি বিষয়টির মূল ধারণা, তত্ত্ব ও বৈজ্ঞানিক ব্যাখ্যা দাও। সংশ্লেষণ করো।',
    'expert2': 'তুমি তুলনামূলক বিশ্লেষণ করো, নতুন দিক আনো, ড. আরিফের বক্তব্য বিস্তার করো।',
    'expert3': 'তুমি বিদ্যমান বক্তব্যকে চ্যালেঞ্জ করো, দুর্বলতা খোঁজো, কঠিন প্রশ্ন করো।',
}

def build_expert_prompt(state: DiscussionState) -> str:
    transcript = "\n\n".join(f"[{d['name']}]: {d['text']}" for d in state['dialogue'][-12:])
    doc = f"\nডকুমেন্ট:\n{state['pdf_context']}\n" if state.get('pdf_context') else ''
    instruction = EXPERT_INSTRUCTIONS.get(state['expert_id'], '')
    return (
        f"বিষয়: {state['topic']}\n"
        f"পর্যায়: {state['phase']}\n"
        f"তোমার ভূমিকা: {instruction}\n"
        f"{doc}"
        f"\nআলোচনা:\n{transcript}\n\n"
        f"এখন সরাসরি বিষয়বস্তু দিয়ে শুরু করো। ২-৩টি সম্পূর্ণ বাক্য লিখবে, শেষ বাক্যটি অবশ্যই দাঁড়ি (।) দিয়ে শেষ করবে। কোনো পরিচয় বাক্য লিখবে না।\n"
        f"মনে রাখবে: \"হল\" লিখতে হবে \"হলো\" হিসেবে, \"বল\" লিখতে হবে \"বলো\" হিসেবে, \"কর\" লিখতে হবে \"করো\" হিসেবে।"
    )

# ── Nodes ─────────────────────────────────────
def make_expert_node(expert_id: str):
    def node(state: DiscussionState) -> dict:
        primary_model = EXPERT_MODELS[expert_id]
        fallback_models = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'llama-3.3-70b-versatile']
        models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]
        prompt_text = build_expert_prompt(state)
        messages = [
            SystemMessage(content=f"{EXPERT_SYSTEMS[expert_id]}\n\n{NUMERIC_FORMAT_INSTRUCTION}"),
            HumanMessage(content=prompt_text),
        ]
        last_err = None
        for model in models_to_try:
            for key in get_groq_keys():
                try:
                    llm_kwargs = {"api_key": key, "model": model, "max_tokens": 400, "temperature": 0.8}
                    if model.startswith('openai/gpt-oss') or model.startswith('qwen/'):
                        llm_kwargs['reasoning_effort'] = 'low'
                    llm = ChatGroq(**llm_kwargs)

                    reply = strip_intro(llm.invoke(messages).content.strip(), expert_id)
                    if reply:
                        return {
                            'reply': reply,
                            'dialogue': [{'name': EXPERT_NAMES[expert_id], 'text': reply}],
                        }
                except Exception as e:
                    last_err = e
                    is_rate_limit = '429' in str(e) or 'rate_limit' in str(e).lower()
                    print(f"[{expert_id}] {model} key failed: {e}")
                    if is_rate_limit:
                        break  # rate limit is per-model, skip remaining keys for this model
                    continue
        raise HTTPException(500, f"All Groq models/keys failed for {expert_id}: {last_err}")
    return node
# ── Routing ───────────────────────────────────
def route_to_expert(state: DiscussionState) -> str:
    return state['expert_id']

# ── Build & compile graph ─────────────────────
_builder = StateGraph(DiscussionState)
_builder.add_node('expert1', make_expert_node('expert1'))
_builder.add_node('expert2', make_expert_node('expert2'))
_builder.add_node('expert3', make_expert_node('expert3'))
_builder.add_conditional_edges(START, route_to_expert, {
    'expert1': 'expert1',
    'expert2': 'expert2',
    'expert3': 'expert3',
})
_builder.add_edge('expert1', END)
_builder.add_edge('expert2', END)
_builder.add_edge('expert3', END)

discussion_graph = _builder.compile()


os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)
app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

class Prompt(BaseModel):
    prompt: str
    context: str = ""


def call_llm(messages: list, max_tokens: int = 2500) -> str:
    """Try each API key in order, fall back on failure."""
    messages = [dict(message) for message in messages]
    system_messages = [message for message in messages if message.get("role") == "system"]
    if system_messages:
        for message in system_messages:
            if NUMERIC_FORMAT_INSTRUCTION not in message.get("content", ""):
                message["content"] = f"{message.get('content', '')}\n\n{NUMERIC_FORMAT_INSTRUCTION}"
    else:
        messages.insert(0, {"role": "system", "content": NUMERIC_FORMAT_INSTRUCTION})

    last_error = None
    for i, c in enumerate(get_clients()):
        try:
            response = c.chat.completions.create(
                model="openrouter/auto",
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  → API key {i+1} failed: {e}")
            last_error = e
            continue
    raise HTTPException(500, f"All API keys failed. Last error: {last_error}")


def extract_undefined_names(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    assigned = set()
    used = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                assigned.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.append(node.id)
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            assigned.add(node.name)
        elif isinstance(node, ast.arguments):
            for arg in node.args + node.posonlyargs + node.kwonlyargs:
                assigned.add(arg.arg)
            if node.vararg:
                assigned.add(node.vararg.arg)
            if node.kwarg:
                assigned.add(node.kwarg.arg)
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                assigned.add(node.target.id)

    safe_globals = {
        'print', 'range', 'len', 'int', 'str', 'float', 'list', 'dict',
        'set', 'tuple', 'bool', 'None', 'True', 'False', 'enumerate',
        'zip', 'map', 'filter', 'isinstance', 'type', 'super',
        'WHITE', 'BLACK', 'RED', 'BLUE', 'GREEN', 'YELLOW',
        'ORANGE', 'PURPLE', 'PINK', 'GRAY', 'GREY', 'TEAL', 'GOLD',
        'UP', 'DOWN', 'LEFT', 'RIGHT', 'IN', 'OUT', 'ORIGIN',
        'PI', 'TAU', 'DEGREES', 'DR', 'DL', 'UR', 'UL',
        'Circle', 'Square', 'Rectangle', 'Triangle', 'Arrow', 'Line',
        'Dot', 'Arc', 'Ellipse', 'Polygon', 'RegularPolygon',
        'Text', 'MathTex', 'Tex', 'MarkupText',
        'VGroup', 'Group', 'AnimationGroup',
        'Create', 'Write', 'FadeIn', 'FadeOut', 'Transform',
        'ReplacementTransform', 'MoveToTarget', 'Indicate',
        'DrawBorderThenFill', 'GrowFromCenter', 'ShrinkToCenter',
        'self', 'MovingCameraScene', 'Scene', 'ThreeDScene',
        'NumberPlane', 'Axes', 'BarChart', 'PolarPlane',
        'Flash', 'Circumscribe', 'ApplyWave', 'config',
        'LinearTransformationScene', 'ZoomedScene',
    }

    undefined = [
        name for name in used
        if name not in assigned and name not in safe_globals
    ]
    return list(set(undefined))


def check_manim_antipatterns(code: str) -> list[str]:
    """Catch known Manim API misuses before render."""
    warnings = []
    if 'self.camera.animate' in code:
        warnings.append("self.camera.animate is invalid — use self.camera.frame.animate instead")
    if '.next_to(self.camera' in code:
        warnings.append("Cannot use self.camera as a positional reference — use a Mobject or ORIGIN")
    if 'self.camera.move_to' in code:
        warnings.append("Use self.camera.frame.move_to() not self.camera.move_to()")
    if re.search(r'\.animate\.next_to\(self\.camera', code):
        warnings.append("Invalid camera reference in animate chain")
    return warnings


def fix_code_with_llm(code: str, error_msg: str, original_prompt: str) -> str:
    """Ask the LLM to fix its own broken code given the error."""
    print("  → Asking LLM to fix its own code...")
    messages = [
        {
            "role": "system",
            "content": """You fix broken Manim Community Edition code. Rules:
- Return ONLY raw Python, no markdown, no backticks, no explanation
- Fix every NameError: make sure every variable is defined before it is used
- Class name must be exactly: Scene (inheriting MovingCameraScene)
- First line: from manim import *
- Keep under 65 lines
- End with self.wait(2)"""
        },
        {
            "role": "user",
            "content": (
                f"This Manim code has an error. Fix it.\n\n"
                f"ORIGINAL PROMPT: {original_prompt}\n\n"
                f"BROKEN CODE:\n{code}\n\n"
                f"ERROR:\n{error_msg}"
            )
        }
    ]
    fixed = call_llm(messages, max_tokens=2500)
    fixed = re.sub(r'```python|```', '', fixed).strip()
    fixed = fixed.replace('class Scene(Scene):', 'class Scene(MovingCameraScene):')
    fixed = re.sub(r'(config\.background_color\s*=\s*BLACK)\s*class', r'\1\n\nclass', fixed)
    return fixed


def sanitize_code(code: str, job_id: str, original_prompt: str) -> str:
    # Check for known Manim API misuses first
    antipatterns = check_manim_antipatterns(code)
    if antipatterns:
        error_msg = "Manim API errors:\n" + "\n".join(antipatterns)
        print(f"[{job_id}] Pre-flight caught antipatterns: {antipatterns}")
        code = fix_code_with_llm(code, error_msg, original_prompt)

    # Then check for undefined names
    undefined = extract_undefined_names(code)
    if not undefined:
        return code

    error_msg = f"NameError: the following names are used but never defined: {', '.join(undefined)}"
    print(f"[{job_id}] Pre-flight caught undefined names: {undefined}")
    fixed = fix_code_with_llm(code, error_msg, original_prompt)

    still_undefined = extract_undefined_names(fixed)
    if still_undefined:
        print(f"[{job_id}] Still undefined after fix attempt: {still_undefined} — proceeding anyway")
    else:
        print(f"[{job_id}] Fix successful, undefined names resolved.")

    return fixed


def is_syntax_valid(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def generate_manim_code(prompt: str, context: str, simple: bool = False) -> str:
    length_note = "Keep under 40 lines total. Very simple animation only." if simple else "Keep under 60 lines total."
    messages = [
        {
            "role": "system",
            "content": f"""Generate ONLY executable Manim Community Edition code. Rules:
- No markdown, no backticks, no explanation, just raw Python
- Class name must be exactly: Scene inheriting MovingCameraScene
- First line must be: from manim import *
- Use config.background_color = BLACK
- {length_note}
- NEVER use MathTex or Tex — use Text() only
- Use only: Circle, Square, Arrow, Text, VGroup, Line, Dot, Create, Write, FadeIn, FadeOut, Transform, self.play(), self.wait()
- No external images, no SVG imports, no custom fonts
- CRITICAL: Every variable referenced must be assigned earlier in the same scope
- CRITICAL: Never leave any parentheses, brackets, or braces unclosed
- End with self.wait(2)"""
        },
        {
            "role": "user",
            "content": f"Create a 3Blue1Brown style Manim animation explaining: {prompt}. Context: {context}"
        }
    ]
    code = call_llm(messages, max_tokens=2500)
    code = re.sub(r'```python|```', '', code).strip()
    code = code.replace('class Scene(Scene):', 'class Scene(MovingCameraScene):')
    code = re.sub(r'(config\.background_color\s*=\s*BLACK)\s*class', r'\1\n\nclass', code)
    return code

# ── Deep Learn endpoint ───────────────────────
class TurnRequest(BaseModel):
    topic:       str
    phase:       str
    expert_id:   str
    pdf_context: str = ''
    dialogue:    List[dict] = []

import re as _re

def strip_intro(text: str, expert_id: str) -> str:
    name_map = {
        'expert1': ['আরিফ', 'Arif'],
        'expert2': ['নাফিসা', 'Nafisa'],
        'expert3': ['রাকিব', 'Rakib'],
    }
    names = name_map.get(expert_id, [])
    lines = text.strip().split('\n')
    # Drop any leading line that contains the expert's own name + intro pattern
    while lines:
        l = lines[0]
        is_intro = any(n in l for n in names) and any(
            w in l for w in ['আমি', 'বলব', 'মনে করি যে', 'একজন', 'হিসেবে']
        )
        if is_intro:
            lines.pop(0)
        else:
            break
    return '\n'.join(lines).strip()


@app.post("/turn")
async def run_turn(req: TurnRequest):
    print(f"[TURN] topic={req.topic} pdf_context_len={len(req.pdf_context)} dialogue_len={len(req.dialogue)}")
    state = {**req.model_dump(), "reply": ""}
    result = discussion_graph.invoke(state)
    return {"reply": result["reply"], "dialogue": result["dialogue"]}

@app.post("/generate")
async def generate(data: Prompt):
    import traceback
    print(f"Using API keys: {[k[:20] + '...' for k in get_api_keys()]}")
    job_id = str(uuid.uuid4())[:8]
    scene_file = os.path.join(SCENES_DIR, f"scene_{job_id}.py")
    output_video = os.path.join(VIDEOS_DIR, f"{job_id}.mp4")

    # Quick runtime check: ensure `manim` binary is available
    if not manim_available():
        msg = (
            "Manim executable not found on the server PATH.\n"
            "Install Manim Community Edition and system dependencies (ffmpeg, cairo, pango)."
        )
        print(f"[{job_id}] ERROR: {msg}")
        raise HTTPException(500, msg)

    # Step 1: Generate code, with fallback to simpler version if syntax broken
    try:
        code = generate_manim_code(data.prompt, data.context, simple=False)
        print(f"[{job_id}] Generated code:\n{code}\n")

        valid, syntax_err = is_syntax_valid(code)
        if not valid:
            print(f"[{job_id}] Syntax error in initial generation: {syntax_err}")
            print(f"[{job_id}] Regenerating with simpler prompt...")
            code = generate_manim_code(data.prompt, data.context, simple=True)
            valid, syntax_err = is_syntax_valid(code)
            if not valid:
                raise HTTPException(500, f"Generated code has syntax error after retry: {syntax_err}")

        print(f"[{job_id}] Syntax check passed.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[{job_id}] AI FAILED: {traceback.format_exc()}")
        raise HTTPException(500, f"AI generation failed: {str(e)}")

    # Step 1.5: Pre-flight sanitization
    code = sanitize_code(code, job_id, data.prompt)

    # Step 2: Save scene file
    os.makedirs(SCENES_DIR, exist_ok=True)
    with open(scene_file, "w", encoding="utf-8") as f:
        f.write(code)

    media_dir = os.path.join(BASE_DIR, f"media_{job_id}")

    # Step 3: Render with retry loop
    MAX_RETRIES = 3
    last_error = ""

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[{job_id}] Render attempt {attempt}/{MAX_RETRIES}")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "manim",
                    "-ql",
                    scene_file,
                    "Scene",
                    "--media_dir",
                    media_dir,
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            print(f"[{job_id}] Manim stdout: {result.stdout[-300:]}")
            print(f"[{job_id}] Manim stderr: {result.stderr[-300:]}")

            if result.returncode == 0:
                break

            last_error = result.stderr
            print(f"[{job_id}] Render attempt {attempt} failed")

            if attempt < MAX_RETRIES:
                if "SyntaxError" in last_error or "IndentationError" in last_error:
                    print(f"[{job_id}] Syntax error detected — regenerating simpler version...")
                    code = generate_manim_code(data.prompt, data.context, simple=True)
                    valid, syntax_err = is_syntax_valid(code)
                    if not valid:
                        print(f"[{job_id}] Regenerated code also has syntax error: {syntax_err}")
                else:
                    print(f"[{job_id}] Attempting LLM fix for attempt {attempt}...")
                    code = fix_code_with_llm(code, last_error[-600:], data.prompt)
                    print(f"[{job_id}] Code fixed, retrying...")

                with open(scene_file, "w", encoding="utf-8") as f:
                    f.write(code)

        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Render timed out")

    else:
        print(f"[{job_id}] RENDER FAILED after {MAX_RETRIES} attempts")
        raise HTTPException(500, f"Render failed after {MAX_RETRIES} attempts: {last_error[-300:]}")

    # Step 4: Find output
    expected = os.path.join(media_dir, "videos", f"scene_{job_id}", "480p15", "Scene.mp4")
    print(f"[{job_id}] Looking for video at: {expected}")
    if not os.path.exists(expected):
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                print(f"[{job_id}] Found file: {os.path.join(root, file)}")
        raise HTTPException(500, "Video file not found after render")

    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.rename(expected, output_video)

    return {"video_url": f"/videos/{job_id}.mp4"}


OPPORTUNITIES_DATA = [
    {
        "title": "Chevening Scholarships",
        "desc": "UK government global scholarship programme offering full financial support for one-year master's degrees at any UK university.",
        "link": "https://www.chevening.org/scholarships/",
        "source": "UK Foreign & Commonwealth Office",
        "type": "Scholarship",
        "region": "🇬🇧 UK",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Fulbright Foreign Student Program",
        "desc": "Fully funded graduate study, master's and PhD programs at leading universities across the United States.",
        "link": "https://foreign.fulbrightonline.org/",
        "source": "US Department of State",
        "type": "Scholarship",
        "region": "🇺🇸 USA",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "DAAD Research Grants - Doctoral Programmes",
        "desc": "Doctoral candidates and young academics can conduct research or complete PhDs at state-recognized universities in Germany.",
        "link": "https://www.daad.de/en/",
        "source": "German Academic Exchange (DAAD)",
        "type": "Research",
        "region": "🇪🇺 EU",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Gates Cambridge Scholarship",
        "desc": "Full-cost awards for outstanding applicants from countries outside the UK to pursue a full-time postgraduate degree at Cambridge.",
        "link": "https://www.gatescambridge.org/",
        "source": "University of Cambridge",
        "type": "Fellowship",
        "region": "🇬🇧 UK",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Erasmus Mundus Joint Master Degrees (EMJM)",
        "desc": "High-level integrated international study programmes with full EU-funded scholarships covering tuition, travel, and monthly allowance.",
        "link": "https://erasmus-plus.ec.europa.eu/opportunities/individuals/students/erasmus-mundus-joint-masters",
        "source": "European Commission",
        "type": "Scholarship",
        "region": "🇪🇺 EU",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "JSPS Postdoctoral Fellowships for Research in Japan",
        "desc": "Fellowships providing opportunities for overseas researchers to conduct cooperative research with host researchers in Japan.",
        "link": "https://www.jsps.go.jp/english/e-fellow/",
        "source": "Japan Society for the Promotion of Science",
        "type": "Research",
        "region": "🇯🇵 Japan",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Swiss Government Excellence Scholarships",
        "desc": "Postgraduate scholarships for foreign scholars and researchers at Swiss public universities and federal institutes of technology.",
        "link": "https://www.sbfi.admin.ch/sbfi/en/home/education/scholarships-and-grants/swiss-government-excellence-scholarships.html",
        "source": "Federal Commission for Scholarships (FCS)",
        "type": "Fellowship",
        "region": "🇪🇺 EU",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Australia Awards Scholarships",
        "desc": "Long-term development awards administered by the Department of Foreign Affairs and Trade for study in Australian universities.",
        "link": "https://www.dfat.gov.au/people-to-people/australia-awards",
        "source": "Australian Government DFAT",
        "type": "Scholarship",
        "region": "🇦🇺 Australia",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "MEXT Japanese Government Scholarships",
        "desc": "Full scholarships for undergraduate, research, and masters/doctoral studies at top Japanese universities funded by MEXT.",
        "link": "https://www.studyinjapan.go.jp/en/planning/scholarship/mext-scholarships/",
        "source": "Ministry of Education Japan (MEXT)",
        "type": "Scholarship",
        "region": "🇯🇵 Japan",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Rhodes Scholarship at Oxford",
        "desc": "The oldest graduate scholarship in the world, supporting exceptional students from across the globe to study at Oxford University.",
        "link": "https://www.rhodeshouse.ox.ac.uk/scholarships/the-rhodes-scholarship/",
        "source": "Rhodes Trust",
        "type": "Fellowship",
        "region": "🇬🇧 UK",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Commonwealth Scholarships",
        "desc": "Funded by the UK Foreign, Commonwealth & Development Office for master's and PhD studies to contribute to sustainable development.",
        "link": "https://cscuk.fcdo.gov.uk/scholarships/",
        "source": "Commonwealth Scholarship Commission",
        "type": "Scholarship",
        "region": "🇬🇧 UK",
        "date": "",
        "deadlineStatus": "unknown"
    },
    {
        "title": "Swedish Institute Scholarships for Global Professionals",
        "desc": "Fully funded scholarship for full-time master's studies in Sweden covering tuition, living expenses, insurance, and travel grant.",
        "link": "https://si.se/en/apply/scholarships/swedish-institute-scholarships-for-global-professionals/",
        "source": "Swedish Institute (SI)",
        "type": "Scholarship",
        "region": "🇪🇺 EU",
        "date": "",
        "deadlineStatus": "unknown"
    }
]


logger = logging.getLogger(__name__)
OPPORTUNITIES_CACHE_SECONDS = 8 * 60 * 60
OPPORTUNITIES_REQUEST_TIMEOUT = 12
OPPORTUNITIES_MAX_RESPONSE_BYTES = 12_000_000
_opportunities_cache = None
_opportunities_cache_time = 0.0
_opportunities_cache_lock = asyncio.Lock()


def _read_opportunity_feed(url: str):
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Amplify opportunity feed (public job listings)",
        },
    )
    with urlopen(request, timeout=OPPORTUNITIES_REQUEST_TIMEOUT) as response:
        body = response.read(OPPORTUNITIES_MAX_RESPONSE_BYTES + 1)
    if len(body) > OPPORTUNITIES_MAX_RESPONSE_BYTES:
        raise ValueError("provider response exceeded size limit")
    return json.loads(body)


def _clean_opportunity_text(value, max_length: int = 500) -> str:
    if not isinstance(value, str):
        return ""
    value = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", value)
    value = html.unescape(re.sub(r"<[^>]*>", " ", value))
    value = re.sub(r"\s+", " ", value).strip()
    return value[:max_length].rstrip()


def _safe_opportunity_url(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if any(character.isspace() or ord(character) < 32 for character in value):
        return None
    parsed = urlparse(value)
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.netloc
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        return None
    return value


def _is_expired_opportunity(value) -> bool:
    if isinstance(value, (int, float)):
        timestamp = value / 1000 if value > 1_000_000_000_000 else value
        deadline = datetime.fromtimestamp(timestamp, timezone.utc)
    elif isinstance(value, str) and value.strip():
        try:
            timestamp = float(value)
            timestamp = timestamp / 1000 if timestamp > 1_000_000_000_000 else timestamp
            deadline = datetime.fromtimestamp(timestamp, timezone.utc)
        except ValueError:
            deadline = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
    else:
        return False
    return deadline <= datetime.now(timezone.utc)


def _make_job(title, description, link, region, company, expiry=None):
    title = _clean_opportunity_text(title, 180)
    description = _clean_opportunity_text(description)
    source_url = _safe_opportunity_url(link)
    region = _clean_opportunity_text(region, 120) or "Not listed"
    company = _clean_opportunity_text(company, 120)
    if not title or not description or not source_url:
        return None
    if expiry is not None:
        try:
            if _is_expired_opportunity(expiry):
                return None
        except (OverflowError, OSError, TypeError, ValueError):
            logger.warning("Ignoring invalid opportunity expiry value")
    if company:
        description = _clean_opportunity_text(f"{company} — {description}")
    return {
        "title": title,
        "desc": description,
        "link": source_url,
        "source": "",
        "type": "Job",
        "region": region,
        "date": "",
        "deadlineStatus": "unknown",
    }


def _himalayas_jobs(payload):
    records = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError("Himalayas response is missing its jobs list")
    items = []
    for record in records:
        if not isinstance(record, dict):
            continue
        restrictions = record.get("locationRestrictions")
        region = ", ".join(
            _clean_opportunity_text(item, 80)
            for item in restrictions[:3]
            if isinstance(item, str) and item.strip()
        ) if isinstance(restrictions, list) else ""
        item = _make_job(
            record.get("title"),
            record.get("excerpt") or record.get("description"),
            record.get("applicationLink"),
            region,
            record.get("companyName"),
            record.get("expiryDate"),
        )
        if item:
            item["source"] = "Himalayas"
            items.append(item)
    return items


def _arbeitnow_jobs(payload):
    records = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError("Arbeitnow response is missing its data list")
    items = []
    for record in records:
        if not isinstance(record, dict):
            continue
        location = record.get("location") if isinstance(record.get("location"), str) else ""
        region = f"Remote — {location}" if record.get("remote") and location else location
        item = _make_job(
            record.get("title"),
            record.get("description"),
            record.get("url"),
            region,
            record.get("company_name"),
        )
        if item:
            item["source"] = "Arbeitnow"
            items.append(item)
    return items


async def _load_opportunity_source(source: str, url: str, parser):
    try:
        payload = await asyncio.to_thread(_read_opportunity_feed, url)
        items = parser(payload)
        return items[:30]
    except Exception as error:
        logger.warning("Opportunity provider %s failed: %s", source, error)
        return []


def _deduplicate_opportunities(items):
    seen = set()
    unique = []
    for item in items:
        parsed = urlparse(item["link"])
        url_key = (parsed.netloc.lower(), parsed.path.rstrip("/").lower())
        text_key = (
            item["title"].casefold(),
            item["desc"][:160].casefold(),
        )
        if url_key in seen or text_key in seen:
            continue
        seen.add(url_key)
        seen.add(text_key)
        unique.append(item)
    return unique


@app.get("/api/opportunities")
async def get_opportunities():
    global _opportunities_cache, _opportunities_cache_time
    if (
        _opportunities_cache is not None
        and time.monotonic() - _opportunities_cache_time < OPPORTUNITIES_CACHE_SECONDS
    ):
        return _opportunities_cache

    async with _opportunities_cache_lock:
        if (
            _opportunities_cache is not None
            and time.monotonic() - _opportunities_cache_time < OPPORTUNITIES_CACHE_SECONDS
        ):
            return _opportunities_cache

        feeds = [
            (
                "Himalayas",
                "https://himalayas.app/jobs/api?limit=40",
                _himalayas_jobs,
            ),
            (
                "Arbeitnow",
                "https://www.arbeitnow.com/api/job-board-api?page=1",
                _arbeitnow_jobs,
            ),
        ]
        results = await asyncio.gather(
            *(
                _load_opportunity_source(source, url, parser)
                for source, url, parser in feeds
            )
        )
        items = _deduplicate_opportunities(
            [item for source_items in results for item in source_items]
        )
        is_fallback = not items
        if is_fallback:
            logger.warning("All live opportunity providers failed; using local fallback data")
            items = OPPORTUNITIES_DATA

        _opportunities_cache = {
            "status": "fallback" if is_fallback else "live",
            "count": len(items),
            "items": items,
        }
        _opportunities_cache_time = time.monotonic()
        return _opportunities_cache


def clean_html_tags(raw: str | None) -> str:
    if not raw:
        return ""
    import html
    text = re.sub(r"<[^>]+>", "", str(raw))
    return html.unescape(text).strip()


@app.get("/research/gifs")
async def get_research_gifs(q: str = ""):
    """Fetch topic-based educational animations from official Wikimedia Commons MediaWiki API."""
    import httpx
    raw_query = q or ""
    # 1. Validate that search query is provided
    normalized = re.sub(r"\s+", " ", raw_query).strip()
    if not normalized:
        return {"query": "", "results": []}

    # 2. Limit query length to 200 characters
    query = normalized[:200]

    # Search candidates: primary query with animation, fallback to without animation if needed
    candidate_searches = [
        f"filemime:image/gif {query} animation",
        f"filemime:image/gif {query}",
    ]

    results = []
    seen_urls = set()
    user_agent = "Amplify/1.0 (educational GIF references; https://amplifywebsite.edu)"

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for gsrsearch in candidate_searches:
            if len(results) >= 5:
                break
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": gsrsearch,
                "gsrnamespace": "6",
                "gsrlimit": "10",
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": "640",
                "format": "json",
            }
            try:
                resp = await client.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params=params,
                    headers={"User-Agent": user_agent},
                )
                if resp.status_code != 200:
                    continue
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for pid, page in pages.items():
                    title = page.get("title", "")
                    # 7. Only accept files whose titles end in .gif
                    if not title.lower().endswith(".gif"):
                        continue

                    clean_title = title[5:] if title.startswith("File:") else title

                    imageinfo = page.get("imageinfo", [])
                    if not imageinfo:
                        continue
                    info = imageinfo[0]

                    # 6. Extract thumburl or url, and descriptionurl
                    img_url = info.get("thumburl") or info.get("url") or ""
                    file_url = info.get("descriptionurl") or ""

                    # 8. Only accept image URLs from upload.wikimedia.org or thumb.wikimedia.org
                    if not (img_url.startswith("https://upload.wikimedia.org/") or img_url.startswith("https://thumb.wikimedia.org/")):
                        continue

                    # 9. Only accept source links from https://commons.wikimedia.org/
                    if not file_url.startswith("https://commons.wikimedia.org/"):
                        continue

                    if img_url in seen_urls:
                        continue
                    seen_urls.add(img_url)

                    # Extract artist and license from extmetadata
                    meta = info.get("extmetadata", {})
                    artist = clean_html_tags(meta.get("Artist", {}).get("value")) or "Wikimedia Commons contributor"
                    license_name = clean_html_tags(meta.get("LicenseShortName", {}).get("value") or meta.get("License", {}).get("value")) or "Wikimedia Commons"

                    results.append({
                        "title": clean_title,
                        "image_url": img_url,
                        "file_url": file_url,
                        "artist": artist,
                        "license": license_name,
                    })

                    # 10. Return a maximum of five valid GIF results
                    if len(results) >= 5:
                        break
            except Exception:
                # Handle failed API requests gracefully without leaking internal errors
                continue

    return {
        "query": query,
        "results": results[:5]
    }


@app.get("/research/papers")
async def get_research_papers(q: str = ""):
    """Fetch topic-based research papers from the arXiv Atom API."""
    import httpx
    import xml.etree.ElementTree as ET

    query = re.sub(r"\s+", " ", q or "").strip()[:200]
    if len(query) < 3:
        return {"query": query, "results": []}

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(
                "https://export.arxiv.org/api/query",
                params={
                    "search_query": f"all:{query}",
                    "max_results": 5,
                    "sortBy": "relevance",
                },
                headers={"User-Agent": "Amplify/1.0 (educational research references)"},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="The arXiv research service is unavailable.") from exc

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise HTTPException(status_code=502, detail="The arXiv research service returned invalid data.") from exc

    atom = "{http://www.w3.org/2005/Atom}"
    results = []
    for entry in root.findall(f"{atom}entry"):
        title = re.sub(r"\s+", " ", entry.findtext(f"{atom}title", default="")).strip()
        if not title:
            continue
        results.append({
            "title": title,
            "abstract": re.sub(r"\s+", " ", entry.findtext(f"{atom}summary", default="")).strip(),
            "link": entry.findtext(f"{atom}id", default="").strip(),
        })

    return {"query": query, "results": results}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "frontend_dir": FRONTEND_DIR,
        "frontend_exists": bool(FRONTEND_DIR and os.path.isdir(FRONTEND_DIR)),
        "base_dir": BASE_DIR,
        "project_root": PROJECT_ROOT,
    }


@app.get("/api/config")
async def get_config():
    """Provide API configuration to frontend"""
    groq_keys = parse_env_list('GROQ_KEYS')
    if not groq_keys:
        for env_name in ('GROQ_API_KEY', 'GROQ_KEY'):
            single = os.getenv(env_name, '').strip()
            if single:
                groq_keys = [single]
                break

    openrouter_keys = parse_env_list('OPENROUTER_API_KEYS')
    print(f"[/api/config] GROQ_KEYS count: {len(groq_keys)}, OPENROUTER_KEYS count: {len(openrouter_keys)}")

    return {
        "GROQ_API_KEY": groq_keys[0] if groq_keys else '',
        "GROQ_KEYS": groq_keys,
        "GROQ_API_BASE_URL": os.getenv('GROQ_BASE', 'https://api.groq.com/openai/v1'),
        "CEREBRAS_API_KEY": os.getenv('CEREBRAS_KEY', ''),
        "CEREBRAS_API_BASE": os.getenv('CEREBRAS_BASE', 'https://api.cerebras.ai/v1'),
        "OPENROUTER_API_KEYS": openrouter_keys,
        "OPENROUTER_KEYS": openrouter_keys,
        "OPENROUTER_BASE": OPENROUTER_BASE_URL,
        "GEMINI_KEY": os.getenv('GEMINI_KEY', ''),
        "GEMINI_MODEL": os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-lite'),
        "GEMINI_BASE": os.getenv('GEMINI_BASE', 'https://generativelanguage.googleapis.com/v1beta/models'),
        "AZURE_SPEECH_KEY": os.getenv('AZURE_SPEECH_KEY', ''),
        "AZURE_SPEECH_REGION": os.getenv('AZURE_SPEECH_REGION', 'southeastasia'),
    }



# ── NEO4J PROXY ──────────────────────────────────────
from neo4j import AsyncGraphDatabase

_neo4j_driver = None

def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        uri  = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER", "neo4j")
        pwd  = os.getenv("NEO4J_PASS")
        if not uri or not pwd:
            raise HTTPException(500, "NEO4J_URI / NEO4J_PASS not set")
        _neo4j_driver = AsyncGraphDatabase.driver(uri, auth=(user, pwd))
    return _neo4j_driver

class Neo4jRequest(BaseModel):
    statement: str
    parameters: dict = {}

@app.post("/neo4j")
async def neo4j_proxy(req: Neo4jRequest):
    driver = get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(req.statement, req.parameters)
        records = await result.data()
        return {"results": [{"data": [{"row": list(r.values())} for r in records]}]}



@app.get("/neo4j/keepalive")
async def neo4j_keepalive():
    try:
        driver = get_neo4j_driver()
        async with driver.session() as session:
            await session.run("RETURN 1")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}



# ── Fallback Authentication & Profile Routes ───────────────────
class AuthRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    password_confirmation: str = ""
    role: str = "student"

class AuthLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/register")
async def api_register(data: AuthRegisterRequest):
    token = f"token_{uuid.uuid4().hex}"
    user = {
        "id": 1,
        "name": data.name,
        "email": data.email,
        "role": "student",
    }
    return {
        "message": "Registration successful.",
        "user": user,
        "token": token,
    }

@app.post("/api/login")
async def api_login(data: AuthLoginRequest):
    name = data.email.split("@")[0].capitalize() or "Student"
    user = {
        "id": 1,
        "name": name,
        "email": data.email,
        "role": "teacher" if "teacher" in data.email.lower() else "student",
    }
    token = f"token_{uuid.uuid4().hex}"
    return {
        "message": "Login successful.",
        "user": user,
        "token": token,
    }

@app.get("/api/user")
async def api_get_user():
    return {
        "user": {
            "id": 1,
            "name": "Student",
            "email": "student@amplify.app",
            "role": "student"
        }
    }

@app.post("/api/logout")
async def api_logout():
    return {"message": "Logged out successfully."}


if FRONTEND_DIR:

    @app.middleware("http")
    async def clean_urls_middleware(request, call_next):
        path = request.url.path
        if not path.startswith(("/api", "/neo4j", "/generate", "/videos", "/turn", "/models", "/static")):
            if FRONTEND_DIR and not os.path.splitext(path)[1]:
                clean_rel = path.strip("/")
                html_file = os.path.join(FRONTEND_DIR, f"{clean_rel}.html")
                if os.path.isfile(html_file):
                    return FileResponse(html_file, media_type="text/html")
                teacher_html = os.path.join(FRONTEND_DIR, "teacher", f"{clean_rel.replace('teacher/', '')}.html")
                if os.path.isfile(teacher_html):
                    return FileResponse(teacher_html, media_type="text/html")
        return await call_next(request)
    public_dir = os.path.join(FRONTEND_DIR, "public")
    models_dir = os.path.join(public_dir, "models")

    if os.path.isdir(models_dir):
        app.mount("/models", StaticFiles(directory=models_dir), name="models")

    @app.get("/amplify-env-bootstrap.js")
    async def amplify_env_bootstrap():
        path = os.path.join(public_dir, "amplify-env-bootstrap.js")
        if not os.path.isfile(path):
            raise HTTPException(404, "amplify-env-bootstrap.js not found")
        return FileResponse(path, media_type="application/javascript")

    @app.get("/icons.svg")
    async def icons_svg():
        path = os.path.join(public_dir, "icons.svg")
        if not os.path.isfile(path):
            raise HTTPException(404, "icons.svg not found")
        return FileResponse(path, media_type="image/svg+xml")

    @app.get("/favicon.svg")
    async def favicon_svg():
        path = os.path.join(public_dir, "favicon.svg")
        if not os.path.isfile(path):
            raise HTTPException(404, "favicon.svg not found")
        return FileResponse(path, media_type="image/svg+xml")

    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
else:
    print("Static HTML frontend will not be served.")
