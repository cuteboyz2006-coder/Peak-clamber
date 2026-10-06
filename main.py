import sys

from layla_engine import LaylaEngine


def main():
    print("=" * 45)
    print("             LAYLA2")
    print("       Local Personal AI")
    print("=" * 45)

    try:
        layla = LaylaEngine()
    except Exception as error:
        print("\nERROR: Layla could not start.")
        print(error)
        sys.exit(1)

    print("\nLayla is ready.")
    print("Type 'exit' to stop.\n")

    # Simple automated test
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:]).strip()

        if prompt:
            print(f"You: {prompt}")
            answer = layla.chat(prompt)
            print(f"Layla: {answer}")

        return

    # Normal terminal chat
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

        answer = layla.chat(user_text)
        print(f"Layla: {answer}")


if __name__ == "__main__":
    main()
