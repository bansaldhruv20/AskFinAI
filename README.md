# AskFinAI

A fintech FAQ assistant using sentence embeddings and FAISS,
with optional local retrieval-augmented generation.

No OpenAI API key or paid inference service is required.

## Features

- Semantic FAQ retrieval using all-MiniLM-L6-v2.
- FAISS cosine-similarity search.
- Low-relevance query rejection.
- Limited Hinglish vocabulary normalization.
- Optional local RAG using google/flan-t5-small.
- Retrieved reference displayed for verification.
- Explicit feedback submission and opt-in local logging.

## Setup

Python 3.12 was validated in the cloud environment.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

For CPU-only PyTorch on supported Linux/Windows systems,
install PyTorch first:

```bash
python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

## Run

```bash
python -m streamlit run app.py
```

The first query downloads the embedding model.
The first local RAG query also downloads Flan-T5.

Keep internet access available during those downloads.
After caching both models, the app can run offline.

The default mode returns the retrieved FAQ answer.
Enable "Use local RAG rephrasing" for generation.

CLI retrieval:

```bash
python query_faq.py
```

CLI local RAG:

```bash
python query_faq_gpt.py
```

The latter filename is retained for compatibility;
it no longer uses GPT or OpenAI.

## Data and architecture

The app reads random_faq_100.csv, deduplicates question/answer
pairs and builds a small FAISS index in memory.

FAQ questions and user queries are embedded with MiniLM.
Normalized inner-product search returns cosine similarity.

Scores below a provisional threshold of 0.55 are rejected.
This score is not a confidence probability. The threshold
needs calibration on a larger representative dataset.

Common Romanized Hindi terms are normalized before retrieval.
This supports selected Hinglish examples, not unrestricted
Hindi translation or arbitrary code-switching.

Answers are in English.

In local RAG mode, Flan-T5 receives the retrieved FAQ answer
as context and generates a response. Generated answers can
omit or distort details; the original reference remains visible.
Generation failures fall back to the retrieved answer.

## Existing artifacts

faq_index.faiss and faq_data.pkl are legacy artifacts retained
in the repository. The app does not load them.

build_faiss_index.py explicitly regenerates those artifacts.
It is not required during setup.

generate_faqs.py overwrites the demo CSV with randomly generated
examples. Do not run it merely to start the application.

## Evaluation

```bash
python evaluate.py
python -m unittest discover -s tests -v
```

evaluate.py writes evaluation/results.json.

The evaluation cases are a tiny authored regression set.
They are not a held-out benchmark, production accuracy
measurement or evidence of ticket deflection.

Tests require model downloads or previously cached models.
First-time downloads can take longer than UI test timeouts;
download the models through the app before running all tests.

## Limitations

- The 100 FAQ rows are synthetic examples.
- Platform labels are randomly assigned.
- Answers are not verified provider-specific policies.
- No live account or transaction integration is provided.
- Hinglish handling uses a limited explicit vocabulary bridge.
- The small local generator is not guaranteed to improve
  or preserve every detail of the reference answer.
- Logging is opt-in and stored under logs/.
- Do not enter personal information, account numbers, PINs or OTPs.
