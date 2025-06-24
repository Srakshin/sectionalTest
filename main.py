import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from io import BytesIO


genai.configure(api_key=st.secrets["AIzaSyBNVIZx9rtGNWdSGZNH9AJtZWhoSV5aihE"])
model = genai.GenerativeModel("gemini-2.0-flash")


topic_prompts = {
    "Critical Reasoning": "Generate a CLAT-level critical reasoning paragraph followed by 6 questions and answers.",
    "General Knowledge": "Write a paragraph covering current affairs or static GK (suitable for CLAT/AILET) with 6 questions and answers.",
    "Legal Reasoning": "Create a legal reasoning scenario paragraph for CLAT with 6 questions testing comprehension and logic, then give answers.",
    "Mathematics": "Write a math word problem paragraph suitable for CLAT with 6 questions and detailed answers.",
    "Reading Comprehension": "Create a CLAT-level RC passage with 6 directly linked questions and their answers."
}


def generate_study_material(topic, count):
    all_sections = []

    for i in range(count):
        if topic == "General Knowledge":
            # (keep the current GK prompt here — already handled)
            prompt = f"""
TONE AND STYLE:
Write in a formal, explanatory tone like a top newspaper's "Explained" section.
Contextual and background-based, not opinionated.
Do not directly state answers to any GK questions.
Paragraphs should build conceptual understanding or current relevance.
PASSAGE INSTRUCTIONS:
Start with inline numbering — not on a separate line.
Length: 600 to 750 words.
Must provide context only.
Do not include any facts that directly give away answers.
QUESTIONS (1.1 to 1.5):
Exactly 5 MCQs per passage.
Each question must be factual and verifiable.
Do not make questions directly answerable from the passage.
Allowed types:
Which of the following is true / not true
Match the following
Chronological order
Identify correct organisation/authority
Pure fact-check MCQs
QUESTION DIFFICULTY:
All questions must be difficult.
At least 3 should involve confusing or close options.
No general or guessable trivia.
OPTIONS:
4 choices: (A), (B), (C), (D)
Only one must be correct.
Distractors must be reasonable but incorrect.
Use closely related names, institutions, or events to confuse.
ANSWER KEY:
After all five questions, provide a detailed answer key.
Format:
1.1 : (C)
Then explain why (C) is correct and why the others are wrong.
FINAL STRUCTURE
GK Passage (600-750 words)
Questions 1.1 to 1.5
Answer Key with full explanations
"""
        
        elif topic == "Legal Reasoning":
            prompt = """
TONE AND VOICE:
Write in the voice of a senior law professor or Supreme Court advocate.
Keep the tone analytical, scholarly, and contemporary.
Do not include real case names or factual examples.
PASSAGE:
Begin each paragraph with inline numbering.
Length: 600 to 700 words.
Introduce one or more legal principles with definitions, rationale, conflicts, and exceptions.
Do not use any factual illustrations.
QUESTIONS (1.1 to 1.6):
Each question must have a fact scenario of at least 300 words.
Include distractions: irrelevant facts, emotional triggers, misleading timelines.
Test only the principle(s) from the passage.
No external legal knowledge should be used.
OPTIONS:
Four choices: (A), (B), (C), (D).
Exactly 2 must conclude the action is legal, and 2 illegal.
Only one option is correct.
Incorrect options must be legally plausible but flawed in logic.
SPECIAL RULES:
At least 2 questions must be thematically or factually linked.
At least 1 question must test an exception or borderline case.
ANSWER KEY:
After all six questions, provide a detailed answer key.
Format:
1.1 : (C)
Then explain why (C) is correct and why the others are wrong.
Each explanation should be 150-200 words and clearly reasoned.
STRUCTURE:
Legal Passage
Questions 1.1 to 1.6
Answer Key with full explanations
"""

        else:
            # Keep the default logic for all other topics
            prompt = f"""..."""  # Your regular passage + 6 MCQs logic

        response = model.generate_content(prompt)
        section = f"Topic: {topic}\n\n" + response.text.strip()
        all_sections.append(section)

    return all_sections





# --- Create PDFs ---
def create_pdf(contents, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use DejaVuSans from current folder
    font_path = "DejaVuSans.ttf"
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.multi_cell(0, 10, title, align='C')
    pdf.ln()

    for section in contents:
        pdf.multi_cell(0, 10, section)
        pdf.ln()

    # ✅ Use dest='S' to return content as a string
    pdf_output = pdf.output(dest='S').encode('latin1')  # Converts to bytes
    buffer = BytesIO(pdf_output)
    return buffer


# --- Streamlit UI ---
st.title("🎓 CLAT/AILET Study Material Generator")
st.write("Generate study content with paragraph, questions & answer key.")

selected_topic = st.selectbox("Choose a Topic", options=list(topic_prompts.keys()))
num_paragraphs = st.number_input("Number of Paragraphs", min_value=1, max_value=5, value=1)

if "practice_pdf" not in st.session_state:
    st.session_state.practice_pdf = None
    st.session_state.answer_pdf = None

if st.button("Generate"):
    with st.spinner("✨ Generating with Gemini..."):
        content_sections = generate_study_material(selected_topic, num_paragraphs)
        st.session_state.practice_pdf = create_pdf(content_sections, f"{selected_topic} Practice Set")
    st.success("✅ PDF Ready Below!")

if st.session_state.practice_pdf:
    st.download_button("📄 Download Study PDF",
                       data=st.session_state.practice_pdf,
                       file_name=f"{selected_topic.lower()}_clat_practice.pdf",
                       key="download_combined")


