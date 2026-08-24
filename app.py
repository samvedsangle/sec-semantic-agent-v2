import os
from pathlib import Path

import streamlit as st
from langchain_classic.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

st.set_page_config(
    page_title="SEC 10-K Semantic Auditor",
    page_icon="📊",
    layout="wide",
)
st.title("SEC 10-K Semantic Auditor")
st.caption("Local document embeddings with Gemini-powered financial risk analysis")

PROJECT_DIR = Path(__file__).resolve().parent
VECTORSTORE_DIR = PROJECT_DIR / "chroma_db_clean"

api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
if not api_key:
    api_key = st.sidebar.text_input("Google Gemini API key", type="password")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key


@st.cache_resource
def initialize_rag_pipeline():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not set. Export it before starting Streamlit.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=str(VECTORSTORE_DIR),
        embedding_function=embeddings,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        max_retries=5,
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )


if not api_key:
    st.info("Provide a Google Gemini API key in the sidebar to start querying.")
    st.stop()

try:
    with st.spinner("Loading SEC disclosures and vector index..."):
        qa_chain = initialize_rag_pipeline()
except Exception as error:
    st.error(str(error))
    st.stop()

st.success("SEC vector database ready")
sample_queries = [
    "What is the total amount of commercial paper, long-term debt, and credit facilities available?",
    "What specific supply chain concentration or operational risks were highlighted?",
    "What are the primary drivers of service revenue growth?",
    "Are there any ongoing antitrust investigations, tax disputes, or legal proceedings mentioned?",
]
st.markdown("**Sample audit queries**")
query_columns = st.columns(2)
if "audit_query" not in st.session_state:
    st.session_state.audit_query = sample_queries[0]

for index, sample_query in enumerate(sample_queries):
    if query_columns[index % 2].button(sample_query, key=f"sample_{index}"):
        st.session_state.audit_query = sample_query

user_query = st.text_input(
    "Ask a custom financial, balance sheet, or operational risk question",
    key="audit_query",
)

if st.button("Run financial audit", type="primary"):
    if not user_query.strip():
        st.warning("Enter a question before running the audit.")
    else:
        with st.spinner("Searching full filing and synthesizing response..."):
            try:
                response = qa_chain.invoke({"query": user_query})

                st.subheader("Audit response")
                st.write(response["result"])

                with st.expander("Retrieved source snippets"):
                    for index, document in enumerate(response["source_documents"]):
                        st.markdown(f"**Source chunk {index + 1}:**")
                        st.text(document.page_content[:600] + "...")

            except Exception as error:
                if "RateLimitError" in type(error).__name__ or "429" in str(error):
                    st.error(
                        "API quota or rate limit exceeded. Please wait for the quota "
                        "window to reset, or use a Google AI Studio key with available "
                        "quota. The app now uses Gemini Flash-Lite and retrieves fewer "
                        "chunks to reduce request usage."
                    )
                else:
                    st.error(f"An unexpected system error occurred: {error}")
