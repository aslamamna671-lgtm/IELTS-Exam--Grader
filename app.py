import streamlit as st
import json
from groq import Groq

# ---------------------------------------------------------
# SYSTEM PROMPT (RAG-Enhanced IELTS/TOEFL/CEFR Examiner)
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are an AI IELTS/TOEFL/CEFR Writing Examiner designed to score student essays using a Retrieval-Augmented (RAG) evaluation pipeline.

Use ONLY the structured inputs provided by the application:
- Task Prompt
- Student Response
- Retrieved Model Answers (Top-K RAG Results)
- Official Rubric Descriptors
- Detected Linguistic Features
- Exam Type & Task Type

Your goals:
1. Apply the official IELTS/TOEFL/CEFR rubrics exactly.
2. Compare the student’s work with retrieved high-band model answers.
3. Provide short, clear, actionable feedback.
4. Prevent hallucination—use only the provided data.

Return your output ONLY in the following JSON structure:

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
  "actionable_feedback": [
    "...",
    "...",
    "..."
  ],
  "rag_references_used": [
    {
      "model_answer_id": "ID",
      "semantic_similarity": "0.00–1.00",
      "notes": "Which key ideas matched or mismatched"
    }
  ]
}

Rules:
- Band scores must be 0–9 in increments of 0.5.
- Justifications must be concise and rubric-aligned.
- Feedback must be short, scannable bullet points.
- Avoid repeating suggestions.
- Explain why each score was assigned.

Do not use external knowledge.
Do not assign Band 9 without strong justification.
"""


# ---------------------------------------------------------
# Streamlit UI Config
# ---------------------------------------------------------
st.set_page_config(page_title="RAG IELTS Auto-Grader", layout="wide")
st.title("📝 RAG-Based Intelligent Auto-Grader (Groq-Powered)")
st.caption("Evaluates IELTS / TOEFL / CEFR writing tasks using Groq LLM + RAG.")


# ---------------------------------------------------------
# Initialize Groq Client
# ---------------------------------------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("❌ Missing GROQ_API_KEY in Streamlit Secrets.\n\nAdd it under: Settings → Secrets")
    st.stop()


# ---------------------------------------------------------
# RAG Placeholder (Replace with vector DB later)
# ---------------------------------------------------------
def retrieve_model_answers(query):
    return [
        {
            "model_answer_id": "sample_001",
            "text": "This is a placeholder high-band model answer.",
            "similarity": 0.82
        }
    ]


# ---------------------------------------------------------
# Function to evaluate essay using Groq LLM
# ---------------------------------------------------------
def evaluate_essay(task_prompt, essay, exam_type):
    rag_results = retrieve_model_answers(essay)

    payload = {
        "task_prompt": task_prompt,
        "student_response": essay,
        "rag_model_answers": rag_results,
        "exam_type": exam_type
    }

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",  # very fast + accurate on Groq
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)}
        ]
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# Streamlit Input Fields
# ---------------------------------------------------------
exam_type = st.selectbox("Exam Type", ["IELTS Academic", "IELTS General Training", "TOEFL", "CEFR"])
task_prompt = st.text_area("Task Prompt", height=140)
essay = st.text_area("Your Essay", height=260)


# ---------------------------------------------------------
# Run Evaluation
# ---------------------------------------------------------
if st.button("Evaluate"):
    if not task_prompt or not essay:
        st.error("⚠ Please enter both the Task Prompt and your Essay before evaluating.")
    else:
        with st.spinner("Evaluating using Groq..."):
            raw_output = evaluate_essay(task_prompt, essay, exam_type)

        try:
            result = json.loads(raw_output)

            st.success("✔ Evaluation Complete")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Band Scores")
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
            st.error("⚠ The model returned non-JSON output.")
            st.code(raw_output)
groq
