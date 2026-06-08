# The Unofficial Guide - Project 1

---

## Domain

This project is about the scientific reasoning behind traditional Indian food and health practices. Things like why dal and rice are eaten together, why people store water in copper vessels, why fasting is connected to lunar cycles. These practices have been followed for generations but most people do not know the actual science behind them.

The problem is that this information is not in one place. A doctor might know the metabolic side of fasting. An Ayurveda practitioner knows the seasonal eating logic. A food scientist understands idli fermentation. None of this is collected together in a way that a normal person can just ask a question and get a proper research-backed answer. That is what this system is trying to do.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | PMC peer-reviewed review | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC9881416/ |
| 2 | Science Meets Food (IFT) | Science blog / article | https://sciencemeetsfood.org/banana-leaves/ |
| 3 | PMC editorial on Ramadan fasting | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC12023006/ |
| 4 | Journal of Traditional and Complementary Medicine (PMC) | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC5506628/ |
| 5 | Ayu Journal (PMC) | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC3361919/ |
| 6 | PMC research article on copper vessel water | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC6437792/ |
| 7 | PMC research article on traditional food storage | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC3857414/ |
| 8 | PMC research article on idli fermentation | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC9525534/ |
| 9 | Stevens Institute of Technology on eating with hands | Research news | https://www.stevens.edu/news/touching-food-directly-your-hands-makes-eating-more-enjoyable |
| 10 | PMC review on Ayurvedic food and health | Academic article | https://pmc.ncbi.nlm.nih.gov/articles/PMC4815005/ |

---

## Chunking Strategy

**Chunk size:** ~450 characters

**Overlap:** 60 characters

**Why these numbers were chosen:** All 10 sources are academic articles. They are not short blog posts. In these articles, the important information usually sits inside one paragraph: a finding, then the evidence for it, then some context. If the chunk is too small, like 150 characters, a sentence gets cut in the middle and the meaning is lost. If it is too large, like 800+ characters, multiple unrelated findings get mixed into one chunk and retrieval becomes less accurate.

450 characters usually fits one complete idea with a little bit of surrounding context. The 60-character overlap is there because sometimes a key sentence starts at the end of one chunk and continues into the next. Without overlap, that sentence would be split and retrieval would miss it. Before chunking, the text goes through basic cleaning: markdown headings, bold formatting, and extra whitespace are removed. The chunker also tries to break at sentence boundaries instead of cutting mid-sentence.

**Final chunk count:** 175 chunks across 10 documents

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key needed)

**Production tradeoff reflection:** For this project, `all-MiniLM-L6-v2` works fine. It runs locally so there is no cost and no latency from a network call. But if this was being deployed for real users, a few things would be worth reconsidering.

`text-embedding-3-small` from OpenAI would give better accuracy on domain-specific text like these PMC articles, but it costs money and needs an API call for every query. If the system needed to handle Hindi questions along with English, `paraphrase-multilingual-MiniLM-L12-v2` would be a better fit. Some of the PMC articles also have very long dense sentences, and a model with a higher token limit would handle those without truncation. So it depends on what the priority is: cost, accuracy, or language support.

---

## Grounded Generation

**System prompt used:**

> "You are a knowledgeable assistant specialising in the scientific and ecological reasoning behind traditional Indian food and health practices. Answer ONLY from the context passages provided below. If the context does not contain enough information to answer, say so clearly - do not guess or hallucinate. Always cite which source document(s) your answer draws from."

The retrieved chunks are passed to the model as a numbered list, like `[1] (Source: 01_turmeric_curcumin.md) ...`, and the question comes after. The model is told explicitly to only use what is in those passages.

**How source attribution works:** The `ask()` function in `query.py` returns two things: the answer text and a deduplicated list of source filenames from the retrieved chunks. In the Gradio UI, the answer shows on one side and the source filenames show on the other side as a list. So the user can always see where the answer came from.

**Out-of-scope query example:**

Query: "Why do we eat with our right hand specifically?"

System response: "The context passages provided do not contain enough information to answer why we eat with our right hand specifically. The passages discuss the benefits and cultural significance of eating with hands in general, but they do not mention any specific reason for using the right hand over the left."

The system refused to guess. It told the user what was missing rather than making something up.

**Example responses with source attribution:**

Query: "Why does storing water in a copper vessel help?"

Response: "We store water in a copper material because copper has antibacterial properties. The copper ions released into the water are lethal to bacteria, disrupting their cell membrane and inhibiting key enzymes involved in energy metabolism and DNA replication (Source: [2] 06_copper_vessel_water.md). This property of copper helps in reducing diarrheal disease episodes, as found in a study on copper vessel water storage (Source: [1] and [3], 06_copper_vessel_water.md)."

Query: "What is the nutritional reason dal and rice are eaten together?"

Response: "The nutritional reason dal and rice are traditionally eaten together is due to protein complementarity. When combined, the amino acid profiles of rice and lentils increase the metabolic availability of both lysine (from the lentils) and methionine (from the rice), allowing the body to utilize the combined protein more efficiently than either food eaten alone. (Source: [2] and [3], 10_dal_rice_food_combining.md)"

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What does the research say about curcumin's effect on inflammation? | Curcumin inhibits NF-kB, reduces pro-inflammatory cytokines | Correct - cited NF-kB inhibition, COX-2, iNOS suppression | Relevant | Accurate |
| 2 | Why does storing water in copper vessels have health benefits? | Copper ions kill bacteria, reduces diarrheal disease | Correct - cited oligodynamic effect and bacterial disruption mechanism | Relevant | Accurate |
| 3 | What is the nutritional reason dal and rice are eaten together? | Protein complementarity - lysine + methionine | Correct - cited amino acid complementarity from 10_dal_rice_food_combining.md | Relevant | Accurate |
| 4 | What happens metabolically during Ekadashi fasting? | Glycogen depletion then fatty acid/ketone metabolism | Correct - cited glycogenolysis then adaptive fat and ketone metabolism | Relevant | Accurate |
| 5 | What is Ritucharya and why does Ayurveda recommend seasonal eating? | Six-season regimen, physiological adaptation to environment | Correct on what Ritucharya is, but thin on the mechanistic why | Partially relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** Why do we eat with our right hand specifically?

**What the system returned:** It said the context does not have enough information to answer that question. The passages talk about eating with hands in general but do not mention anything specific to the right hand.

**Root cause:** This is not a chunking problem or an embedding problem. The retrieval stage did its job correctly. It pulled the most relevant chunks from `09_eating_with_hands.md` and those chunks were genuinely the closest match to the query. But none of the 10 documents in the collection cover why the right hand is used specifically. There is nothing about handedness in any of the sources. So the retrieval found the best available content, the model looked at it, and correctly said there is not enough to answer. The gap is in what documents were collected, not in how they were processed.

**What would fix it:** Add a source that specifically covers the Ayurvedic or cultural reasoning behind using the right hand when eating. Something like a paper on food rituals in South Asian culture or an Ayurvedic text on the topic. That would give retrieval something to actually return.

---

## Query Interface

The interface is built with Gradio. There is a text input box where the user types a question. There is a slider to choose how many chunks to retrieve (top-k, default is 5, goes up to 10). When the user clicks Ask, two output boxes appear: one with the answer and one with the list of source filenames.

**Sample interaction:**

Input: "Why should we mix rice with ghee?"

Output (answer): "According to the context passages, we should mix rice with ghee because ghee provides the fat medium required for the absorption of fat-soluble vitamins present in the meal. (Source: 10_dal_rice_food_combining.md, passages [1] and [5])"

Output (sources): 10_dal_rice_food_combining.md

---

## Spec Reflection

**One way the spec helped during implementation:**

The chunking strategy section in planning.md was the most useful part. Before writing ingest.py, the chunk size (450 characters) and overlap (60 characters) were already decided and the reasoning was written down. So when Claude Code generated the chunking function, it was easy to check if the logic made sense. Without that, I would have just accepted whatever it produced. Having the reasoning written beforehand also made it easier to spot that the loop guard logic looked wrong, which turned out to be one of the bugs found during code review.

**One way the implementation diverged from the spec:**

The spec mentioned .txt files but all 10 sources were saved as .md files. So ingest.py had to glob *.md instead of *.txt. It is a small difference but it was not in the original plan. I noticed it only after checking the documents folder. The chunking still works the same way since the content is plain text either way.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The full planning.md file. I asked Claude Code to generate all four pipeline scripts (ingest.py, embed.py, query.py, app.py) in a subfolder called codespace, following the architecture and technical choices in the spec.
- *What it produced:* All four files in one response. The chunking logic, ChromaDB setup, Groq API call, and Gradio UI were all included. It also wrote a short README inside codespace explaining how to run things.
- *What I changed or overrode:* The spec said .txt files but my documents were .md, so I asked it to update the glob pattern in ingest.py. The chunk size was listed as "around 450" and Claude used exactly 450, which was acceptable.

**Instance 2**

- *What I gave the AI:* I asked Claude Code to review the codespace folder like a senior AI engineer would, after reading planning.md first. The goal was to check if the code matched the spec and catch any bugs.
- *What it produced:* It found 5 issues. Gradio was commented out in requirements.txt. The GROQ_API_KEY was not raising an error if missing. chromadb.Client() was deprecated. The loop guard in ingest.py could break on short texts. And retrieve() had no guard for an empty collection. It then applied all five fixes.
- *What I changed or overrode:* I checked each fix before accepting it. The chromadb change and the loop guard change I reviewed more carefully since I was not fully sure about the original behavior. Everything looked correct so all five fixes were kept.