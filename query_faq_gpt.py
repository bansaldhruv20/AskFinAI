import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
index = faiss.read_index("faq_index.faiss")
df = pd.read_pickle("faq_data.pkl")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
def find_best_faq_answer(user_question, top_k=1):
    user_embedding = embed_model.encode([user_question])
    user_embedding = np.array(user_embedding).astype('float32')
    distances, indices = index.search(user_embedding, top_k)
    best_idx = indices[0][0]
    best_question = df.iloc[best_idx]['question']
    best_answer = df.iloc[best_idx]['answer']
    return best_question, best_answer, distances[0][0]

def get_rephrased_answer(user_question, matched_question, matched_answer):
    prompt = (
        f"You are a helpful chatbot for a platform. "
        f"A user asked: \"{user_question}\".\n"
        f"The most relevant FAQ is:\n"
        f"Q: {matched_question}\n"
        f"A: {matched_answer}\n\n"
        f"Please rephrase the answer in a friendly, natural tone suitable for app users:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print("Error with OpenAI API:", e)
        return matched_answer 

if __name__ == "__main__":
    print("FAQ Bot is ready! Ask me your question.")
    while True:
        user_input = input("\nAsk your question (or type 'exit'): ")
        if user_input.lower() == 'exit':
            break
        matched_q, matched_a, dist = find_best_faq_answer(user_input)
        rephrased = get_rephrased_answer(user_input, matched_q, matched_a)
        print(f"\nMatched FAQ: {matched_q}")
        print(f"Bot Answer: {rephrased}")
        print(f"Confidence Score: {1 - dist:.4f}")
