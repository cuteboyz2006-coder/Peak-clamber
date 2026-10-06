from pathlib import Path
import json

from llama_cpp import Llama


ROOT = Path(__file__).resolve().parent

MODEL_PATH = (
    ROOT
    / "models"
    / "SmolLM2-135M-Instruct-Q4_K_M.gguf"
)

MEMORY_PATH = ROOT / "layla_memory.json"

MAX_HISTORY = 20


SYSTEM_PROMPT = """
You are Layla, a helpful personal AI assistant.

Personality:
- Friendly
- Natural
- Helpful
- Clear
- Respectful

You can help with:
- General questions
- Study
- Mathematics
- Coding
- Programming
- Ideas
- Explanations
- Normal conversation

Use saved memory and recent conversation when useful.

Do not invent memories.
Only use information supplied in the memory or conversation.
"""


class LaylaMemory:

    def __init__(self, path=MEMORY_PATH):
        self.path = Path(path)
        self.data = self._load()

    def _default(self):
        return {
            "name": None,
            "likes": [],
            "facts": [],
            "history": []
        }

    def _load(self):
        if not self.path.exists():
            return self._default()

        try:
            with self.path.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            result = self._default()

            result["name"] = data.get("name")
            result["likes"] = data.get("likes", [])
            result["facts"] = data.get("facts", [])
            result["history"] = data.get("history", [])

            return result

        except Exception:
            return self._default()

    def save(self):
        try:
            with self.path.open(
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.data,
                    file,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception:
            pass

    def learn(self, text):
        original = text.strip()
        lower = original.lower()

        if lower.startswith("my name is "):
            name = original[len("my name is "):].strip()

            if name:
                self.data["name"] = name

        elif lower.startswith("mera naam "):
            name = original[len("mera naam "):].strip()

            if name:
                self.data["name"] = name

        elif lower.startswith("i like "):
            item = original[len("i like "):].strip()

            if item and item not in self.data["likes"]:
                self.data["likes"].append(item)

        elif lower.startswith("i love "):
            item = original[len("i love "):].strip()

            if item and item not in self.data["likes"]:
                self.data["likes"].append(item)

        elif "mujhe " in lower and " pasand hai" in lower:
            start = lower.find("mujhe ") + len("mujhe ")
            end = lower.find(" pasand hai")

            if end > start:
                item = original[start:end].strip()

                if item and item not in self.data["likes"]:
                    self.data["likes"].append(item)

        self.save()

    def add_history(self, role, content):
        self.data["history"].append({
            "role": role,
            "content": content
        })

        self.data["history"] = (
            self.data["history"][-MAX_HISTORY:]
        )

        self.save()

    def get_history(self):
        return self.data.get(
            "history",
            []
        )[-MAX_HISTORY:]

    def get_context(self):
        context = []

        if self.data.get("name"):
            context.append(
                "The user's name is "
                + self.data["name"]
                + "."
            )

        if self.data.get("likes"):
            context.append(
                "The user likes: "
                + ", ".join(self.data["likes"])
                + "."
            )

        if self.data.get("facts"):
            context.extend(
                self.data["facts"][-10:]
            )

        return "\n".join(context)


class LaylaEngine:

    def __init__(
        self,
        model_path=MODEL_PATH,
        memory_path=MEMORY_PATH
    ):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                "GGUF model not found: "
                + str(self.model_path)
            )

        self.memory = LaylaMemory(memory_path)

        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )

    def _build_messages(self, user_text):
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        saved_memory = self.memory.get_context()

        if saved_memory:
            messages.append({
                "role": "system",
                "content": (
                    "Saved memory about the user:\n"
                    + saved_memory
                )
            })

        for item in self.memory.get_history():
            role = item.get("role")
            content = item.get("content")

            if role in ("user", "assistant") and content:
                messages.append({
                    "role": role,
                    "content": content
                })

        messages.append({
            "role": "user",
            "content": user_text
        })

        return messages

    def chat(self, user_text):
        user_text = user_text.strip()

        if not user_text:
            return ""

        self.memory.learn(user_text)

        messages = self._build_messages(
            user_text
        )

        result = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=256,
            temperature=0.7
        )

        answer = (
            result["choices"][0]["message"]["content"]
            .strip()
        )

        self.memory.add_history(
            "user",
            user_text
        )

        self.memory.add_history(
            "assistant",
            answer
        )

        return answer
