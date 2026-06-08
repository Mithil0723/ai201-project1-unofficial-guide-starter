# The Unofficial Guide — Project 1

---

## Domain

The domain is the scientific and ecological reasoning behind traditional Indian food and health practices — things like why dal and rice are eaten together, why copper vessels store water, why fasting follows lunar cycles.

This knowledge exists but is scattered across disciplines. A doctor might know the metabolic angle on fasting; an Ayurvedic practitioner knows the seasonal eating logic; a food scientist can explain fermentation in idli batter. No single resource lets someone ask "why do we actually do this" and get an answer grounded in research rather than mythology or vague wellness content. That is the gap this system fills.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | PMC peer-reviewed review | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC9881416/ |
| 2 | Science Meets Food (IFT) | Science blog / article | https://sciencemeetsfood.org/banana-leaves/ |
| 3 | PMC editorial on Ramadan fasting | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC12023006/ |
| 4 | Journal of Traditional and Complementary Medicine (PMC) | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC5506628/ |
| 5 | Ayu Journal (PMC) | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC3361919/ |
| 6 | PMC research article — copper vessel water | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC6437792/ |
| 7 | PMC research article — traditional food storage | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC3857414/ |
| 8 | PMC research article — idli fermentation | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC9525534/ |
| 9 | Stevens Institute of Technology — eating with hands | Research news | https://www.stevens.edu/news/touching-food-directly-your-hands-makes-eating-more-enjoyable |
| 10 | PMC review — Ayurvedic food and health | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC4815005/ |

---

## Chunking Strategy

**Chunk size:** ~450 characters

**Overlap:** 60 characters

**Why these choices fit the documents:** The sources are academic articles, not short reviews. Key findings tend to sit inside a single paragraph: a claim, its supporting evidence, then context. A chunk that is too small (e.g. 150 characters) cuts sentences in half and loses the claim-evidence link. A chunk that is too large (800+ characters) blends multiple findings from different sections, making it harder to match a specific query. 450 characters keeps one coherent idea per chunk — usually a finding plus one sentence of context. The 60-character overlap handles cases where a key phrase straddles a boundary, such as a conclusion sentence that opens the next paragraph. Before chunking, the text is cleaned by stripping Markdown syntax (headings, bold, links) and HTML artifacts, then collapsing excess whitespace. The chunker also snaps split points to the nearest sentence boundary within an 80-character look-back window to avoid cutting mid-sentence.

**Final chunk count:** 175 chunks across 10 documents

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (local, no API cost)

**Production tradeoff reflection:** Several tradeoffs would be worth weighing for a real deployment. `text-embedding-3-small` (OpenAI) has better accuracy on domain-specific text but requires an API call and ongoing cost per query. `paraphrase-multilingual-MiniLM-L12-v2` would be the better choice if the system ever needs to handle Hindi queries alongside English. Context length also matters: some of these PMC articles have dense, long sentences, and a model with a longer max token window would handle those better without truncation. On latency, a local model like `all-MiniLM-L6-v2` wins decisively — no network round-trip — but at the cost of lower accuracy compared to larger API-hosted models.

---

## Grounded Generation

**System prompt grounding instruction:**

> "You are a knowledgeable assistant specialising in the scientific and ecological reasoning behind traditional Indian food and health practices. Answer ONLY from the context passages provided below. If the context does not contain enough information to answer, say so clearly — do not guess or hallucinate. Always cite which source document(s) your answer draws from."

The user turn presents the retrieved chunks as a numbered list (e.g. `[1] (Source: 01_turmeric_curcumin.md) …`) followed by the question, explicitly instructing the model to answer only from the context above and to cite the source(s) used.

**How source attribution is surfaced in the response:** The `ask()` function in `query.py` returns a dict with two keys: `answer` (the model's text) and `sources` (a deduplicated list of source filenames drawn from the retrieved chunks). The Gradio UI displays these in separate output boxes — the answer on the left, and the source filenames as a bulleted list on the right — so the user always sees which documents the answer came from.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What does the research say about curcumin's effect on inflammation? | Curcumin inhibits NF-κB, reduces pro-inflammatory cytokines | Correct — cited NF-κB inhibition, COX-2, iNOS suppression | Relevant | Accurate |
| 2 | Why does storing water in copper vessels have health benefits? | Copper ions kill bacteria, reduces diarrheal disease | Correct — cited oligodynamic effect and bacterial disruption mechanism | Relevant | Accurate |
| 3 | What is the nutritional reason dal and rice are eaten together? | Protein complementarity — lysine + methionine | Correct — cited amino acid complementarity from 10_dal_rice_food_combining.md | Relevant | Accurate |
| 4 | What happens metabolically during Ekadashi fasting? | Glycogen depletion → fatty acid/ketone metabolism | Correct — cited glycogenolysis then adaptive fat and ketone metabolism | Relevant | Accurate |
| 5 | What is Ritucharya and why does Ayurveda recommend seasonal eating? | Six-season regimen, physiological adaptation to environment | Correct on what Ritucharya is, but thin on the mechanistic why | Partially relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** Why do we eat with our right hand specifically?

**What the system returned:** "The context passages provided do not contain enough information to answer why we eat with our right hand specifically. The passages discuss the benefits and cultural significance of eating with hands in general, but they do not mention any specific reason for using the right hand over the left."

**Root cause (tied to a specific pipeline stage):** This is a document coverage gap, not a chunking or embedding failure. The retrieval stage correctly pulled the top chunks from `09_eating_with_hands.md` — those chunks were genuinely the most semantically relevant to the query. But none of the 10 source documents address the cultural, hygienic, or Ayurvedic rationale specific to the right hand. The system behaved correctly by refusing to answer rather than hallucinating; the gap is upstream in the ingestion stage, where no source covering handedness in eating was collected.

**What you would change to fix it:** Add a source covering the anthropological or Ayurvedic reasoning behind handedness — for example, a paper on ritual food practices in South Asian culture or an Ayurvedic text on the significance of the right hand in eating. This would give the retrieval stage something to actually find.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The chunking strategy section in planning.md was probably the most useful part. Before writing ingest.py, I already knew the chunk size should be around 450 characters and overlap should be 60 characters, and more importantly I knew why. So when I gave the spec to Claude Code and asked it to implement the chunking function, I could actually check if what it generated made sense. Without the spec I would have just accepted whatever the AI gave me. Having the reasoning written down beforehand made it easier to catch when the loop guard logic looked off.

**One way your implementation diverged from the spec, and why:**

The spec said the documents would be .txt files, but I actually collected and saved all 10 sources as .md files. So ingest.py had to be updated to glob *.md instead of *.txt. It is a small change but it was not in the original plan. I realized this only after running dir /b and seeing the documents folder. The content itself is still plain text so the chunking works the same way, just the file extension is different.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* I gave Claude Code the full planning.md file and asked it to generate all four pipeline scripts (ingest.py, embed.py, query.py, app.py) inside a codespace subfolder, following the architecture diagram and technical choices written in the spec.
- *What it produced:* It generated all four files in one go. The chunking logic, ChromaDB setup, Groq API call, and Gradio UI were all there. It also added a README inside codespace explaining the run order.
- *What I changed or overrode:* The spec said .txt files but my documents were .md, so I asked it to update the glob pattern in ingest.py. Also the chunk size in the spec was "around 450" and Claude used exactly 450, which was fine.

**Instance 2**

- *What I gave the AI:* I asked Claude Code to review the codespace folder as a senior AI engineer, after first reading planning.md. I wanted it to check if the implementation matched the spec and if there were any bugs.
- *What it produced:* It found 5 issues: gradio was commented out in requirements.txt, the GROQ_API_KEY was not failing fast if missing, chromadb.Client() was deprecated, the loop guard in ingest.py could cause problems on short texts, and retrieve() had no guard for empty collections. It also applied all the fixes itself.
- *What I changed or overrode:* I reviewed each fix before accepting. The chromadb fix and the loop guard fix I checked manually because I was not fully sure what the original code was doing. Everything looked correct so I kept all changes.