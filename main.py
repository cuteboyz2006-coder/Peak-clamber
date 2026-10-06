from pathlib import Path
import json
import sys

from llama_cpp import Llama


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "SmolLM2-135M-Instruct-Q4_K_M.gguf"
MEMORY_PATH = ROOT / "layla_memory.json"

MAX_HISTORY = 20


SYSTEM_PROMPT = """
You are Layla, a helpful personal AI assistant.

Personality:
- Friendly
- Natural
- Helpful
- Clear
- Concise when possible

You can help with:
- General questions
- Study
- Mathematics
- Coding
- Ideas
- Explanations
- Normal conversation

Use the user's conversation history and saved memory when useful.

Do not claim to remember something unless it is actually present
in the supplied memory or conversation history.
"""


class LaylaMemory:
    def __init__(self, path):
        self.path = path
        self.data = self.load()

    def default_data(self):
        return {
            "name": None,
            "likes": [],
            "facts": [],
            "history": []
        }

    def load(self):
        if not self.path.exists():
            return self.default_data()

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            result = self.default_data()

            result["name"] = data.get("name")
            result["likes"] = data.get("likes", [])
            result["facts"] = data.get("facts", [])
            result["history"] = data.get("history", [])

            return result

        except (json.JSONDecodeError, OSError, TypeError):
            return self.default_data()

    def save(self):
        try:
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(
                    self.data,
                    file,
                    indent=2,
                    ensure_ascii=False
                )
        except OSError:
            pass

    def learn(self, text):
        original = text.strip()
        lower = original.lower()

        # English name
        if lower.startswith("my name is "):
            name = original[11:].strip()

            if name:
                self.data["name"] = name

        # Hindi/Hinglish name
        elif lower.startswith("mera naam "):
            name = original[10:].strip()

            if name:
                self.data["name"] = name

        # English likes
        elif lower.startswith("i like "):
            item = original[7:].strip()

            if item and item not in self.data["likes"]:
                self.data["likes"].append(item)

        elif lower.startswith("i love "):
            item = original[7:].strip()

            if item and item not in self.data["likes"]:
                self.data["likes"].append(item)

        # Hindi/Hinglish likes
        elif "mujhe " in lower and " pasand hai" in lower:
            start = lower.find("mujhe ") + len("mujhe ")
            end = lower.find(" pasand hai")

            if end > start:
                item = original[start:end].strip()

                if item and item not in self.data["likes"]:
                    self.data["likes"].append(item)

        self.save()

    def add_history(self, role, content):
        self.data["history"].append(
            {
                "role": role,
                "content": content
            }
        )

        self.data["history"] = self.data["history"][-MAX_HISTORY:]

        self.save()

    def context(self):
        parts = []

        if self.data.get("name"):
            parts.append(
                f"The user's name is {self.data['name']}."
            )

        if self.data.get("likes"):
            parts.append(
                "The user likes: "
                + ", ".join(self.data["likes"])
                + "."
            )

        if self.data.get("facts"):
            parts.extend(self.data["facts"][-10:])

        return "\n".join(parts)

    def history(self):
        return self.data.get("history", [])[-MAX_HISTORY:]


def create_model():
    if not MODEL_PATH.exists():
        print("ERROR: GGUF model not found.")
        print(MODEL_PATH)
        sys.exit(1)

    return Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_threads=4,
        verbose=False,
    )


def ask_layla(llm, memory, user_text):
    memory.learn(user_text)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    saved_context = memory.context()

    if saved_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Saved memory about the user:\n"
                    + saved_context
                )
            }
        )

    # Previous conversation
    for item in memory.history():
        role = item.get("role")
        content = item.get("content")

        if role in ("user", "assistant") and content:
            messages.append(
                {
                    "role": role,
                    "content": content
                }
            )

    # Current message
    messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    result = llm.create_chat_completion(
        messages=messages,
        max_tokens=256,
        temperature=0.7,
    )

    answer = (
        result["choices"][0]["message"]["content"]
        .strip()
    )

    memory.add_history("user", user_text)
    memory.add_history("assistant", answer)

    return answer


def memory_test():
    print("Running Layla memory test...")

    llm = create_model()
    memory = LaylaMemory(MEMORY_PATH)

    first = "My name is LaylaUser"
    second = "What is my name?"

    print(f"\nYou: {first}")
    first_answer = ask_layla(llm, memory, first)
    print(f"Layla: {first_answer}")

    print(f"\nYou: {second}")
    second_answer = ask_layla(llm, memory, second)
    print(f"Layla: {second_answer}")

    print("\nMemory test completed.")


def main():
    print("=" * 45)
    print("             LAYLA2")
    print("       Local Personal AI")
    print("=" * 45)

    # GitHub Actions memory test
    if "--test-memory" in sys.argv:
        memory_test()
        return

    llm = create_model()
    memory = LaylaMemory(MEMORY_PATH)

    print("\nLayla is ready.")
    print("Type 'exit' to stop.\n")

    # Single command-line prompt
    if len(sys.argv) > 1:
        prompt = " ".join(
            arg for arg in sys.argv[1:]
            if arg != "--test-memory"
        ).strip()

        if prompt:
            print(f"You: {prompt}")
            answer = ask_layla(llm, memory, prompt)
            print(f"Layla: {answer}")

        return

    # Normal chat
    while True:
        try:
            user_text = input("You: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nLayla: Bye! 👋")
            break

        if user_text.lower() == "exit":
            print("Layla: Bye! 👋")
            break

        if not user_text:
            continue

        answer = ask_layla(
            llm,
            memory,
            user_text
        )

        print(f"Layla: {answer}")


if __name__ == "__main__":
    main()
