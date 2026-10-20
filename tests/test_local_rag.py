import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from faq_engine import FALLBACK, LocalGenerator


class LocalRAGTests(unittest.TestCase):
    def test_rejected_query_bypasses_generation(self):
        generator = object.__new__(LocalGenerator)

        answer = generator.generate(
            "unrelated",
            {
                "accepted": False,
                "answer": FALLBACK,
            },
        )

        self.assertEqual(answer, FALLBACK)

    def test_local_rag_ui(self):
        app_path = (
            Path(__file__).resolve().parents[1]
            / "app.py"
        )

        app = AppTest.from_file(
            str(app_path)
        ).run(timeout=120)

        app.checkbox[0].check()
        app.text_input[0].set_value(
            "How do I reset my UPI PIN?"
        )
        app.button[0].click().run(timeout=120)

        self.assertFalse(app.exception)

        result = app.session_state["result"]

        self.assertEqual(
            result["mode"],
            "Local RAG",
        )
        self.assertTrue(result["answer"].strip())
        self.assertIn(
            "pin",
            result["answer"].lower(),
        )
        self.assertIn(
            "Reset UPI PIN",
            result["reference"],
        )


if __name__ == "__main__":
    unittest.main()
