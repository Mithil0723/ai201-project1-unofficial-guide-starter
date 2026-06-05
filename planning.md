# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain is the scientific and ecological reasoning behind traditional Indian food and health practices. Things like why dal and rice are eaten together, why copper vessels store water, why fasting follows lunar cycles.

This knowledge exists, but it's scattered. A doctor might know the metabolic angle on fasting. An Ayurvedic practitioner knows the seasonal eating logic. A food scientist can explain fermentation in idli batter. None of them are talking to each other, and there's no single place where someone can ask "why do we actually do this" and get an answer grounded in research rather than mythology or vague wellness content. That's the gap this system fills.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
| --- | --- | --- | --- |
| 1 | PMC peer-reviewed review | Curcumin's antioxidant, anti-inflammatory, antimicrobial, and metabolic effects | https://pmc.ncbi.nlm.nih.gov/articles/PMC9881416/ |
| 2 | Science Meets Food (IFT) | Phytochemical and antioxidant properties of banana leaves | https://sciencemeetsfood.org/banana-leaves/ |
| 3 | PMC editorial on Ramadan fasting | Metabolic health, insulin sensitivity, inflammation, and circadian rhythm | https://pmc.ncbi.nlm.nih.gov/articles/PMC12023006/ |
| 4 | Journal of Traditional and Complementary Medicine (PMC) | Digestive effects of hing, ajwain, and jeera with experimental data | https://pmc.ncbi.nlm.nih.gov/articles/PMC5506628/ |
| 5 | Ayu Journal (PMC) | Ritucharya: Ayurvedic seasonal regimen and physiological adaptation | https://pmc.ncbi.nlm.nih.gov/articles/PMC3361919/ |
| 6 | PMC research article | Copper vessel water storage and reduction of bacterial contamination | https://pmc.ncbi.nlm.nih.gov/articles/PMC6437792/ |
| 7 | PMC research article | Shelf life and storage issues in Indian traditional foods | https://pmc.ncbi.nlm.nih.gov/articles/PMC3857414/ |
| 8 | PMC research article | Microbial ecology of idli fermentation via high-throughput sequencing | https://pmc.ncbi.nlm.nih.gov/articles/PMC9525534/ |
| 9 | Stevens Institute of Technology | Sensory research on direct touch and perceived food enjoyment when eating with hands | https://www.stevens.edu/news/touching-food-directly-your-hands-makes-eating-more-enjoyable |
| 10 | PMC review on Ayurvedic food and health | Traditional food and health concepts compared with biomedical ideas, including food combining | https://pmc.ncbi.nlm.nih.gov/articles/PMC4815005/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400-500 characters

**Overlap:** 50-75 characters

**Reasoning:**
These are academic articles, not short reviews. The key facts tend to sit inside a paragraph: a claim, then its supporting evidence, then context. A chunk that's too small (say, 150 characters) would cut a sentence in half and lose the claim-evidence link. A chunk that's too large (800+ characters) would blend multiple findings from different sections, making it harder to match a specific query.

400–500 characters keeps one coherent idea per chunk, usually a finding plus one sentence of context. The 50-character overlap handles cases where a key phrase straddles a boundary (e.g., a conclusion sentence that opens the next paragraph).

If retrieval consistently pulls vague or loosely related chunks, I'll try bumping to 600 characters and see if that helps.

**Expected chunk count:** Roughly 150–400 chunks across 10 documents, depending on article length.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2`

**Top-k:** Starting at 5. If responses feel thin, try 7. If they feel noisy, drop to 3.

**Production tradeoff reflection:**
- `text-embedding-3-small` (OpenAI) has better accuracy on domain-specific text but costs money and requires an API call per query.
- `paraphrase-multilingual-MiniLM-L12-v2` if the system ever needs to handle Hindi queries alongside English.
- Context length matters: some of these PMC articles have dense, long sentences. A model with a longer max token window would handle those better without truncation.
- Latency: local models win here. For a production API, embedding latency adds up at scale.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |  What does the research say about curcumin's effect on inflammation? | Curcumin inhibits NF-κB signaling and reduces pro-inflammatory cytokines; multiple studies show anti-inflammatory properties comparable to some NSAIDs without the side effects. |
| 2 | Why does storing water in copper vessels have health benefits? | Copper ions leach into the water over time and have demonstrated antibacterial effects; the PMC study showed stored water killed a significant proportion of bacteria after several hours. |
| 3 | What is the nutritional reason dal and rice are traditionally eaten together? | Rice is low in lysine; legumes like dal are low in methionine. Together they form a complete amino acid profile. IAAO studies confirm combining them increases metabolic availability of both limiting amino acids. |
| 4 |  What happens metabolically during Ekadashi or similar Indian fasting practices? | Short-term fasting triggers metabolic shifts including improved insulin sensitivity, reduced triglycerides, and autophagy activation. This is documented in the Indian Journal of Endocrinology and Metabolism study. |
| 5 | What is Ritucharya and why does Ayurveda recommend seasonal eating? | Ritucharya is the Ayurvedic seasonal regimen prescribing diet and lifestyle changes across six seasons. The Ayu Journal paper connects this to physiological adaptation: digestive capacity and dosha balance shift with climate, and seasonal foods tend to match those shifts. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Dense academic language vs. plain-language queries:** The documents use technical terms (curcumin, NF-κB, IAAO, dosha). A user asking "why is turmeric healthy" probably won't use any of those words. The semantic embedding should bridge this, but it's worth testing explicitly during retrieval validation.

2.**Overlapping topics across documents:** Fermented foods, spices, and seasonal eating all touch gut health. A query about gut health could pull chunks from three different sources, some directly relevant and some tangential. This might dilute response quality. Metadata filtering by topic could help as a stretch feature.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

[Raw Documents (.txt files)]
         |
         v
   ingest.py
   - Load from /documents
   - Clean: strip HTML, whitespace
   - Chunk: ~450 chars, 60 overlap
         |
         v
   embed.py
   - Embed: all-MiniLM-L6-v2 (sentence-transformers)
   - Store: ChromaDB + source metadata
         |
         v
   query.py
   - Retrieve: top-5 chunks via semantic similarity
   - Generate: Groq llama-3.3-70b-versatile
   - Ground: context-only prompt + source attribution
         |
         v
   app.py
   - Interface: Gradio UI
   - Input: user question
   - Output: answer + source list

---

## AI Tool Plan

**Ingestion + chunking (`ingest.py`)**

Input to AI: the Documents section above (file types, sources), the chunking strategy section, and the pipeline diagram. Ask it to implement a script that loads `.txt` files from `/documents`, cleans them (strip HTML artifacts, excess whitespace), splits into ~450-character chunks with 60-character overlap, and outputs a list of dicts with `{text, source, chunk_index}`.

**Embedding + ChromaDB (`embed.py`)**

Input to AI: the Retrieval Approach section and the pipeline diagram. Ask it to load chunks from `ingest.py` output, embed with `all-MiniLM-L6-v2`, store in a local ChromaDB collection with source metadata attached, and expose a `retrieve(query, k=5)` function.

**Generation (`query.py`)**

Input to AI: the grounding requirement (answer only from retrieved context, include source names) and the Groq model name. Ask it to implement a function that takes a query, calls `retrieve()`, builds a prompt with context, calls `llama-3.3-70b` via Groq, and returns `{answer, sources}`.

**Interface (`app.py`)**

Input to AI: the `ask()` function signature from `query.py`. Ask it to build a minimal Gradio UI with a text input, an Ask button, an answer output box, and a sources output box.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
