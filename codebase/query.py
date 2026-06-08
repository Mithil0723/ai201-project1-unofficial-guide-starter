"""
query.py — Retrieval-Augmented Generation
Pipeline stage 3: Retrieve relevant chunks, then generate a grounded answer via Groq.

Public API:
    ask(question, k=5) -> {"answer": str, "sources": list[str]}
"""

import os
from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

# ---------------------------------------------------------------------------

load_dotenv()  # reads GROQ_API_KEY from .env

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """\
You are a knowledgeable assistant specialising in the scientific and ecological \
reasoning behind traditional Indian food and health practices. \
Answer ONLY from the context passages provided below. \
If the context does not contain enough information to answer, say so clearly — \
do not guess or hallucinate. \
Always cite which source document(s) your answer draws from.\
"""

# ---------------------------------------------------------------------------


def _build_context_block(hits: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    lines = []
    for i, h in enumerate(hits, start=1):
        lines.append(f"[{i}] (Source: {h['source']})\n{h['text']}")
    return "\n\n".join(lines)


def _unique_sources(hits: list[dict]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for h in hits:
        if h["source"] not in seen:
            seen.add(h["source"])
            sources.append(h["source"])
    return sources


def ask(question: str, k: int = 5) -> dict:
    """
    Ask a question against the indexed documents.

    Returns:
        {
            "answer": str,        # grounded answer text
            "sources": list[str], # deduplicated source filenames
        }
    """
    # Step 1: Retrieve relevant chunks
    hits = retrieve(question, k=k)
    if not hits:
        return {
            "answer": "No relevant information found in the indexed documents.",
            "sources": [],
        }

    # Step 2: Build prompt
    context_block = _build_context_block(hits)
    user_message = (
        f"Context passages:\n\n{context_block}\n\n"
        f"Question: {question}\n\n"
        "Answer based only on the context above. Cite the source(s) used."
    )

    # Step 3: Call Groq
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY is not set. Add it to your .env file.")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,       # low temperature for factual, grounded answers
        max_tokens=1024,
    )

    answer = response.choices[0].message.content.strip()
    sources = _unique_sources(hits)

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    # Run the 5 evaluation questions from planning.md
    eval_questions = [
        "What does the research say about curcumin's effect on inflammation?",
        "Why does storing water in copper vessels have health benefits?",
        "What is the nutritional reason dal and rice are traditionally eaten together?",
        "What happens metabolically during Ekadashi or similar Indian fasting practices?",
        "What is Ritucharya and why does Ayurveda recommend seasonal eating?",
    ]

    for q in eval_questions:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        result = ask(q)
        print(f"\nA: {result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
