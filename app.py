import streamlit as st
import json
from groq import Groq

# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are an AI IELTS/TOEFL/CEFR Writing Examiner using a Retrieval-Augmented (RAG) evaluation pipeline.

Evaluate using ONLY:
- Task Prompt
- Student Response
- Retrieved Model Answers
- Rubric Descriptors
- Detected Linguistic Features
- Exam Type & Task Type

Return STRICT JSON:

{
  "overall_band": "X.X",
  "scores": {
    "task_response": "X.X",
    "coherence_cohesion": "X.X",
    "lexical_resource": "X.X",
    "grammatical_range_accuracy": "X.X"
  },
  "justification": {
    "task_response": "...",
    "coherence_cohesion": "...",
    "lexical_resource": "...",
    "grammatical_range_accuracy": "..."
  },
  "actionable_feedback": ["...", "...", "..."],
  "rag_references_used": [
    {"model_answer_id": "ID", "semantic_similarity": "0.00–1.00", "notes": "..."}
  ]
}

Rules:
- Band 0–9 in steps of 0.5.
- Be concise.
- Do NOT hallucinate.
- Use only provided inputs.
"""

# ---------------------------------------------------------
# Streamlit UI config
# ---------------------------------------------------------
st.set_page_config(page_title="RAG Auto-Grader (Groq)", layout="wide")
st.title("📝 RAG-Based Intelligent Auto-Grader (Groq Powered)")

# ---------------------------------------------------------
# Initialize Groq Client
# ---------------------------------------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("❌ Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# ---------------------------------------------------------
# Dummy RAG Retrieval (placeholder)
# ---------------------------------------------------------
def retrieve_model_answers(query):
    return [
        {
            "model_answer_id": "example_1",
            "text": "This is a placeholder Band 9 model answer.",
            "similarity": 0.81
        }
    ]

# ---------------------------------------------------------
# Evaluation Function (Correct Groq Format)
# ---------------------------------------------------------
def evaluate_essay(task_prompt, essay, exam_type):
    rag_results = retrieve_model_answers(essay)

    user_payload = {
        "task_prompt": task_prompt,
        "student_response": essay,
        "rag_model_answers": rag_results,
        "exam_type": exam_type
    }

    response = client.chat.completions.create(
        model="llama3-70b-8192",   # BEST model for structured output
        temperature=0,
        max_tokens=1500,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload)}
        ]
    )

    return response.choices[0].message.content

# ---------------------------------------------------------
# Streamlit Inputs
# ---------------------------------------------------------
exam_type = st.selectbox(
    "Exam Type",
    ["IELTS Academic", "IELTS General Training", "TOEFL", "CEFR"]
)

task_prompt = st.text_area("Task Prompt", height=130)
essay = st.text_area("Your Essay", height=250)

# ---------------------------------------------------------
# Run Evaluation
# ---------------------------------------------------------
if st.button("Evaluate"):
    if not task_prompt or not essay:
        st.error("⚠ Please enter both Task Prompt and Essay.")
    else:
        with st.spinner("Scoring using Groq..."):
            raw_output = evaluate_essay(task_prompt, essay, exam_type)

        try:
            result = json.loads(raw_output)

            st.success("✔ Evaluation Complete")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Scores")
                st.json(result["scores"])

            with col2:
                st.subheader("⭐ Overall Band")
                st.metric("Overall Band", result["overall_band"])

            st.subheader("📌 Justifications")
            st.json(result["justification"])

            st.subheader("🛠 Actionable Feedback")
            for fb in result["actionable_feedback"]:
                st.markdown(f"- {fb}")

            st.subheader("📚 RAG References Used")
            st.json(result["rag_references_used"])

        except Exception:
            st.error("⚠ Model did NOT return valid JSON.")
            st.code(raw_output)
groq
