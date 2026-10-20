import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import logger
from faq_engine import FAQEngine, normalize_query


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = FAQEngine()

    def test_retrieval_and_rejection(self):
        result = self.engine.search(
            "How do I reset my UPI PIN?"
        )

        self.assertTrue(result["accepted"])
        self.assertEqual(
            result["question"],
            "How do I reset my UPI PIN?",
        )
        self.assertIn(
            "Reset UPI PIN",
            result["answer"],
        )

        unrelated = self.engine.search(
            "Write a recipe for chocolate cake"
        )
        self.assertFalse(unrelated["accepted"])

        with self.assertRaises(ValueError):
            self.engine.search(" ")

    def test_hinglish(self):
        self.assertIn(
            "refund",
            normalize_query("paise wapas kab aayega"),
        )

        result = self.engine.search(
            "upi pin kaise reset karu"
        )

        self.assertEqual(
            result["question"],
            "How do I reset my UPI PIN?",
        )

    def test_streamlit_submit_and_feedback(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(
                logger,
                "LOG_DIR",
                Path(directory),
            ):
                app_path = (
                    Path(__file__).resolve().parents[1]
                    / "app.py"
                )

                app = AppTest.from_file(
                    str(app_path)
                ).run(timeout=120)

                self.assertFalse(app.exception)

                app.text_input[0].set_value(
                    "How do I reset my UPI PIN?"
                )
                app.button[0].click().run(timeout=120)

                self.assertFalse(app.exception)
                self.assertTrue(
                    app.session_state["result"]["accepted"]
                )

                # No logs before explicit consent/submission.
                self.assertFalse(
                    list(Path(directory).iterdir())
                )

                app.checkbox[1].check()
                app.radio[0].set_value("Yes")
                app.button[1].click().run()

                feedback_file = (
                    Path(directory) / "feedback.csv"
                )

                self.assertEqual(
                    len(
                        feedback_file.read_text().splitlines()
                    ),
                    2,
                )

                # A rerun must not duplicate the feedback.
                app.run()

                self.assertEqual(
                    len(
                        feedback_file.read_text().splitlines()
                    ),
                    2,
                )


if __name__ == "__main__":
    unittest.main()
