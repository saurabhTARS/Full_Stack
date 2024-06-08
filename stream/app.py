import streamlit as st
import docx2txt
import PyPDF2
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from docx import Document

# Replace with your actual OpenAI API key
api_key = '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'

model = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
parser = StrOutputParser()

section_prompts = {
    "Profile Summary": "Write a professional profile summary based on the given content:",
    "Skills": "List the skills mentioned in the resume:",
    "Experience": "Provide a brief description of the work experience:",
    "Projects": "Summarize the projects mentioned in the resume:"
}

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def reformat_resume_with_gpt(resume_text):
    system_message = SystemMessage(content="You are a professional resume formatter.")
    human_message = HumanMessage(content=f"Extract sections like Profile Summary, Skills, Experience, Projects:\n\n{resume_text}")
    
    response = model.invoke([system_message, human_message])
    return response.content.strip()

def extract_sections(resume_text):
    sections = {}
    for section_name, prompt in section_prompts.items():
        system_message = SystemMessage(content=f"You are an AI model for resume section extraction. {prompt}")
        human_message = HumanMessage(content=resume_text)
        
        response = model.invoke([system_message, human_message])
        
        sections[section_name] = response.content.strip()
    
    return sections

def display_sections(sections):
    for section_name, section_content in sections.items():
        st.text_area(label=f"Your Generated {section_name}", max_chars=500, placeholder=section_name, height=200, value=section_content)


def upload():
    with st.spinner("Fetching from GPT") :
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
        if uploaded_file is not None:
            st.success("File uploaded successfully")
            
            if uploaded_file.type == "application/pdf":
                resume_content = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_content = extract_text_from_docx(uploaded_file)
            
            system_template = '''
                                Given a resume extract the sections from the resume as per the list in a dictionary
                                1.Name
                                2.Title line if there is no title line ignore take none
                                3.Contact details have mail id, mobile number, any , media links like github, linkedin, medium etc. 
                                4.Profile summary
                                5.Skill set
                                6.Work experience
                                7.Education
                                8.Projects
                                9.Certifications
                                10.Hobbies
                                11.Papers published
                            '''
            
            prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{resume_content}")])
            chain = prompt_template | model | parser
            resume_sections = chain.invoke({"resume_content": resume_content})

            st.session_state.resume_sections = resume_sections  # Save resume sections in session state
            st.session_state.page = "upload_jd_file"  # Set the page state to "upload_jd_file"

            st.experimental_rerun()  # Trigger a rerun to update the page state

def upload_jd_file():
    st.text_area(label="Attach JD", max_chars=3000, placeholder="Attach JD.", height=None, value="", key="unique_key_for_text_area")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"], key="unique_key_for_uploader")
    if uploaded_file is not None:
        st.success("JD uploaded successfully")
        st.write('JD uploaded successfully')
        
        if uploaded_file.type == "application/pdf":
            jd_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            jd_text = extract_text_from_docx(uploaded_file)
        
        job_summary(st.session_state.resume_sections, jd_text)

def job_summary(resume_sections, job_description):
    system_template = '''
                        Give me a summary about the job description and the summary must contain
                        1. Job title 
                        2. company name
                        3. Job type remote or on-site or contract or permanent 
                        3. experience expected
                        4. Location
                        5. Responsibilities 
                        6. skill set required
                        7. Tools required 
                        8. Benefits
                        9. Interview process include any other required. 
                        and finally Keywords 
                      '''
    
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{job_description}")])
    chain = prompt_template | model | parser
    job_description = chain.invoke({"job_description": job_description})

    system_template = '''
                        Keywords: gather as many keywords and keyphrases as possible and Store the keywords in a dictionary with values
                        skills, tools, others
                        1. terms or phrases of the skills mentioned hardskils, soft skills
                        2. tools mentioned in the JD
                        3. Abilities, Tasks, proverbs, verbs, adjectives or phrases used to describe things
                        and also give me a count of the keywords and keyphrases identified
                      '''
    
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{job_description}")])
    chain = prompt_template | model | parser
    key_words = chain.invoke({"job_description": job_description})

    system_template = '''
                        Role: Act as an expert resume building assistant for an experienced employee. 
                        Task: Rewrite the given resume using the keywords and keyphrases provided in the keywords.
                        Instructions: 
                        common instruction - Rewrite each section by including the keywords in key_words try to repeat the important keywords twice in the document as per context. 
                        Name - Include the name as it is 
                        Title line - include professional title and describe using experience, skills set or achievements, passion relevant to the keywords in a single line not more than ten words. 
                        Contact details - include contact details as it is in a single line separated by "|". 
                        Profile Summary - Rewrite by including the keywords and key_phrases in key_words with professional title with a powerful adjective, skills, contribution in projects, achievements and why applying for the job. 
                        Skill set - Rewrite all skills by including the keywords and key_phrases in key_words which are relevant and skills mentioned in resume and  not include all only the best suiting skills. 
                        Experience - Rewrite by including the keywords in key_words and key_phrases within the content of the experience section of the resume by including skills and abilities showcased and impact created 
                        Projects - Rewrite by including the keywords in key_words and key_phrases within the content the projects by including skills, tasks, abilities mentioned in the keywords and resume content and also write about the impact it has created. 
                        Education - Keep education details as it is. if possible mentions relevant skills under each education within one line. 
                        regenerate the resume in the same format and order. 
                      '''
    
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{resume_sections} and {key_words}")])
    chain = prompt_template | model | parser
    new_resume = chain.invoke({"resume_sections": resume_sections, "key_words": key_words})

    system_template = f"""
                        format the resume content in to a well structured resume and return a docx document. 
                        """

    prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", "{new_resume}")])
    chain = prompt_template | model | parser
    new_resume = chain.invoke({"new_resume": new_resume})
    # print(new_resume)

    st.write(new_resume)
    # st.download_button("Download as PDF", data=generate_pdf(new_resume), file_name="new_resume.pdf", mime="application/pdf")
    st.download_button("Download as DOCX", data=generate_docx(new_resume), file_name="new_resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


def generate_pdf(content):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    lines = content.split('\n')
    x = inch
    y = height - inch

    for line in lines:
        wrapped_lines = split_line_to_fit_width(line, width - 2 * inch, p)
        for wrapped_line in wrapped_lines:
            if y <= inch:
                p.showPage()
                y = height - inch
            p.drawString(x, y, wrapped_line)
            y -= 14

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def split_line_to_fit_width(line, max_width, canvas):
    words = line.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if canvas.stringWidth(test_line) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def generate_docx(content):
    doc = Document()
    lines = content.split('\n')

    for line in lines:
        doc.add_paragraph(line)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(layout="wide")
# st.title("ResumaGAIN", 
#          # Apply CSS style for center alignment
#          style="text-align: center;")

st.markdown("<h1 style='text-align: center;'>ResumaGAIN</h1>", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'default'

st.markdown("""
    Introducing our cutting-edge resume customization application powered by state-of-the-art Language Models (LLMs). 
    Say goodbye to generic resumes that get lost in the Applicant Tracking System (ATS) abyss. Our innovative tool revolutionizes 
    the job application process by seamlessly tailoring resumes to match specific job descriptions. Simply upload your resume 
    and the job description, and watch as our LLMs work their magic to optimize your resume for the highest ATS ranking. 
    With our application, you'll stand out to recruiters and increase your chances of landing interviews. 
    Say hello to personalized career success!
""")

# col1, col2 = st.columns(2)

st.markdown("""
    <style>
        .stButton button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)


upload_button = st.button("Upload")


if upload_button:
    st.session_state.page = "upload"

if st.session_state.page == 'upload':
    upload()
elif st.session_state.page == 'upload_jd_file':
    upload_jd_file()

percentage = 75

st.markdown("""
    <style>
        .progress-text {
            text-align: center;
            color: white;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

