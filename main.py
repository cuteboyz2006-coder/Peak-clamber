from pathlib import Path
import json
import sys

from llama_cpp import Llama


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "SmolLM2-135M-Instruct-Q4_K_M.gguf"
MEMORY_PATH = ROOT / "layla_memory.json"


SYSTEM_PROMPT = """
You are Layla, a helpful personal AI assistant.

Your personality:
- Friendly
- Clear
- Helpful
- Natural
- Concise when possible

You can help with:
- General questions
- Study
- Mathematics
- Coding
- Ideas and explanations
- Normal conversation

Always answer the user directly.
"""


class LaylaMemory:
    def __init__(self, path):
        self.path = path
        self.data = self.load()

    def load(self):
        if not self.path.exists():
            return {
                "name": None,
                "likes": [],
                "facts": []
            }

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return {
                "name": data.get("name"),
                "likes": data.get("likes", []),
                "facts": data.get("facts", [])
            }
        except (json.JSONDecodeError, OSError):
            return {
                "name": None,
                "likes": [],
                "facts": []
            }

    def save(self):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)

    def learn(self, text):
        lower = text.lower().strip()

        if lower.startswith("my name is "):
            name = text[11:].strip()
            if name:
                self.data["name"] = name
                self.save()

        elif lower.startswith("mera naam "):
            name = text[9:].strip()
            if name:
                self.data["name"] = name
                self.save()

        elif lower.startswith("i like "):
            item = text[7:].strip()
            if item and item not in self.data["likes"]:
                self.data["likes"].append(item)
                self.save()

        elif "mujhe " in lower and " pasand hai" in lower:
            start = lower.find("mujhe ") + 6
            end = lower.find(" pasand hai")

            item = text[start:end].strip()

            if item and item not in self.data["likes"]:
                self.data["likes"].append(item)
                self.save()

    def context(self):
        parts = []

        if self.data["name"]:
            parts.append(f"The user's name is {self.data['name']}.")

        if self.data["likes"]:
            parts.append(
                "The user likes: "
                + ", ".join(self.data["likes"])
                + "."
            )

        if self.data["facts"]:
            parts.extend(self.data["facts"][-10:])

        return "\n".join(parts)


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

    memory_context = memory.context()

    system_message = SYSTEM_PROMPT

    if memory_context:
        system_message += "\n\nMemory about the user:\n" + memory_context

    result = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        max_tokens=256,
        temperature=0.7,
    )

    return result["choices"][0]["message"]["content"].strip()


def main():
    print("=" * 45)
    print("             LAYLA2")
    print("       Local Personal AI")
    print("=" * 45)

    llm = create_model()
    memory = LaylaMemory(MEMORY_PATH)

    print("\nLayla is ready.")
    print("Type 'exit' to stop.\n")

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:]).strip()

        if prompt:
            print(f"You: {prompt}")
            print(f"Layla: {ask_layla(llm, memory, prompt)}")

        return

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

        answer = ask_layla(llm, memory, user_text)
        print(f"Layla: {answer}")


if __name__ == "__main__":
    main()
