from logger import log_interaction
import streamlit as st
import numpy as np
import pandas as pd
import faiss
import os
from sentence_transformers import SentenceTransformer
from deep_translator import GoogleTranslator
from langdetect import detect
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.environ["TOKENIZERS_PARALLELISM"] = "false"

@st.cache_resource
def load_resources():
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("faq_index.faiss")
    df = pd.read_pickle("faq_data.pkl")
    return embed_model, index, df

embed_model, index, df = load_resources()

def find_best_faq(query, top_k=1):
    embedding = embed_model.encode([query])
    embedding = np.array(embedding).astype('float32')
    distances, indices = index.search(embedding, top_k)
    idx = indices[0][0]
    return df.iloc[idx]['question'], df.iloc[idx]['answer'], distances[0][0]

def get_similarity_score(text1, text2):
    emb1 = embed_model.encode([text1])[0]
    emb2 = embed_model.encode([text2])[0]
    emb1 /= np.linalg.norm(emb1)
    emb2 /= np.linalg.norm(emb2)
    return float(np.dot(emb1, emb2))

def rephrase_with_openai(user_q, faq_q, faq_a):
    prompt = (
        f"You are a helpful assistant for an app user.\n\n"
        f"User question: {user_q}\n"
        f"Matched FAQ question: {faq_q}\n"
        f"Answer: {faq_a}\n\n"
        f"Rephrase the answer in a friendly and natural tone:"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return faq_a

def translate_text(text, target='en'):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return text  #fallback in case not working fine and return original text

st.set_page_config(page_title="Jupiter FAQ Bot", page_icon="🤖")
st.title("🤖 Jupiter Help Centre FAQ Bot")
st.write("Ask your question in English, Hindi, or Hinglish — get a friendly answer instantly!")

user_input = st.text_input("Ask your question:")

if user_input:
    with st.spinner("Generating answer..."):
        try:
            detected_lang = detect(user_input)
            query_en = translate_text(user_input, target='en') if detected_lang != 'en' else user_input

            matched_q, matched_a, dist = find_best_faq(query_en)
            rephrased = rephrase_with_openai(query_en, matched_q, matched_a)
            similarity = get_similarity_score(matched_a, rephrased)
            final_answer = translate_text(rephrased, target=detected_lang) if detected_lang != 'en' else rephrased
            st.success("Here's your answer:")
            st.markdown(f"**Q:** {matched_q}")
            st.markdown(f"**A:** {final_answer}")
            st.caption(f"Language: {detected_lang.upper()} | FAQ Match Score: {1 - dist:.2f} | GPT Similarity: {similarity:.2f}")

            # Log to logger
            log_interaction(
                user_input,
                matched_q,
                matched_a,
                final_answer,
                detected_lang,
                1 - dist,
                similarity
            )

            #Feedback section
            st.markdown("---")
            st.write("Was this answer helpful?")
            feedback = st.radio("Feedback", ("👍 Yes", "👎 No"), horizontal=True, key="feedback_radio")

            if feedback:
                feedback_value = 1 if feedback == "👍 Yes" else 0
                st.success("Thanks for your feedback!")

                feedback_data = {
                    "question": user_input,
                    "matched_faq": matched_q,
                    "answer_given": final_answer,
                    "language": detected_lang,
                    "match_score": 1 - dist,
                    "similarity": similarity,
                    "feedback": feedback_value
                }
                feedback_df = pd.DataFrame([feedback_data])
                if os.path.exists("feedback_log.csv"):
                    feedback_df.to_csv("feedback_log.csv", mode='a', header=False, index=False)
                else:
                    feedback_df.to_csv("feedback_log.csv", index=False)

        except Exception as err:
            st.error(f"Something went wrong: {err}")
