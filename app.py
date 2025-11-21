import streamlit as st
import json
from openai import OpenAI

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
4. Prevent any hallucination—use only the provided data.

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

Evaluation Logic:
1. Task Response — relevance, coverage, depth vs. model answers
2. Coherence & Cohesion — logical flow, paragraphing, cohesive devices
3. Lexical Resource — range, accuracy, collocations, repetition
4. Grammatical Range & Accuracy — variety, errors, complexity

Style:
- Friendly, clear, professional tone.
- Highlight strengths + 3–5 key improvements.
- Avoid overwhelming the user with long text.

Do not use any external knowledge.  
Do not exceed the provided information.  
Do not assign Band 9 without solid evidence.
"""

# ---------------------------------------------------------
# Streamlit UI Setup
# ---------------------------------------------------------
st.set_page_config(page_title="RAG Auto-Grader", layout="wide")
st.title("📝 RAG-Based Intelligent Auto-Grader (IELTS/TOEFL/CEFR)")
st.write("Paste your writing task and essay below to receive an AI-powered evaluation.")

# ---------------------------------------------------------
# API Setup (requires .streamlit/secrets.toml)
# ---------------------------------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------------------------------------
# Placeholder RAG Function (replace with FAISS/Chroma)
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
# Evaluation Function
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
        model="gpt-4.1",
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
exam_type = st.selectbox(
    "Exam Type:",
    ["IELTS Academic", "IELTS General Training", "TOEFL", "CEFR"]
)

task_prompt = st.text_area("Task Prompt", height=140)
essay = st.text_area("Your Essay", height=260)

# ---------------------------------------------------------
# Evaluate Button
# ---------------------------------------------------------
if st.button("Evaluate"):
    if not task_prompt or not essay:
        st.error("Please fill in both the Task Prompt and Essay fields.")
    else:
        with st.spinner("Evaluating your essay..."):
            raw_output = evaluate_essay(task_prompt, essay, exam_type)

        # Display Results
        try:
            result = json.loads(raw_output)

            st.success("Evaluation Complete ✔")

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

        except Exception as e:
            st.error("Error parsing the model's response. Raw output shown below:")
            st.code(raw_output)
            st.exception(e)
groq
