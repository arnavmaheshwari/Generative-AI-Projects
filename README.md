# Gen-AI Applications Portfolio

A comprehensive monorepo showcasing Generative AI capabilities utilizing Google's Gemini LLMs, LangChain, and Streamlit. This repository contains two powerful AI-driven tools: a **News Research Tool** leveraging Retrieval-Augmented Generation (RAG), and a **Retail Store Q&A** application capable of translating natural language directly into Microsoft SQL Server queries.

---

## 📖 Overview

This project provides interactive, browser-based applications that make advanced AI accessible.

* **News Research Tool:** Designed for analysts and researchers, it allows users to input up to three news article URLs, processes their content, and provides a conversational interface to query the articles with exact source citations.
* **Retail Store Q&A:** Built for retail managers and data analysts, this tool democratizes database access by allowing users to ask natural language questions (e.g., "What are total sales?") and executing dynamically generated SQL against a retail database.

---

## ✨ Features

### News Research Tool

* **URL Ingestion:** Loads unstructured data directly from web URLs.
* **Intelligent Text Splitting:** Uses `RecursiveCharacterTextSplitter` to optimize context windows for the LLM.
* **Local Vector Indexing:** Employs FAISS to build and store local vector embeddings for fast retrieval.
* **Source Citations:** Strictly enforces source citation in answers to prevent hallucinations and provide traceability.

### Retail Store Q&A

* **Natural Language to SQL:** Translates user questions into MS SQL Server syntax.
* **Direct Database Execution:** Automatically queries the database and renders the output within a Streamlit dataframe.
* **Query Caching:** Utilizes Streamlit's `@st.cache_data` (1-hour TTL) to cache expensive database queries and LLM calls.
* **Safety Mechanisms:** Employs active validation to block unsafe database operations like `DROP`, `DELETE`, and `UPDATE`.

---

## 🛠️ Tech Stack

| Category | Technologies |
| --- | --- |
| **Frontend** | Streamlit |
| **LLM & AI** | Google Gemini (`gemini-robotics-er-1.5-preview`), LangChain |
| **Embeddings** | Google Generative AI Embeddings (`models/gemini-embedding-001`) |
| **Vector Store** | FAISS |
| **Database** | Microsoft SQL Server, PyODBC |
| **Environment** | Python `python-dotenv` |

---

## 🏗️ Architecture

### News Research Tool Data Flow

1. **Ingestion:** User inputs URLs; `UnstructuredURLLoader` extracts text.
2. **Processing:** Text is chunked with a 1000-character size limit using `RecursiveCharacterTextSplitter`.
3. **Embedding:** Chunks are vectorized using Google Gemini Embeddings and stored in a local FAISS index.
4. **Retrieval & Generation:** A query retrieves the Top-3 ($k=3$) relevant documents from FAISS, constructing a custom prompt for the LLM to generate an answer backed strictly by sources.

### Retail Store Q&A Data Flow

1. **Prompt Engineering:** User query is injected into a specialized prompt containing the strict MS SQL database schema.
2. **SQL Generation:** Gemini LLM generates native SQL Server syntax.
3. **Sanitization:** The raw SQL undergoes regex cleaning and security validation.
4. **Execution:** Query executed via PyODBC; results rendered in Streamlit.

---

## 📁 Project Structure

```text
.
├── NewsResearchTool/
│   ├── main.py                     # Streamlit frontend and RAG pipeline setup
│   ├── retrievalQAWithSources.py   # Custom LLM invocation and retrieval logic
│   └── vector_index/               # Local directory where FAISS indexes are saved
├── RetailStoreQnA/
│   ├── main.py                     # Streamlit UI and caching configuration
│   └── langchain_helper.py         # DB connection, prompt generation, and security
├── .env                            # Environment variables file (requires gemini_key)
└── How to run streamlit app.txt    # Basic run instructions

```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Microsoft SQL Server (for RetailStoreQnA)
* ODBC Driver 17 for SQL Server

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/arnavmaheshwari/gen-ai.git
cd gen-ai

```


2. **Install dependencies**
Ensure you have the required libraries installed:
```bash
pip install streamlit langchain-google-genai langchain-community unstructured pyodbc faiss-cpu python-dotenv

```


3. **Database Setup (Retail Store Tool)**
Ensure a local Microsoft SQL Server instance is running (`SERVER=DESKTOP-V5VTL7B`).
Create a database named `retail_store` with the tables defined in the schema below.
4. **Environment Variables**
Create a `.env` file in the root directory and add your Google API key:
```env
gemini_key=your_google_gemini_api_key_here

```


*(Note: The apps rely on the `gemini_key` environment variable to authenticate with Google Generative AI)*.
5. **Run the Applications**
Use Streamlit to run either of the main application files:
**For News Research:**
```bash
streamlit run NewsResearchTool/main.py

```


**For Retail Store Q&A:**
```bash
streamlit run RetailStoreQnA/main.py

```



---

## ⚙️ Environment Variables

| Variable | Description | Required |
| --- | --- | --- |
| `gemini_key` | Google Generative AI API Key required for LLM and Embeddings. | Yes |

---

## 🗄️ Database Schema (Retail Store Q&A)

The Retail Q&A tool specifically maps natural language to a defined schema within MS SQL Server.

**Table:** `t_shirts`

* `t_shirt_id` (int, primary key)
* `brand` (Van Huesen, Levi, Nike, Adidas)
* `color` (Red, Blue, Black, White)
* `size` (XS, S, M, L, XL)
* `price` (int)
* `stock_quantity` (int)

**Table:** `discounts`

* `discount_id` (int, primary key)
* `t_shirt_id` (int, foreign key → t_shirts.t_shirt_id)
* `pct_discount` (decimal between 0 and 100)

---

## ⚡ Performance

* **Caching:** The Retail Q&A tool implements Streamlit's `@st.cache_data` with a 3600-second (1 hour) Time-To-Live (TTL). This significantly reduces redundant LLM API calls and database hits for duplicate questions, showing an active "Thinking 🤔" spinner when computing fresh answers. Users can manually clear the cache via the UI.
* **Vectorization Limits:** The News Research tool is optimized by enforcing dangerous deserialization allowances specifically for locally-controlled FAISS indexes, reducing load times.

---

## 🛡️ Security

The Retail Store Q&A implements strict programmatic security checks directly on generated SQL before passing it to PyODBC:

* **Destructive Command Blocking:** Throws a `ValueError("Unsafe SQL operation detected")` if the LLM attempts to generate any strings containing `drop`, `delete`, `truncate`, `update`, `insert`, or `alter`.
* **Dialect Validation:** Explicitly checks for invalid Markdown or MySQL backticks (```) and rejects the query, preventing syntax errors and enforcing SQL Server standards.

---

## 📈 Future Improvements

* Implement dynamic database connection configurations via the UI to remove hardcoded server names in the PyODBC string.
* Extend the `UnstructuredURLLoader` capability to support PDF and CSV document uploads in the Streamlit UI.
* Introduce containerization (Docker) to streamline ODBC driver installations and PyODBC setups for different operating systems.

---

## 📝 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
