import streamlit as st
import openai
from PyPDF2 import PdfReader

# Set your OpenAI API key directly here
openai.api_key = "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"
client = openai.Client(api_key=openai.api_key)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_question(resume_content, previous_questions, previous_responses):
    qa_history = ""
    if previous_questions:
        for q, r in zip(previous_questions, previous_responses):
            qa_history += f"\nQ: {q}\nA: {r}"
    
    prompt = f"""Based on the following resume content and previous Q&A, please ask a NEW and DIFFERENT question to evaluate if they have traits to become a millionaire. Be concise.
    
Resume content: {resume_content}

Previous Q&A: {qa_history}

Important: Please ask a completely different question that explores a new aspect of their potential to become a millionaire."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI asking personalized questions based on the resume to determine if someone is likely to become a millionaire. Each question must be different from previous ones and explore different aspects of the person's potential."},
                {"role": "user", "content": prompt},
            ]
        )
        question = response.choices[0].message.content.strip()
        return question
    except Exception as e:
        return f"Error generating question: {str(e)}"

def determine_likelihood(resume_content, questions, responses):
    # Format the Q&A history for better clarity
    qa_history = "\n".join([f"Q: {q}\nA: {r}" for q, r in zip(questions, responses)])
    
    # Updated prompt to explicitly ask the model to consider both resume and responses
    prompt = f"""
    Based on the following resume content and Q&A history, analyze the likelihood of the user becoming a millionaire within the next 5 years. Please provide a detailed analysis that carefully examines both the resume content and the user's responses in the Q&A.

    Resume Content:
    {resume_content}

    Q&A History:
    {qa_history}

    Please consider how the user's experience, skills, mindset, and answers to the questions indicate their potential to become a millionaire. Be concise.
    """
    
    try:
        # Using GPT-4 for more detailed analysis
        response = client.chat.completions.create(
            model="gpt-4",  # Switch to GPT-4 for better handling of complex tasks
            messages=[
                {"role": "system", "content": "You are an AI tasked with evaluating the likelihood of someone becoming a millionaire. Analyze their resume and Q&A responses to make a comprehensive assessment."},
                {"role": "user", "content": prompt},
            ]
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        return f"Error determining likelihood: {str(e)}"

# Streamlit app
st.title("Can you become a Millionaire in the next 5 years?")

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = ''
if 'result' not in st.session_state:
    st.session_state.result = ''
if 'is_result' not in st.session_state:
    st.session_state.is_result = False
if 'resume_content' not in st.session_state:
    st.session_state.resume_content = ''
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# File upload section
uploaded_file = st.file_uploader("Upload your resume file (PDF)", type=['pdf'])

# Handle file upload and initial question
if uploaded_file is not None:
    try:
        # Process the file if it's new or we're starting over
        if not st.session_state.resume_content:
            st.session_state.resume_content = extract_text_from_pdf(uploaded_file)
            truncated_content = st.session_state.resume_content[:10000]

            # Generate first question
            if st.session_state.question_count == 0:
                st.session_state.current_question = generate_question(
                    truncated_content,
                    st.session_state.questions,
                    st.session_state.responses
                )
                st.session_state.question_count = 1

        # Display current question and response form
        if not st.session_state.is_result:
            st.write(f"Question {st.session_state.question_count} of 4:")
            st.write(st.session_state.current_question)
            
            # Create form for response
            with st.form(key=f'question_form_{st.session_state.question_count}'):
                response_input = st.text_input("Your Response:")
                submit_button = st.form_submit_button("Submit Response")
                
                if submit_button and response_input.strip():
                    # Store current Q&A
                    st.session_state.questions.append(st.session_state.current_question)
                    st.session_state.responses.append(response_input)
                    
                    if st.session_state.question_count >= 4:
                        # Final analysis
                        with st.spinner("Analyzing your responses..."):
                            st.session_state.result = determine_likelihood(
                                st.session_state.resume_content,
                                st.session_state.questions,
                                st.session_state.responses
                            )
                            st.session_state.is_result = True
                    else:
                        # Generate next question
                        with st.spinner("Generating next question..."):
                            next_question = generate_question(
                                st.session_state.resume_content,
                                st.session_state.questions,
                                st.session_state.responses
                            )
                            st.session_state.current_question = next_question
                            st.session_state.question_count += 1
                    
                    st.rerun()  # Updated line
                elif submit_button and not response_input.strip():
                    st.error("Please provide a response before submitting.")

    except Exception as e:
        st.error(f"An error occurred while processing your resume: {str(e)}")

# Display result if complete
if st.session_state.is_result:
    st.write("Your Analysis:")
    st.write(st.session_state.result)
    if st.button("Start Over"):
        # Reset all session state variables
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()  # Updated line

# Display progress
if st.session_state.questions:
    st.write("---")
    st.write("Previous Questions and Responses:")
    for i, (q, r) in enumerate(zip(st.session_state.questions, st.session_state.responses)):
        st.write(f"Q{i+1}: {q}")
        st.write(f"A{i+1}: {r}")
        st.write("---")
