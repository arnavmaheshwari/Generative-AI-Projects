import os
import time
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.vectorstores import FAISS
from retrievalQAWithSources import retrieval_qa_with_sources

# --------------------------------------------------
# Setup
# --------------------------------------------------
load_dotenv()

st.title("News Research Tool 📈")
st.sidebar.title("News Article URLs")

urls = [st.sidebar.text_input(f"URL {i+1}") for i in range(3)]
process_url_clicked = st.sidebar.button("Process URLs")

VECTOR_DIR = "vector_index"

main_placeholder = st.empty()

llm = ChatGoogleGenerativeAI(
    model="gemini-robotics-er-1.5-preview",
    temperature=0.7,
    api_key=os.getenv("gemini_key")
)

# --------------------------------------------------
# Process URLs → Build FAISS
# --------------------------------------------------
if process_url_clicked:
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Loading data...✅✅✅")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", ","],
        chunk_size=1000
    )

    main_placeholder.text("Splitting text...✅✅✅")
    docs = text_splitter.split_documents(data)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",api_key=os.getenv("gemini_key"))

    main_placeholder.text("Building vector index...✅✅✅")
    vectorindex = FAISS.from_documents(docs, embeddings)

    vectorindex.save_local(VECTOR_DIR)
    main_placeholder.text("Vector index saved successfully ✅")
    time.sleep(1)

# --------------------------------------------------
# Question Answering
# --------------------------------------------------
query = st.text_input("Question:")

if query:
    if not os.path.exists(VECTOR_DIR):
        st.error("Vector index not found. Please process URLs first.")
    else:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",api_key=os.getenv("gemini_key"))

        vectorIndex = FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )

        main_placeholder.text("Retrieving answer...✅✅✅")
        result = retrieval_qa_with_sources(
            llm=llm,
            vector_index=vectorIndex,
            question=query,
            k=3
        )

        st.header("Answer")
        st.write(result["answer"])

        main_placeholder.text("Retrieved answer...✅✅✅")
        if result.get("source_documents"):
            st.subheader("Sources")
            for i, doc in enumerate(result["source_documents"], 1):
                st.write(f"Source {i}:")
                st.write(doc.page_content[:500] + "...")