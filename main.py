from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "SmolLM2-135M-Instruct-Q4_K_M.gguf"


def main():
    print("=" * 40)
    print("        LAYLA2 - LOCAL AI")
    print("=" * 40)

    if Llama is None:
        print("\nllama-cpp-python is not installed.")
        print("Install it with:")
        print("pip install llama-cpp-python")
        return

    if not MODEL_PATH.exists():
        print("\nModel not found!")
        print(f"Expected location:\n{MODEL_PATH}")
        print("\nPut the GGUF model inside the models folder.")
        return

    print("\nLoading Layla local model...")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        verbose=False,
    )

    print("Layla is ready!")
    print("Type 'exit' to close.\n")

    while True:
        user_text = input("You: ").strip()

        if user_text.lower() == "exit":
            print("Layla: Bye! 👋")
            break

        if not user_text:
            continue

        result = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Layla, a helpful personal AI assistant. "
                        "Answer clearly and naturally."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
            max_tokens=256,
            temperature=0.7,
        )

        answer = result["choices"][0]["message"]["content"].strip()

        print(f"Layla: {answer}")


if __name__ == "__main__":
    main()
