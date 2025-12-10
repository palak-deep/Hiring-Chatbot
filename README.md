🤖 TalentScout AI – Intelligent Technical Hiring Assistant

TalentScout AI is an interactive, AI-powered technical assessment tool built with Streamlit and Groq LLMs.
It automates the technical screening process by generating MCQs based on a candidate’s tech stack and evaluating their responses instantly.

🚀 Features
🔍 Candidate Information Collection

Collects essential candidate details:

Full Name

Email, Phone

Years of Experience

Desired Role

Location

Technical Stack

🧠 AI-Generated Technical MCQs

Automatically generates 5 tailored MCQs using Groq Llama & Gemma models based on the candidate’s tech stack.

📝 Dynamic MCQ Parsing

Extracts questions, options, and correct answers using regex

Ensures consistent MCQ formatting

⭐ Interactive Assessment

User selects answers inside Streamlit

Highlights correct and incorrect answers

Scoring system (10 points per question)

Final score out of 50 with percentage

📊 Result Evaluation

Clean score breakdown

Correct-option highlighting

Progress bar showing percentage

Option to retake test or submit application

🛠️ Debug Mode

Shows raw API responses for debugging purposes.

🔄 Reset Anytime

Restart the full assessment workflow with one click.

🧰 Tech Stack

Python 3.10+

Streamlit

Groq API (Llama & Gemma models)

dotenv

Regex

OS / Session State

🧪 Groq Models Used
Model Name	Description
llama-3.3-70b-versatile	High-quality MCQ generation
llama-3.1-8b-instant	Fast and lightweight
gemma2-9b-it	Google Gemma 2 instruction model
📦 Installation
1️⃣ Clone the Repository

Use these commands in your Command Line / Terminal:

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Set Environment Variables

Create a .env file in your project directory:

GROQ_API_KEY=your_api_key_here

▶️ Run the Application
streamlit run app.py


Replace app.py with your main Streamlit file if different.

📂 Project Structure                                                                                                        
📁 TalentScout-AI                                                             
 ├── app.py                # Main Streamlit application                                                    
 ├── prompt_templates.py   # Template logic for MCQ generation                                                                         
 ├── requirements.txt      # Python dependencies                                                                            
 ├── .env                  # API keys (excluded from repo)                                                                                   
 ├── README.md             # Project documentation                                                                                                                      


🤝 Contributing

Contributions are welcome!
Open an issue to discuss improvements or submit a pull request.
