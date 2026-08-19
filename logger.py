import csv
from datetime import datetime

def log_interaction(user_question, matched_question, matched_answer, gpt_answer, lang, match_score, similarity_score):
    with open("faq_logs.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now(),
            user_question,
            matched_question,
            matched_answer,
            gpt_answer,
            lang,
            round(match_score, 3),
            round(similarity_score, 3)
        ])
