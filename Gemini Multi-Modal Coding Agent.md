# Gemini Multi-Modal Coding Agent

A production-grade, multi-modal Software Engineering Agent powered by the Google Gemini API (`gemini-2.5-pro` and `gemini-2.5-flash`).

This agent goes beyond standard chatbots by integrating **Function Calling (Tools)** to autonomously create directories, write files, and scaffold full projects directly on your local machine. It accepts **Text, Voice, and Image** inputs.

## Features

- **Multi-Modal Input**: 
  - 🎤 **Voice**: Record directly from your microphone or provide an audio file.
  - 🖼️ **Image**: Attach UI mockups, architecture diagrams, or screenshots.
  - ⌨️ **Text**: Standard terminal chat interface.
- **Autonomous Execution**: Uses Gemini's Function Calling to execute local Python functions that write code to your disk.
- **Project Scaffolding**: Built-in templates for React, Next.js, FastAPI, Node.js/Express, and more.
- **Conversation Memory**: Maintains context across multiple turns, truncating older history to fit context windows.
- **Security-First**: Blocks dangerous shell commands and enforces safe file writing paths.

---

## 1. Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation
Clone or copy this directory, then install the dependencies:

```bash
cd gemini_coding_agent
pip install -r requirements.txt
```

*(Optional)* For microphone voice input support, you need `pyaudio` and `SpeechRecognition`:
```bash
# macOS
brew install portaudio
pip install pyaudio SpeechRecognition

# Ubuntu/Debian
sudo apt-get install portaudio19-dev
pip install pyaudio SpeechRecognition
```

### Environment Variable
Set your API key:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

---

## 2. Usage (Python CLI)

### Interactive Mode (REPL)
Start the agent in interactive mode:
```bash
python agent.py
```
Inside the interactive prompt, you can use commands:
- `/image <path>`: Attach an image to your next prompt.
- `/voice mic`: Record from your microphone (requires `pyaudio`).
- `/voice <file.mp3>`: Transcribe an audio file.
- `/clear`: Clear conversation history.
- `/exit`: Quit.

### One-Shot Commands
You can run the agent for a single task directly from your terminal:

**Text only:**
```bash
python agent.py --text "Scaffold a FastAPI app named my_backend"
```

**With an Image (e.g., UI Mockup):**
```bash
python agent.py --text "Build this UI using React and TailwindCSS" --image "mockup.png"
```

**With an Audio File:**
```bash
python agent.py --voice "instructions.mp3"
```

**Specify Output Directory & Model:**
```bash
python agent.py --text "Create a Python CLI tool" --output-dir "./my_cli" --model "gemini-2.5-flash"
```

---

## 3. Google AI Studio Setup (No-Code Version)

If you prefer to use Google AI Studio directly instead of the Python script, you can set up the agent persona there.

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Create New Prompt** -> **System Instructions**.
3. Copy the contents of `system_prompt.txt` (or the block below) and paste it into the **System Instructions** box.
4. Set the Model to **Gemini 2.5 Pro**.
5. Set Temperature to **0.2** (for deterministic code).
6. Under **Tools**, if you are using the API, you can define function declarations. In the web UI, the agent will output markdown code blocks.

### AI Studio System Prompt
```text
You are an elite, multi-modal Software Engineering Agent powered by Google Gemini.
You can build anything from simple scripts to production-ready, enterprise-scalable applications.

## Your Capabilities
- Accept text, voice transcriptions, and image-based inputs (UI mockups, architecture diagrams, screenshots).
- Generate complete, runnable software projects with full file structures.
- Support all major tech stacks: React, Next.js, Vue, FastAPI, Django, Node.js/Express, Flutter, Go, Rust.
- Generate Docker, CI/CD, Terraform, and cloud deployment configurations.

## Workflow
1. ANALYZE: Understand the full request. If an image is provided, extract UI layout, components, and structure. If voice, extract the core technical intent.
2. PLAN: Output a brief architecture plan (tech stack, file structure, key components) before writing any code.
3. BUILD: Output the complete code for all necessary files in clearly marked markdown blocks with file paths as headers (e.g., `### src/main.py`).
4. REVIEW: Provide the exact commands to install dependencies and run the application.

## Code Quality Standards
- Always include error handling and logging.
- Never hardcode secrets — use environment variables and `.env` files (with `.env.example`).
- Include a `README.md` with setup and run instructions.
- Write clean, modular, well-commented code.
- For web apps: responsive design, accessibility (ARIA), and cross-browser compatibility.

## Security-First Principle
Prioritize security in every decision. Sanitize all inputs. Use secure defaults.
Follow OWASP guidelines. Make the application as resilient as possible.
```

---

## 4. Architecture

- `agent.py`: The main entry point. Manages the Gemini client, argument parsing, and the core agentic loop.
- `modules/file_writer.py`: Contains the local Python functions exposed to Gemini via Function Calling (`create_directory`, `write_file`, `execute_command`).
- `modules/scaffolder.py`: Pre-built project templates (React, FastAPI, Node) that Gemini can trigger to save tokens and time.
- `modules/image_input.py`: Handles loading, resizing, and encoding images for the Gemini API.
- `modules/voice_input.py`: Handles microphone recording and audio file transcription using Gemini's native audio capabilities.
- `modules/memory.py`: Manages the rolling conversation history to prevent context window overflow.
