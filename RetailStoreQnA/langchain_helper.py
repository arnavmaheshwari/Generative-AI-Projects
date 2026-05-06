from langchain_google_genai import ChatGoogleGenerativeAI
import pyodbc
import re
import os
from dotenv import load_dotenv

load_dotenv()


def clean_sql(sql: str) -> str:
    sql = sql.strip()
    sql = re.sub(r"^```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r"```$", "", sql).strip()
    return sql


def get_answer(question: str) -> tuple[str, list]:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-V5VTL7B;"
        "DATABASE=retail_store;"
        "Trusted_Connection=yes;"
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-robotics-er-1.5-preview",
            temperature=0.5,
            api_key=os.getenv("gemini_key")
        )

        prompt = f"""
You are an expert Microsoft SQL Server data analyst.

DATABASE DETAILS
Database name: retail_store
Database type: Microsoft SQL Server

SCHEMA (THIS IS THE COMPLETE SCHEMA — DO NOT INVENT ANY TABLES)

Table: t_shirts
Columns:
- t_shirt_id (int, primary key)
- brand (Van Huesen, Levi, Nike, Adidas)
- color (Red, Blue, Black, White)
- size (XS, S, M, L, XL)
- price (int)
- stock_quantity (int)

Table: discounts
Columns:
- discount_id (int, primary key)
- t_shirt_id (int, foreign key → t_shirts.t_shirt_id)
- pct_discount (decimal between 0 and 100)

IMPORTANT RULES (MUST FOLLOW ALL)
- Target database is SQL Server
- Use SQL Server syntax ONLY
- NEVER use backticks (`)
- NEVER use MySQL syntax
- NEVER use LIMIT (use TOP instead)
- Use only the tables and columns listed above
- DO NOT assume the existence of sales or orders tables
- There is NO sales history in this database
- “Sales” must be DERIVED using available columns
- DO NOT use Markdown
- DO NOT wrap output in ``` blocks
- Output ONLY raw SQL

DEFINITION OF "TOTAL SALES"
Total sales means:
price × stock_quantity

QUESTION
{question}

Return ONLY the SQL Server query.
"""

        raw_sql = llm.invoke(prompt).content
        sql = clean_sql(raw_sql)

        # -------- SAFETY CHECKS --------
        forbidden = ("drop ", "delete ", "truncate ", "update ", "insert ", "alter ")
        if any(word in sql.lower() for word in forbidden):
            raise ValueError("Unsafe SQL operation detected")

        if "`" in sql:
            raise ValueError("Invalid SQL dialect: backticks detected")

        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        return sql, rows

    finally:
        conn.close()
