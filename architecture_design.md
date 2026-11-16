# Gemini Multi-Modal Coding Agent: Architecture & Design

## Overview
This project provides a comprehensive, production-grade coding agent powered by the Google Gemini API (specifically `gemini-2.5-pro` or `gemini-2.5-flash`). It is designed to accept multi-modal inputs (text, voice, and images) and output complete, runnable software projects.

## Components

1. **System Prompt (AI Studio)**
   - A highly optimized prompt that defines the agent's persona, workflow, and output format.
   - Can be pasted directly into Google AI Studio for a no-code agent experience.

2. **Python CLI Agent**
   - A command-line interface application that interacts with the Gemini API.
   - Handles multi-modal inputs:
     - **Text**: Standard terminal input.
     - **Image**: Reads local image files (UI mockups, diagrams) and encodes them for Gemini.
     - **Voice**: Uses local microphone input (via `speech_recognition` or similar) or reads audio files, passing them to Gemini's native audio capabilities.
   - **Function Calling (Tools)**: Implements local tools that the Gemini model can call to actually create directories and write files to the user's disk, transforming it from a chatbot into an autonomous builder.

3. **File Writer & Scaffolder**
   - A module containing the tools exposed to Gemini.
   - `create_directory(path)`: Creates a folder.
   - `write_file(path, content)`: Writes code to a file.
   - `execute_command(command)`: (Optional/Sandboxed) Runs commands like `npm install` or `pip install`.

## Tech Stack
- **Language**: Python 3.10+
- **LLM SDK**: `google-genai` (The new official Google GenAI SDK)
- **Audio Processing**: `SpeechRecognition`, `pyaudio` (for local mic input) or direct audio file upload to Gemini.
- **Image Processing**: `Pillow` (PIL) for image handling before sending to Gemini.

## Workflow
1. User runs the CLI: `python agent.py`
2. Agent prompts for input mode: `[T]ext, [V]oice, [I]mage + Text`
3. User provides input.
4. Python script constructs the payload (system instructions + multi-modal user input) and sends it to the Gemini API.
5. Gemini processes the request and responds with a plan and a series of Function Calls (e.g., `write_file('app.py', '...')`).
6. The Python script executes the local functions, building the project on disk.
7. Agent returns a success message and instructions to run the app.
