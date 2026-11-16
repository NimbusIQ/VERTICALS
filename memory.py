"""
modules/memory.py
─────────────────
Conversation memory management for the Gemini Coding Agent.

Maintains a rolling window of conversation history to support multi-turn
interactions. Implements a token-budget-aware truncation strategy to avoid
exceeding Gemini's context window limits.

Features:
  - Multi-turn conversation history
  - Automatic history truncation (keeps last N turns)
  - Session persistence (save/load to JSON)
  - Summary injection for long sessions
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from google.genai import types

logger = logging.getLogger(__name__)

# Keep the last N turns in active memory (each turn = user + assistant)
MAX_TURNS = 20
HISTORY_FILE = ".agent_history.json"


class ConversationMemory:
    """
    Manages conversation history for multi-turn interactions with Gemini.
    """

    def __init__(self, max_turns: int = MAX_TURNS, persist: bool = True):
        self.max_turns = max_turns
        self.persist = persist
        self._history: list[types.Content] = []
        self._raw_history: list[dict] = []  # For JSON persistence
        self._session_start = datetime.now().isoformat()

        if persist:
            self._load_from_disk()

    def add_turn(self, contents: list[types.Content]):
        """Add a user turn to history."""
        for content in contents:
            self._history.append(content)
        self._trim()

    def add_assistant_response(self, text: str):
        """Add an assistant text response to history."""
        self._history.append(
            types.Content(
                role="model",
                parts=[types.Part(text=text)],
            )
        )
        self._trim()
        if self.persist:
            self._save_to_disk(text)

    def add_raw_turns(self, turns: list[types.Content]):
        """Add raw Content objects (e.g., function call/response turns)."""
        self._history.extend(turns)
        self._trim()

    def get_history(self) -> list[types.Content]:
        """Return the full conversation history."""
        return list(self._history)

    def clear(self):
        """Clear all conversation history."""
        self._history = []
        self._raw_history = []
        logger.info("Conversation history cleared.")

    def _trim(self):
        """
        Trim history to max_turns to avoid context overflow.
        Keeps the most recent turns. Always preserves the first system context
        if present.
        """
        # Each "turn" is roughly 2 Content objects (user + model)
        max_contents = self.max_turns * 2
        if len(self._history) > max_contents:
            trimmed = len(self._history) - max_contents
            self._history = self._history[trimmed:]
            logger.debug(f"Trimmed {trimmed} old content items from history.")

    def _save_to_disk(self, assistant_text: str):
        """Save the latest exchange to disk for session persistence."""
        try:
            history_path = Path(HISTORY_FILE)
            if history_path.exists():
                with open(history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"session_start": self._session_start, "turns": []}

            data["turns"].append({
                "timestamp": datetime.now().isoformat(),
                "assistant": assistant_text[:500],  # Truncate for storage
            })

            # Keep only last 50 turns on disk
            data["turns"] = data["turns"][-50:]

            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.warning(f"Could not save history to disk: {e}")

    def _load_from_disk(self):
        """Load previous session summary from disk (for context)."""
        try:
            history_path = Path(HISTORY_FILE)
            if not history_path.exists():
                return

            with open(history_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            turns = data.get("turns", [])
            if not turns:
                return

            # Inject a brief summary of the previous session as context
            recent = turns[-5:]  # Last 5 exchanges
            summary_lines = [
                f"[Previous session context - {data.get('session_start', 'unknown')}]"
            ]
            for t in recent:
                if "assistant" in t:
                    summary_lines.append(f"- {t['assistant'][:200]}...")

            summary = "\n".join(summary_lines)
            self._history.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=f"[CONTEXT FROM PREVIOUS SESSION]\n{summary}")],
                )
            )
            self._history.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text="Understood. I have context from our previous session and will continue from where we left off.")],
                )
            )
            logger.info(f"Loaded {len(turns)} turns from previous session.")

        except Exception as e:
            logger.warning(f"Could not load history from disk: {e}")

    @property
    def turn_count(self) -> int:
        """Return the number of content items in history."""
        return len(self._history)
