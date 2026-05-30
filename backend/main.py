from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, json, os, uuid, re, ast
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


app = FastAPI()
application = app
handler = app

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True)

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
- বাক্য যেন মাঝপথে না কাটে।""",

  'expert2': """তুমি ড. নাফিসা, বিশ্লেষক।
নিয়ম:
- সরাসরি বিশ্লেষণ দিয়ে শুরু করো। কোনো পরিচয় দিও না।
- "আমি ড. নাফিসা", "আমি বলব", "আমি মনে করি যে" — এই ধরনের বাক্য সম্পূর্ণ নিষিদ্ধ।
- প্রথম বাক্যেই মূল বক্তব্য শুরু হবে।
- মোট ২-৩টি সম্পূর্ণ বাক্য লিখবে। প্রতিটি বাক্য দাঁড়ি (।) দিয়ে শেষ করবে।
- বাক্য যেন মাঝপথে না কাটে।""",

  'expert3': """তুমি ড. রাকিব, সমালোচক।
নিয়ম:
- সরাসরি প্রশ্ন বা চ্যালেঞ্জ দিয়ে শুরু করো। কোনো পরিচয় দিও না।
- "আমি ড. রাকিব", "আমি বলব", "আমি মনে করি যে" — এই ধরনের বাক্য সম্পূর্ণ নিষিদ্ধ।
- প্রথম বাক্যেই মূল বক্তব্য শুরু হবে।
- মোট ২-৩টি সম্পূর্ণ বাক্য লিখবে। প্রতিটি বাক্য দাঁড়ি (।) দিয়ে শেষ করবে।
- বাক্য যেন মাঝপথে না কাটে।""",
}

EXPERT_NAMES = {
  'expert1': 'ড. আরিফ',
  'expert2': 'ড. নাফিসা',
  'expert3': 'ড. রাকিব',
}

EXPERT_MODELS = {
  'expert1': 'llama-3.3-70b-versatile',
  'expert2': 'gemma2-9b-it',
  'expert3': 'llama3-70b-8192',
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
        f"এখন সরাসরি বিষয়বস্তু দিয়ে শুরু করো। ২-৩টি সম্পূর্ণ বাক্য লিখবে, শেষ বাক্যটি অবশ্যই দাঁড়ি (।) দিয়ে শেষ করবে। কোনো পরিচয় বাক্য লিখবে না।"
    )

# ── Nodes ─────────────────────────────────────
def make_expert_node(expert_id: str):
    def node(state: DiscussionState) -> dict:
        primary_model = EXPERT_MODELS[expert_id]
        fallback_models = ['gemma2-9b-it', 'llama3-70b-8192', 'llama-3.1-8b-instant']
        models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]
        prompt_text = build_expert_prompt(state)
        messages = [
            SystemMessage(content=EXPERT_SYSTEMS[expert_id]),
            HumanMessage(content=prompt_text),
        ]
        last_err = None
        for model in models_to_try:
            for key in get_groq_keys():
                try:
                    llm = ChatGroq(api_key=key, model=model, max_tokens=400, temperature=0.8)
                    
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
                ["manim", "-ql", scene_file, "Scene", "--media_dir", media_dir],
                capture_output=True, text=True, timeout=120
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
        single = os.getenv('GROQ_KEY', '').strip()
        if single:
            groq_keys = [single]

    openrouter_keys = parse_env_list('OPENROUTER_API_KEYS')

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
    }


if FRONTEND_DIR:
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