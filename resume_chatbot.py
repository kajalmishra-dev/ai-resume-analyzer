import os
import re
import fitz  # PyMuPDF
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

st.sidebar.header("🔐 OpenAI API Key")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

if not openai_api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

os.environ["OPENAI_API_KEY"] = openai_api_key

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    return text

def build_vectorstore(text):
    splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    texts = splitter.split_text(text)
    docs = [Document(page_content=t) for t in texts]
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(docs, embedding=embeddings)
    return vectordb

def create_chatbot_chain(vectordb):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0)
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)

def score_resume_match(resume_text, job_description):
    llm = ChatOpenAI(temperature=0)
    prompt_template = """
Compare the following resume and job description.

Resume:
{resume_text}

Job Description:
{job_description}

Give a match percentage (0–100%) and explain why, listing matching skills and any gaps.
Respond with:
- Match %: ...
- Matched Skills: ...
- Missing Skills: ...
- Summary: ...
"""
    prompt = PromptTemplate(
        input_variables=["resume_text", "job_description"],
        template=prompt_template
    )
    formatted_prompt = prompt.format(resume_text=resume_text, job_description=job_description)
    response = llm.call_as_llm(formatted_prompt)
    return response

st.set_page_config(page_title="Smart Resume Chatbot", layout="wide")
st.title("🤖 Chat with Your Resume + Job Fit Analysis")

uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type="pdf")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    resume_text = extract_text_from_pdf(pdf_bytes)
    vectordb = build_vectorstore(resume_text)
    chatbot_chain = create_chatbot_chain(vectordb)
    st.success("✅ Resume processed!")

    tab1, tab2 = st.tabs(["💬 Chat with Resume", "📄 Job Match Dashboard"])

    with tab1:
        user_question = st.text_input("Ask a question about your resume:")
        if user_question:
            response = chatbot_chain.run(user_question)
            st.markdown(f"**AI:** {response}")

    with tab2:
        st.subheader("🔎 Paste a Job Description Below")
        job_desc = st.text_area("Job Description", height=200)

        if job_desc:
            with st.spinner("Analyzing match..."):
                result = score_resume_match(resume_text, job_desc)

            match_pct = re.search(r"Match %: (\d+)", result)
            percent = int(match_pct.group(1)) if match_pct else 0

            matched = re.search(r"Matched Skills: (.+)", result)
            missing = re.search(r"Missing Skills: (.+)", result)
            summary = re.search(r"Summary: (.+)", result)

            st.subheader("📊 Match Score")
            st.progress(percent / 100)
            st.metric("Match %", f"{percent}%")

            st.subheader("✅ Matched Skills")
            st.write(matched.group(1) if matched else "Not found")

            st.subheader("❌ Missing Skills")
            st.write(missing.group(1) if missing else "None")

            st.subheader("🧠 Summary")
            st.write(summary.group(1) if summary else "Not available")