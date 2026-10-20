import streamlit as st

from faq_engine import FAQEngine, LocalGenerator
from logger import log_interaction, log_feedback


st.set_page_config(
    page_title="AskFinAI",
    page_icon="💬",
)

st.title("AskFinAI — Fintech FAQ Assistant")

st.caption(
    "Demo FAQ data, not bank-specific advice. "
    "Never enter account numbers, PINs or OTPs."
)

st.write(
    "Ask in English or simple Hinglish. "
    "Answers are in English."
)


@st.cache_resource
def engine():
    return FAQEngine()


@st.cache_resource
def generator():
    return LocalGenerator()


use_rag = st.checkbox(
    "Use local RAG rephrasing (no API key)",
    value=False,
)

st.caption(
    "Semantic search retrieves a FAQ. "
    "Optional local RAG generates a response from that FAQ; "
    "review the reference for accuracy."
)

with st.form("question_form"):
    question = st.text_input("Ask your question:")
    submitted = st.form_submit_button("Find answer")

if submitted:
    st.session_state.pop("result", None)
    st.session_state.pop("feedback_saved", None)

    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Searching FAQs..."):
                result = engine().search(question)

                result["user_question"] = question
                result["reference"] = result["answer"]

                if use_rag and result["accepted"]:
                    try:
                        result["answer"] = generator().generate(
                            question,
                            result,
                        )
                        result["mode"] = "Local RAG"
                    except Exception:
                        st.warning(
                            "Local generation is unavailable. "
                            "Showing the retrieved FAQ answer."
                        )

                st.session_state.result = result

        except Exception:
            st.error(
                "Could not load the FAQ engine. "
                "Check the CSV and download access to the "
                "embedding model; see README."
            )

if "result" in st.session_state:
    result = st.session_state.result

    st.write(result["answer"])

    st.caption(
        f"{result['mode']} · "
        f"cosine similarity {result['score']:.3f} "
        "(not a confidence probability)"
    )

    if result["accepted"]:
        with st.expander("Retrieved reference"):
            st.write(result["question"])
            st.write(result["reference"])
            st.write("Category:", result["category"])

    consent = st.checkbox(
        "Save this demo question and answer locally for evaluation",
        key="log_consent",
    )

    with st.form("feedback_form"):
        helpful = st.radio(
            "Was this helpful?",
            ["Yes", "No"],
            index=None,
        )

        feedback_submit = st.form_submit_button(
            "Submit feedback",
            disabled=st.session_state.get(
                "feedback_saved",
                False,
            ),
        )

    if (
        feedback_submit
        and not st.session_state.get("feedback_saved", False)
    ):
        if helpful is None:
            st.warning(
                "Select Yes or No before submitting."
            )

        elif not consent:
            st.info(
                "Enable local saving to record feedback. "
                "No interaction has been saved."
            )

        else:
            try:
                log_interaction(result)
                log_feedback(result, helpful == "Yes")

                st.session_state.feedback_saved = True
                st.success("Feedback saved. Thank you!")

            except OSError:
                st.error(
                    "Unable to save feedback. "
                    "Check write permissions for the logs directory."
                )
