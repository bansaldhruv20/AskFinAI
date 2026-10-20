"""Local RAG CLI. Legacy filename; no OpenAI dependency."""

from faq_engine import FAQEngine, LocalGenerator
def main():
    engine = FAQEngine()
    generator = LocalGenerator()

    print("AskFinAI local RAG. Type exit to quit.")

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break

        if question.lower() == "exit":
            break

        if question:
            result = engine.search(question)

            print(generator.generate(question, result))
            print("Reference:", result["answer"])


if __name__ == "__main__":
    main()
