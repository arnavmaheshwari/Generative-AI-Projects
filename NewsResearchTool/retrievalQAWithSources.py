def retrieval_qa_with_sources(llm, vector_index, question, k=3):
    # Step 1: Retrieve similar documents
    docs = vector_index.similarity_search(question, k=k)

    # Step 2: Build context
    context = "\n\n".join(
        f"Source {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )

    # Step 3: Build prompt
    prompt = f"""
You are an assistant that answers questions strictly using the provided sources.

Sources:
{context}

Question:
{question}

Answer concisely. Cite sources using [Source X].
"""

    # Step 4: Call LLM
    response = llm.invoke(prompt)

    # Step 5: Return structured output (like RetrievalQAWithSourcesChain)
    return {
        "answer": response.content,
        "sources": [f"Source {i+1}" for i in range(len(docs))],
        "source_documents": docs,
    }