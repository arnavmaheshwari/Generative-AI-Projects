import streamlit as st
from langchain_helper import get_answer

st.title("Retail Store Q&A 👕")

question = st.text_input("Question:")

@st.cache_data(
    show_spinner="Thinking 🤔",
    ttl=3600  # cache for 1 hour
)
def cached_get_answer(question: str) -> tuple[str, list]:
    return get_answer(question)

if question.strip():
    sql, rows = cached_get_answer(question)

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    st.subheader("Query Results")

    if rows:
        st.dataframe(rows)
    else:
        st.info("No results found.")

if st.button("Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared")
