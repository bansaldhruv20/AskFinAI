"""Explicitly rebuild legacy artifacts."""

import faiss
from faq_engine import FAQEngine, ROOT


def main():
    engine = FAQEngine()

    faiss.write_index(
        engine.index,
        str(ROOT / "faq_index.faiss"),
    )

    engine.data.to_pickle(
        ROOT / "faq_data.pkl"
    )

    print(
        f"Indexed {len(engine.data)} unique FAQs "
        "using normalized inner-product search."
    )


if __name__ == "__main__":
    main()
