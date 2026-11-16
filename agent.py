#!/usr/bin/env python3
"""
=============================================================================
  Gemini Multi-Modal Coding Agent
  Author: Manus AI
  Version: 1.0.0
  Description:
    A production-grade, multi-modal coding agent powered by Google Gemini.
    Accepts text, voice (audio file or microphone), and image inputs to
    generate complete, runnable software projects on disk via function calling.
=============================================================================
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# ── Third-party imports ───────────────────────────────────────────────────────
from google import genai
from google.genai import types

# ── Local module imports ──────────────────────────────────────────────────────
from modules.voice_input import transcribe_audio_file, record_from_microphone
from modules.image_input import load_image_part
from modules.file_writer import (
    create_directory,
    write_file,
    read_file,
    list_directory,
    execute_command,
)
from modules.scaffolder import scaffold_project
from modules.memory import ConversationMemory

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "gemini-2.5-pro"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.txt"

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an elite, multi-modal Software Engineering Agent powered by Google Gemini.
You can build anything from simple scripts to production-ready, enterprise-scalable applications.

## Your Capabilities
- Accept text, voice transcriptions, and image-based inputs (UI mockups, architecture diagrams, screenshots).
- Generate complete, runnable software projects with full file structures.
- Use your tools to create directories and write files directly to the user's disk.
- Support all major tech stacks: React, Next.js, Vue, FastAPI, Django, Node.js/Express, Flutter, Go, Rust, and more.
- Generate Docker, CI/CD, Terraform, and cloud deployment configurations.

## Workflow
1. ANALYZE: Understand the full request. If an image is provided, extract UI layout, components, and structure. If voice, extract the core technical intent.
2. PLAN: Output a brief architecture plan (tech stack, file structure, key components) before writing any code.
3. BUILD: Use your tools (`create_directory`, `write_file`) to build the project on disk, file by file.
4. REVIEW: After writing all files, summarize what was built and provide the exact commands to install dependencies and run the application.

## Code Quality Standards
- Always include error handling and logging.
- Never hardcode secrets — use environment variables and `.env` files (with `.env.example`).
- Include a `README.md` with setup and run instructions.
- Write clean, modular, well-commented code.
- For web apps: responsive design, accessibility (ARIA), and cross-browser compatibility.
- For APIs: input validation, rate limiting, and proper HTTP status codes.
- For databases: use parameterized queries, never raw string interpolation.

## Security-First Principle
Prioritize security in every decision. Sanitize all inputs. Use secure defaults.
Follow OWASP guidelines. Make the application as resilient as possible.

## Output Format
- When calling tools, do so one at a time in logical order (create directory before writing files in it).
- After all tool calls, provide a final summary with run instructions.
- If the user asks for a simple snippet (not a full project), just provide the code in a markdown block.
"""


# ── Tool Definitions (Function Declarations for Gemini) ───────────────────────
TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="create_directory",
                description="Creates a directory (and any necessary parent directories) on the user's local filesystem.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(
                            type=types.Type.STRING,
                            description="The relative or absolute path of the directory to create. E.g., 'my_app/src/components'",
                        )
                    },
                    required=["path"],
                ),
            ),
            types.FunctionDeclaration(
                name="write_file",
                description="Writes content to a file on the user's local filesystem. Creates the file if it does not exist, and overwrites it if it does.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(
                            type=types.Type.STRING,
                            description="The relative or absolute path of the file to write. E.g., 'my_app/src/main.py'",
                        ),
                        "content": types.Schema(
                            type=types.Type.STRING,
                            description="The full content to write to the file.",
                        ),
                    },
                    required=["path", "content"],
                ),
            ),
            types.FunctionDeclaration(
                name="read_file",
                description="Reads and returns the content of an existing file on the user's local filesystem.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(
                            type=types.Type.STRING,
                            description="The path of the file to read.",
                        )
                    },
                    required=["path"],
                ),
            ),
            types.FunctionDeclaration(
                name="list_directory",
                description="Lists the files and subdirectories within a given directory path.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "path": types.Schema(
                            type=types.Type.STRING,
                            description="The path of the directory to list. Defaults to '.' (current directory).",
                        )
                    },
                    required=["path"],
                ),
            ),
            types.FunctionDeclaration(
                name="execute_command",
                description="Executes a shell command on the user's local machine. Use this for commands like 'npm install', 'pip install -r requirements.txt', 'git init', etc. ONLY use safe, non-destructive commands.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "command": types.Schema(
                            type=types.Type.STRING,
                            description="The shell command to execute. E.g., 'pip install -r requirements.txt'",
                        ),
                        "working_directory": types.Schema(
                            type=types.Type.STRING,
                            description="The directory in which to run the command. Defaults to the current directory.",
                        ),
                    },
                    required=["command"],
                ),
            ),
            types.FunctionDeclaration(
                name="scaffold_project",
                description="Scaffolds a standard project template. Use this as the first step for common project types to set up the base structure quickly.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "project_type": types.Schema(
                            type=types.Type.STRING,
                            description="The type of project to scaffold. Options: 'fastapi', 'react', 'nextjs', 'node-express', 'flutter', 'django', 'cli-python', 'fullstack-react-fastapi'",
                        ),
                        "project_name": types.Schema(
                            type=types.Type.STRING,
                            description="The name of the project (used as the root directory name).",
                        ),
                    },
                    required=["project_type", "project_name"],
                ),
            ),
        ]
    )
]

# ── Tool Dispatcher ───────────────────────────────────────────────────────────
TOOL_MAP = {
    "create_directory": create_directory,
    "write_file": write_file,
    "read_file": read_file,
    "list_directory": list_directory,
    "execute_command": execute_command,
    "scaffold_project": scaffold_project,
}


def dispatch_tool(function_call: types.FunctionCall) -> str:
    """Execute a tool call returned by Gemini and return the result as a string."""
    name = function_call.name
    args = dict(function_call.args) if function_call.args else {}

    if name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool: {name}"})

    logger.info(f"🔧 Calling tool: {name}({json.dumps(args, indent=2)})")

    try:
        result = TOOL_MAP[name](**args)
        logger.info(f"✅ Tool '{name}' succeeded.")
        return json.dumps({"result": result})
    except Exception as e:
        logger.error(f"❌ Tool '{name}' failed: {e}")
        return json.dumps({"error": str(e)})


# ── Agentic Loop ──────────────────────────────────────────────────────────────
def run_agent_loop(client: genai.Client, model: str, contents: list, memory: ConversationMemory) -> str:
    """
    Runs the core agentic loop:
    1. Send contents to Gemini.
    2. If Gemini returns function calls, execute them and send results back.
    3. Repeat until Gemini returns a final text response.
    """
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode=types.FunctionCallingConfigMode.AUTO
            )
        ),
        temperature=0.2,  # Low temperature for deterministic code generation
    )

    # Add current contents to memory
    memory.add_turn(contents)

    # Build full conversation history
    full_history = memory.get_history()

    response = client.models.generate_content(
        model=model,
        contents=full_history,
        config=config,
    )

    # Agentic loop: keep executing tools until we get a final text response
    while True:
        # Check for function calls
        function_calls = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_calls.append(part.function_call)

        if not function_calls:
            # No more function calls — extract the final text response
            final_text = ""
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_text += part.text
            memory.add_assistant_response(final_text)
            return final_text

        # Execute all function calls and collect results
        tool_results = []
        for fc in function_calls:
            result_str = dispatch_tool(fc)
            tool_results.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response=json.loads(result_str),
                    )
                )
            )

        # Append the model's function call response and our tool results to history
        model_turn = types.Content(
            role="model",
            parts=[types.Part(function_call=fc) for fc in function_calls],
        )
        tool_turn = types.Content(role="user", parts=tool_results)

        memory.add_raw_turns([model_turn, tool_turn])

        # Send tool results back to the model
        response = client.models.generate_content(
            model=model,
            contents=memory.get_history(),
            config=config,
        )


# ── Input Builders ────────────────────────────────────────────────────────────
def build_text_input(text: str) -> list:
    """Build a simple text content list."""
    return [types.Content(role="user", parts=[types.Part(text=text)])]


def build_image_input(text: str, image_path: str) -> list:
    """Build a multi-modal content list with text and an image."""
    image_part = load_image_part(image_path)
    return [
        types.Content(
            role="user",
            parts=[
                types.Part(text=text),
                image_part,
            ],
        )
    ]


def build_voice_input(audio_source: str, extra_text: str = "") -> list:
    """Build a content list from a voice input (file or microphone)."""
    if audio_source == "mic":
        print("🎤 Listening... Speak your request now.")
        transcript = record_from_microphone()
    else:
        print(f"🎧 Transcribing audio file: {audio_source}")
        transcript = transcribe_audio_file(audio_source)

    print(f"\n📝 Transcription: {transcript}\n")
    combined = f"{extra_text}\n\n[Voice Input Transcript]: {transcript}".strip()
    return [types.Content(role="user", parts=[types.Part(text=combined)])]


# ── CLI Interface ─────────────────────────────────────────────────────────────
def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║       Gemini Multi-Modal Coding Agent  v1.0.0               ║
║       Powered by Google Gemini 2.5 Pro                      ║
║       Modes: Text | Voice | Image | Multi-Modal             ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def interactive_mode(client: genai.Client, model: str, memory: ConversationMemory):
    """Run the agent in an interactive REPL loop."""
    print("\nType your request below. Commands:")
    print("  /image <path>   — Attach an image to your next message")
    print("  /voice <file>   — Use an audio file as input")
    print("  /voice mic      — Record from your microphone")
    print("  /clear          — Clear conversation history")
    print("  /exit           — Quit the agent\n")

    pending_image = None

    while True:
        try:
            user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "/exit":
            print("Goodbye!")
            break

        if user_input.lower() == "/clear":
            memory.clear()
            print("✅ Conversation history cleared.\n")
            continue

        if user_input.lower().startswith("/image "):
            pending_image = user_input[7:].strip()
            print(f"📎 Image attached: {pending_image}")
            print("Now type your text prompt and press Enter.")
            continue

        if user_input.lower().startswith("/voice "):
            audio_source = user_input[7:].strip()
            contents = build_voice_input(audio_source)
        elif pending_image:
            contents = build_image_input(user_input, pending_image)
            pending_image = None
        else:
            contents = build_text_input(user_input)

        print("\n🤖 Agent is thinking...\n")
        try:
            response = run_agent_loop(client, model, contents, memory)
            print(f"\n{'─'*60}")
            print(f"Agent >\n{response}")
            print(f"{'─'*60}\n")
        except Exception as e:
            logger.error(f"Agent loop error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}\n")


# ── Main Entry Point ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Gemini Multi-Modal Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python agent.py

  # One-shot text request
  python agent.py --text "Build a FastAPI REST API for a todo list with SQLite"

  # One-shot with image (UI mockup)
  python agent.py --text "Build this UI as a React app" --image mockup.png

  # One-shot with audio file
  python agent.py --voice request.mp3

  # Use a specific model
  python agent.py --model gemini-2.5-flash
        """,
    )
    parser.add_argument("--text", type=str, help="Text prompt for a one-shot request.")
    parser.add_argument("--image", type=str, help="Path to an image file (UI mockup, diagram).")
    parser.add_argument("--voice", type=str, help="Path to an audio file, or 'mic' for microphone input.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Gemini model to use. Default: {DEFAULT_MODEL}")
    parser.add_argument("--output-dir", type=str, default=".", help="Base directory for generated project files.")
    parser.add_argument("--no-execute", action="store_true", help="Disable the execute_command tool (safer mode).")

    args = parser.parse_args()

    # ── API Key Validation ────────────────────────────────────────────────────
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable is not set.")
        print("   Get your free key at: https://aistudio.google.com/app/apikey")
        print("   Then run: export GEMINI_API_KEY='your_key_here'")
        sys.exit(1)

    # ── Client Initialization ─────────────────────────────────────────────────
    client = genai.Client(api_key=api_key)
    memory = ConversationMemory()

    # Change to output directory if specified
    if args.output_dir and args.output_dir != ".":
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
        logger.info(f"Working directory set to: {os.path.abspath(args.output_dir)}")

    # Disable execute_command if requested
    if args.no_execute:
        TOOL_MAP.pop("execute_command", None)
        logger.info("execute_command tool disabled (--no-execute flag).")

    print_banner()
    print(f"🚀 Model: {args.model}")
    print(f"📁 Output directory: {os.path.abspath(args.output_dir)}\n")

    # ── One-Shot Mode ─────────────────────────────────────────────────────────
    if args.text or args.voice:
        if args.voice:
            contents = build_voice_input(args.voice, args.text or "")
        elif args.image:
            contents = build_image_input(args.text, args.image)
        else:
            contents = build_text_input(args.text)

        print("🤖 Agent is thinking...\n")
        try:
            response = run_agent_loop(client, args.model, contents, memory)
            print(f"\n{'─'*60}")
            print(f"Agent >\n{response}")
            print(f"{'─'*60}\n")
        except Exception as e:
            logger.error(f"Agent loop error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}\n")
            sys.exit(1)
    else:
        # ── Interactive Mode ──────────────────────────────────────────────────
        interactive_mode(client, args.model, memory)


if __name__ == "__main__":
    main()
