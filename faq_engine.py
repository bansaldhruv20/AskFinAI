from pathlib import Path
import os
import re

import faiss
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FALLBACK = (
    "I could not find a relevant FAQ. "
    "Please rephrase your question or contact support."
)

# Limited vocabulary bridge for common Romanized Hindi queries.
# This is not general-purpose Hindi translation.
HINGLISH = {
    "wapas": "refund",
    "wapis": "refund",
    "paise": "money",
    "paisa": "money",
    "kab": "when",
    "aayega": "arrive",
    "kare": "do",
    "karu": "do",
    "kaise": "how",
    "kyun": "why",
    "nahi": "not",
    "nahin": "not",
    "bhugtan": "payment",
    "atka": "delayed",
    "kitna": "how much",
    "roz": "daily",
    "khata": "account",
    "jode": "link",
    "jodu": "link",
}


def normalize_query(text):
    text = text.strip().lower()
    text = re.sub(
        r"\b(?:paisa|paise)\s+(?:wapas|wapis)\b",
        "refund",
        text,
    )
    return " ".join(
        HINGLISH.get(word, word)
        for word in re.findall(r"[\w]+", text)
    )


class FAQEngine:
    def __init__(self, threshold=0.55):
        import torch
        from sentence_transformers import SentenceTransformer

        torch.set_num_threads(
            int(os.getenv("ASKFINAI_THREADS", "2"))
        )
        self.threshold = threshold

        data = pd.read_csv(ROOT / "random_faq_100.csv")
        required = {"question", "answer", "category", "platform"}

        if (
            not required.issubset(data.columns)
            or data[list(required)].isna().any().any()
        ):
            raise ValueError(
                "FAQ CSV must contain nonempty question, answer, "
                "category and platform columns."
            )

        # Platform tags are synthetic; answers are generic examples.
        self.data = data.drop_duplicates(
            ["question", "answer"]
        ).reset_index(drop=True)

        if self.data.empty:
            raise ValueError("FAQ dataset is empty.")

        self.model = SentenceTransformer(EMBED_MODEL)

        embeddings = self.model.encode(
            self.data.question.tolist(),
            normalize_embeddings=True,
        )

        # Inner product of normalized vectors = cosine similarity.
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(
            np.asarray(embeddings, dtype="float32")
        )

    def search(self, query):
        if not query.strip():
            raise ValueError("Please enter a question.")

        normalized = normalize_query(query)

        vector = self.model.encode(
            [normalized],
            normalize_embeddings=True,
        )

        scores, ids = self.index.search(
            np.asarray(vector, dtype="float32"),
            1,
        )

        row = self.data.iloc[int(ids[0, 0])]
        score = float(scores[0, 0])
        accepted = score >= self.threshold

        return {
            "question": row.question,
            "answer": row.answer if accepted else FALLBACK,
            "category": row.category,
            "score": score,
            "accepted": accepted,
            "normalized_query": normalized,
            "mode": "Semantic retrieval",
        }


class LocalGenerator:
    def __init__(self):
        import torch
        from transformers import (
            AutoTokenizer,
            AutoModelForSeq2SeqLM,
        )

        torch.set_num_threads(
            int(os.getenv("ASKFINAI_THREADS", "2"))
        )

        name = "google/flan-t5-small"
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(name)
        self.model.eval()

    def generate(self, query, result):
        if not result["accepted"]:
            return result["answer"]

        prompt = (
            "Answer the question using only the reference answer. "
            "Do not add facts. "
            f"Question: {query} "
            f"Reference answer: {result['answer']} "
            "Answer:"
        )

        tokens = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        import torch

        with torch.inference_mode():
            output = self.model.generate(
                **tokens,
                max_new_tokens=100,
                do_sample=False,
            )

        answer = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        ).strip()

        if not answer:
            raise ValueError(
                "Local model returned an empty answer."
            )

        return answer
