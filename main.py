import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from io import BytesIO

# --- Load API Key from TOML ---
# secrets = toml.load("secrets.toml")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Topic Prompts ---
topic_prompts = {
    "Critical Reasoning": "Generate a CLAT-level critical reasoning paragraph followed by 6 questions and answers.",
    "General Knowledge": "Write a paragraph covering current affairs or static GK (suitable for CLAT/AILET) with 6 questions and answers.",
    "Legal Reasoning": "Create a legal reasoning scenario paragraph for CLAT with 6 questions testing comprehension and logic, then give answers.",
    "Mathematics": "Write a math word problem paragraph suitable for CLAT with 6 questions and detailed answers.",
    "Reading Comprehension": "Create a CLAT-level RC passage with 6 directly linked questions and their answers."
}

# --- Generate content using Gemini ---
def generate_study_material(topic, count):
    all_sections = []

    for i in range(count):
        if topic == "General Knowledge":
            # (keep the current GK prompt here — already handled)
            prompt = f"""
Generate one General Knowledge & Current Affairs passage (600–750 words) in the tone of 'The Hindu Insight' or 'Indian Express Explained'.

Start the passage with inline paragraph numbering (e.g., "1 India’s foreign policy…", "2 The changing nature…").

The passage must be neutral and explanatory, giving context/background but not directly revealing the answers to follow-up questions.

Then, generate **6 extremely difficult multiple-choice questions** numbered 1.1 to 1.6. These should:
- Be based on the theme of the passage
- Require deep factual knowledge
- NOT be directly answerable from the passage
- Include 4 options (A–D) with tricky distractors like similar names, dates, agencies, schemes, etc.

End your output with an answer key in this exact format (no explanations):

1.1 – (C)  
1.2 – (A)  
1.3 – (D)  
1.4 – (B)  
1.5 – (C)  
1.6 – (A)
"""
        
        elif topic == "Legal Reasoning":
            prompt = """
Generate 1 full-length Legal Reasoning passage (600–700 words), starting with inline numbering (e.g., "1 The doctrine of legitimate expectation...").

Tone: Analytical and scholarly — as if written by a senior law professor or Supreme Court advocate.

Content: 
- Introduce one or more legal principles
- Include definitions, rationale, conflicts, and exceptions
- Do NOT provide factual examples, illustrations, or case applications — these will be used only in the questions

Then, generate exactly 6 ultra-challenging multiple-choice questions (1.1 to 1.6) that apply the principle(s) introduced in the passage.

Each question must:
- Contain a fact scenario of at least 300 words
- Be packed with irrelevant facts, emotional/moral distractions, and layered/misleading timelines
- Test only the principle(s) from the passage — do NOT use external legal knowledge
- Use real-world language, names, and framing (e.g., protests, arrests, contracts, defamation, etc.)

**Options Format for Each Question:**
- Four answer choices: (A), (B), (C), (D)
- Exactly 2 options must say the action is *legal*, and 2 must say it is *illegal*
- Only **one** option is correct
- Distractors must be misleading but legally plausible

Ensure:
- At least **2 questions are thematically or factually linked**
- At least **1 question tests a borderline or exception case**

Finally, **only output a clean answer key** like this (no explanations):


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

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
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


