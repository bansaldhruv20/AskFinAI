from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd

index = faiss.read_index("faq_index.faiss")
df = pd.read_pickle("faq_data.pkl")
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_best_faq_answer(user_question, top_k=1):
    user_embedding = model.encode([user_question])
    user_embedding = np.array(user_embedding).astype('float32')
    distances, indices = index.search(user_embedding, top_k)
    best_idx = indices[0][0]
    best_question = df.iloc[best_idx]['question']
    best_answer = df.iloc[best_idx]['answer']
    return best_question, best_answer, distances[0][0]

if __name__ == "__main__":
    print(" Welcome to the FAQ Bot ")
    while True:
        user_query = input("\nAsk your question (or type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            print("Exiting. Goodbye!")
            break
        matched_q, matched_a, distance = find_best_faq_answer(user_query)
        confidence = 1 - distance 
        print(f"\n Matched FAQ: {matched_q}")
        print(f"Answer: {matched_a}")
        print(f"Confidence Score: {confidence:.4f}")
