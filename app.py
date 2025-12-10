import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import re

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Check if API key exists
if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found in .env file!")
    st.stop()

client = Groq(api_key=groq_api_key)

# Streamlit settings
st.set_page_config(page_title="TalentScout AI", layout="centered")

# Initialize session state
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "submitted_answers" not in st.session_state:
    st.session_state.submitted_answers = False

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

if "raw_questions" not in st.session_state:
    st.session_state.raw_questions = ""

# Available Groq models (updated December 2024)
AVAILABLE_MODELS = {
    "Llama 3.3 70B (Recommended)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
    "Gemma 2 9B": "gemma2-9b-it",
}

# Helper function to generate prompt
def generate_technical_questions_prompt(tech_stack):
    return f"""Generate exactly 5 multiple choice technical questions about: {tech_stack}

CRITICAL: Follow this EXACT format with no deviations:

Q1. What is the primary use of Python?
a) Only web development
b) Only data science
c) Multiple purposes including web, data science, automation
d) Only game development
Answer: c

Q2. Which framework is used for building user interfaces in JavaScript?
a) Django
b) React
c) Flask
d) Spring
Answer: b

Q3. [Continue with same format]
a) [Option A]
b) [Option B]
c) [Option C]
d) [Option D]
Answer: [a/b/c/d]

Continue for Q4 and Q5. Each question must have exactly 4 options (a, b, c, d) and one correct answer."""

# Groq call function with error handling
def ask_groq(prompt, model="llama-3.3-70b-versatile"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical interviewer. Generate MCQ questions in the EXACT format specified. Do not add any extra text before or after the questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# Improved MCQ parser
def parse_mcq_questions(raw_text):
    if not raw_text:
        return []
    
    questions = []
    
    # Split by question numbers
    question_blocks = re.split(r'\n(?=Q\d+\.)', raw_text.strip())
    
    for block in question_blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split('\n')
        current = {"question": "", "options": [], "answer": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match question
            q_match = re.match(r'^Q\d+\.\s*(.+)', line)
            if q_match:
                current["question"] = q_match.group(1).strip()
                continue
            
            # Match options
            opt_match = re.match(r'^([a-dA-D])\)\s*(.+)', line)
            if opt_match:
                letter = opt_match.group(1).lower()
                text = opt_match.group(2).strip()
                current["options"].append({"letter": letter, "text": text})
                continue
            
            # Match answer
            ans_match = re.match(r'^Answer\s*:?\s*([a-dA-D])', line, re.IGNORECASE)
            if ans_match:
                current["answer"] = ans_match.group(1).lower()
                continue
        
        # Validate question before adding
        if current["question"] and len(current["options"]) == 4 and current["answer"]:
            questions.append(current)
    
    return questions

# Reset function
def reset_app():
    st.session_state.candidate_data = {}
    st.session_state.questions = []
    st.session_state.answers = {}
    st.session_state.submitted_answers = False
    st.session_state.raw_questions = ""

# UI
st.title("🤖 TalentScout AI")
st.markdown("Welcome to TalentScout! I'm your AI hiring assistant for technical screening.")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection
    selected_model_name = st.selectbox(
        "AI Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=0
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]
    
    st.markdown("---")
    
    if st.button("🔄 Start Over", use_container_width=True):
        reset_app()
        st.rerun()
    
    st.markdown("---")
    st.session_state.debug_mode = st.checkbox("🐛 Debug Mode", value=st.session_state.debug_mode)
    
    if st.session_state.debug_mode:
        st.info("Debug mode: Shows raw API responses")
    
    st.markdown("---")
    st.caption(f"Model: `{selected_model}`")

# Candidate form
if not st.session_state.candidate_data:
    st.subheader("📋 Candidate Information")
    
    with st.form("candidate_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email Address *", placeholder="john@example.com")
            phone = st.text_input("Phone Number *", placeholder="+1234567890")
        
        with col2:
            experience = st.number_input("Years of Experience *", min_value=0, max_value=50, step=1)
            role = st.text_input("Desired Position *", placeholder="Full Stack Developer")
            location = st.text_input("Location", placeholder="New York, USA")
        
        tech_stack = st.text_area(
            "Tech Stack * (Comma-separated)", 
            placeholder="Python, JavaScript, React, Node.js, PostgreSQL, Docker",
            help="List the technologies you're proficient in"
        )

        submitted = st.form_submit_button("✅ Submit & Generate Questions", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([name, email, phone, role, tech_stack]):
                st.error("❌ Please fill all required fields marked with *")
            elif "@" not in email or "." not in email:
                st.error("❌ Please enter a valid email address")
            else:
                st.session_state.candidate_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "experience": experience,
                    "role": role,
                    "location": location,
                    "tech_stack": tech_stack
                }
                st.success("✅ Info submitted! Generating questions...")
                st.rerun()

# Generate technical MCQs
if st.session_state.candidate_data and not st.session_state.questions:
    st.info(f"👋 Hello **{st.session_state.candidate_data['name']}**! Generating questions for: **{st.session_state.candidate_data['tech_stack']}**")
    
    with st.spinner("🔄 Generating technical questions... This may take 10-20 seconds..."):
        tech_stack = st.session_state.candidate_data["tech_stack"]
        prompt = generate_technical_questions_prompt(tech_stack)
        
        questions_raw = ask_groq(prompt, model=selected_model)
        
        if questions_raw:
            st.session_state.raw_questions = questions_raw
            
            # Debug mode: Show raw response
            if st.session_state.debug_mode:
                with st.expander("🐛 Raw API Response"):
                    st.code(questions_raw)
            
            parsed_mcqs = parse_mcq_questions(questions_raw)
            
            if parsed_mcqs and len(parsed_mcqs) >= 3:  # At least 3 questions
                st.session_state.questions = parsed_mcqs
                st.success(f"✅ Generated {len(parsed_mcqs)} questions successfully!")
                st.rerun()
            else:
                st.error(f"❌ Failed to parse questions properly. Only parsed {len(parsed_mcqs)} valid questions.")
                
                # Show what went wrong
                with st.expander("🔍 Debugging Information"):
                    st.markdown("**Raw Response:**")
                    st.code(questions_raw)
                    st.markdown("**Parsed Questions:**")
                    st.json(parsed_mcqs)
                    st.markdown("**Expected Format:**")
                    st.code("""Q1. Your question here?
a) Option A
b) Option B
c) Option C
d) Option D
Answer: c""")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Retry Generation", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("⬅️ Go Back to Form", use_container_width=True):
                        reset_app()
                        st.rerun()
        else:
            st.error("❌ Failed to connect to Groq API. Please check your API key and internet connection.")
            
            if st.button("🔄 Retry"):
                st.rerun()

# MCQ answer form
if st.session_state.questions and not st.session_state.submitted_answers:
    st.subheader("🧠 Technical Assessment")
    st.info(f"📝 Answer **{len(st.session_state.questions)}** questions below. Each correct answer = **10 points**")
    
    with st.form("answers_form"):
        for i, item in enumerate(st.session_state.questions):
            st.markdown(f"### Question {i+1}")
            st.write(f"**{item['question']}**")
            st.markdown("")
            
            # Create options for radio button
            options = [f"{opt['letter']}) {opt['text']}" for opt in item['options']]
            
            selected = st.radio(
                f"Your answer:",
                options=options,
                key=f"answer_q{i+1}",
                index=None
            )
            
            if selected:
                selected_letter = selected.split(')')[0].strip()
                st.session_state.answers[f"q{i+1}"] = selected_letter
            
            st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submit_answers = st.form_submit_button("📤 Submit All Answers", use_container_width=True)
        with col2:
            if st.form_submit_button("🔙 Back", use_container_width=True):
                reset_app()
                st.rerun()
        
        if submit_answers:
            if len(st.session_state.answers) < len(st.session_state.questions):
                st.error(f"❌ Please answer all questions! You've answered {len(st.session_state.answers)}/{len(st.session_state.questions)}")
            else:
                st.session_state.submitted_answers = True
                st.rerun()

# Evaluation results
if st.session_state.submitted_answers:
    st.subheader("📊 Assessment Results")
    
    candidate_name = st.session_state.candidate_data.get("name", "Candidate")
    st.markdown(f"**Candidate:** {candidate_name}")
    st.markdown(f"**Tech Stack:** {st.session_state.candidate_data.get('tech_stack', 'N/A')}")
    st.markdown("---")
    
    total_score = 0
    max_score = len(st.session_state.questions) * 10
    
    for i, item in enumerate(st.session_state.questions):
        user_ans = st.session_state.answers.get(f"q{i+1}", "").lower()
        correct_ans = item["answer"].lower()
        is_correct = user_ans == correct_ans
        
        # Display question
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### Q{i+1}: {item['question']}")
        with col2:
            if is_correct:
                st.success("✅ +10")
            else:
                st.error("❌ 0")
        
        # Display options with highlighting
        for opt in item["options"]:
            opt_letter = opt["letter"]
            opt_text = opt["text"]
            
            if opt_letter == user_ans and is_correct:
                st.success(f"**{opt_letter}) {opt_text}** ← Your answer (Correct! ✅)")
            elif opt_letter == user_ans and not is_correct:
                st.error(f"**{opt_letter}) {opt_text}** ← Your answer (Incorrect ❌)")
            elif opt_letter == correct_ans:
                st.info(f"**{opt_letter}) {opt_text}** ← Correct answer ✓")
            else:
                st.write(f"{opt_letter}) {opt_text}")
        
        score = 10 if is_correct else 0
        total_score += score
        st.markdown("---")

    # Final score with color coding
    percentage = (total_score / max_score) * 100
    
    st.markdown(f"## 🏆 Final Score: **{total_score}/{max_score}** ({percentage:.1f}%)")
    
    # Progress bar
    st.progress(percentage / 100)
    
    if percentage >= 80:
        st.success("🎉 **Excellent!** You've demonstrated strong technical knowledge.")
    elif percentage >= 60:
        st.info("👍 **Good job!** You have a solid foundation.")
    elif percentage >= 40:
        st.warning("📚 **Fair performance.** Consider reviewing the topics covered.")
    else:
        st.error("💪 **Keep learning!** There's room for improvement.")
    
    st.markdown("---")
    st.markdown("### 📧 Next Steps")
    st.write("Our team will review your application and assessment results.")
    st.write("**Expected timeline:** 3-5 business days")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit Final Application", use_container_width=True):
            st.balloons()
            st.success("🎊 Application submitted successfully! Check your email for confirmation.")
    with col2:
        if st.button("🔄 Take Another Assessment", use_container_width=True):
            reset_app()
            st.rerun()