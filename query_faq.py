from functools import lru_cache
from faq_engine import FAQEngine

@lru_cache(maxsize=1)
def get_engine():
    return FAQEngine()


def find_best_faq_answer(user_question, top_k=1):
    if top_k != 1:
        raise ValueError(
            "This assistant returns one best FAQ; "
            "top_k must be 1."
        )

    result = get_engine().search(user_question)

    matched = (
        result["question"]
        if result["accepted"]
        else "No relevant FAQ"
    )

    return matched, result["answer"], result["score"]


def main():
    print(
        "AskFinAI semantic FAQ assistant. "
        "Type exit to quit."
    )

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break

        if question.lower() == "exit":
            break

        if question:
            matched, answer, score = (
                find_best_faq_answer(question)
            )

            print(
                f"FAQ: {matched}\n"
                f"Answer: {answer}\n"
                f"Cosine similarity: {score:.3f}"
            )


if __name__ == "__main__":
    main()
