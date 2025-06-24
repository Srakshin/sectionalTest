import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from io import BytesIO


genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
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
    
        elif topic == "Critical Reasoning":
            prompt = """
TONE AND STYLE:
Write in the style of a university-level logic instructor or a professional critical thinking textbook.
Tone should be clear, analytical, and slightly academic — never casual or oversimplified.
Avoid storytelling tone or emotional language.
Focus on logical reasoning and argument structures, not opinions.

PASSAGE FORMAT:
Begin with inline paragraph numbering (e.g., 1, 2, 3…).
Length: 500–600 words.
The passage must contain **one or more arguments** (claim + support), embedded in a formal discussion or analysis.
Use abstract or general topics like ethics, technology, law, economy, governance, etc.
Clearly highlight assumptions, logical structure, and potential flaws in reasoning.
Passage **must not give away answers** to any questions.
Do not explain the correct reasoning explicitly — leave room for inference.

QUESTIONS (1.1 to 1.5):
Exactly **5 MCQs** per passage.
Each question must test **core logical reasoning skills**, such as:
- Identifying assumptions
- Evaluating argument strength
- Identifying flaws in reasoning
- Drawing inferences
- Strengthening or weakening arguments
Each question must be **based on the passage** and only test logical reasoning — not facts or prior knowledge.
Include **at least 2 questions** that are deceptively tricky (with tempting but incorrect options).
Each question must be **self-contained** — do not refer to other questions.

OPTIONS:
Four choices: (A), (B), (C), (D).
Only one correct.
Other three must be plausible but logically incorrect or flawed.

ANSWER KEY:
After all questions, provide a detailed answer key.
Format:
1.1 : (B)
Then give a **150-word explanation** for why (B) is correct and **why each of the others is wrong**.
Use logic-based reasoning — avoid factual justifications.

STRUCTURE:
Critical Reasoning Passage  
Questions 1.1 to 1.5  
Answer Key with full logic-based explanations  

"""
        elif topic == "Mathematics":
            prompt = """
TONE AND STYLE:
Use a clear, neutral, formal tone — like a government aptitude booklet or official exam paper.
Avoid storytelling or casual phrasing.
Use straightforward mathematical language and structured presentation.

PASSAGE FORMAT:
Create a **data-based scenario** or **numerical information set** (like a graph/table/paragraph).
Begin with inline numbering (1, 2, etc.).
Use **paragraph-style presentation of numerical data**, not actual graphs/tables.
Length: 120 to 150 words.
Present a real-world context (e.g., survey data, business profits, school marks, voter stats, etc.).
Include **numerical values, percentages, ratios, fractions, or trends** that are needed for calculation.
Do NOT include any analysis or calculation in the passage.
The data should be **enough to derive answers**, but never directly point to them.

QUESTIONS (1.1 to 1.5):
Generate **exactly 5 MCQs** based on the numerical data in the passage.
Each question should require basic to moderate-level calculations involving:
- Percentages / Ratios / Averages
- Profit & Loss / SI & CI
- Time, Speed & Distance
- Logical deduction / Comparative Analysis
Do NOT give away any answers or hints in the questions.
Use data only from the passage — no external numbers.
At least 2 questions should involve multi-step calculations or data comparison.
Ensure 1 question tests approximation or estimation logic.

OPTIONS:
Exactly 4 choices per question: (A), (B), (C), (D).
Only one must be correct.
Others should be close (plausible miscalculations or distractions).
Ensure numerical traps (e.g., rounding errors, swapped ratio terms, wrong base values).

ANSWER KEY:
After all 5 questions, provide a full answer key:
Format:
1.1 : (D)
Then give **concise but clear working**, including:
- Step-by-step calculation (use math notation)
- Final answer with brief justification
- Also explain why other options are incorrect

STRUCTURE:
Mathematics Data Passage  
Questions 1.1 to 1.5  
Answer Key with full working and explanations  

"""
        elif topic == "Mathematics":
            prompt = """
TONE AND STYLE:
Adopt the tone of a long-form editorial, journalistic article, or published essay.
Use formal, context-rich, and intellectual language — as found in The Hindu, The Indian Express (Explained), or Scroll.in.
Avoid emotional or sensational writing.
Maintain neutrality and depth.
Passage should be **conceptual, abstract, or issue-based** — not factual news reporting.

PASSAGE FORMAT:
Begin each paragraph with inline numbering (1, 2, etc.).
Length: 500–600 words.
Choose one central theme from contemporary issues like:
- Democracy & governance
- Technology & society
- Economics & inequality
- Ethics & environment
- Identity, media, justice, liberty
Build a layered argument or reflection — NOT just a narrative.
Include:
- Subtle argumentation
- Shifts in tone or contrast
- Implied assumptions
- Contextual complexity
Avoid facts that make answers obvious.
**Do not give definitions** or summaries that give away answers.
Passage must be logically structured but open to interpretation.

QUESTIONS (1.1 to 1.5):
Generate **exactly 5 MCQs** that test:
- Author's main point / thesis
- Tone and attitude
- Inference from given statements
- Logical structure or flow of ideas
- Assumptions / contradictions / implications
Avoid vocabulary, dates, or factual recall.
Each question must require reasoning — not surface-level reading.
Use **distractors** that are partially true or misinterpret the argument.
At least 3 questions must have **close options**.

OPTIONS:
Each question must have 4 options: (A), (B), (C), (D).
Only one correct.
Others must be **plausible but logically flawed**.
Avoid obviously wrong or silly choices.

ANSWER KEY:
After all five questions, provide a detailed answer key:
Format:
1.1 : (B)
Then explain:
- Why (B) is correct with passage reference
- Why (A), (C), (D) are incorrect — explain the trap or flaw in reasoning

Each explanation should be **100–150 words**, written in a formal academic tone.

STRUCTURE:
Reading Comprehension Passage  
Questions 1.1 to 1.5  
Answer Key with detailed explanations  

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
    pdf_output = pdf.output(dest='S')  # Converts to bytes
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


