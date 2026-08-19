from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd

df = pd.read_csv("random_faq_100.csv")
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['question'].tolist()).astype('float32')
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, "faq_index.faiss")
df.to_pickle("faq_data.pkl")
print("Indexed:", len(df))
