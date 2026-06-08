"""
app.py - Gradio User Interface
Pipeline stage 4: Wrap query.py in a minimal Gradio UI.

Run:
    python app.py
    # or
    gradio app.py
"""

import gradio as gr
from query import ask


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def format_sources(sources: list[str]) -> str:
    if not sources:
        return "No sources retrieved."
    return "\n".join(f"• {s}" for s in sources)


def handle_question(question: str, top_k: int) -> tuple[str, str]:
    """Called by Gradio on every submission."""
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    result = ask(question, k=int(top_k))
    answer = result["answer"]
    sources = format_sources(result["sources"])
    return answer, sources


# ---------------------------------------------------------------------------
# Gradio layout
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="The Unofficial Guide — Indian Food & Health Science",
    theme=gr.themes.Soft(),
) as demo:

    gr.Markdown(
        """
        # 🌿 The Unofficial Guide
        ### Scientific & ecological reasoning behind traditional Indian food and health practices
        Ask a question grounded in research — the system retrieves relevant passages
        from academic sources and generates a cited, evidence-based answer.
        """
    )

    with gr.Row():
        with gr.Column(scale=4):
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. Why is turmeric anti-inflammatory? Why do we store water in copper vessels?",
                lines=2,
            )
        with gr.Column(scale=1):
            top_k_slider = gr.Slider(
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                label="Chunks retrieved (top-k)",
            )

    ask_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            answer_box = gr.Textbox(
                label="Answer",
                lines=10,
                interactive=False,
            )
        with gr.Column(scale=1):
            sources_box = gr.Textbox(
                label="Sources",
                lines=10,
                interactive=False,
            )

    # Example questions from evaluation plan
    gr.Examples(
        examples=[
            ["What does the research say about curcumin's effect on inflammation?"],
            ["Why does storing water in copper vessels have health benefits?"],
            ["What is the nutritional reason dal and rice are traditionally eaten together?"],
            ["What happens metabolically during Ekadashi or similar Indian fasting practices?"],
            ["What is Ritucharya and why does Ayurveda recommend seasonal eating?"],
        ],
        inputs=question_box,
        label="Try an evaluation question",
    )

    # Wire up button and Enter key
    ask_btn.click(
        fn=handle_question,
        inputs=[question_box, top_k_slider],
        outputs=[answer_box, sources_box],
    )
    question_box.submit(
        fn=handle_question,
        inputs=[question_box, top_k_slider],
        outputs=[answer_box, sources_box],
    )

    gr.Markdown(
        """
        ---
        *Answers are generated from retrieved document passages only.
        The model is instructed not to answer beyond what the sources contain.*
        """
    )


if __name__ == "__main__":
    demo.launch(share=False)
