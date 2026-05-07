import os
from groq import Groq
from dotenv import load_dotenv
from backend.rag.retriever import retrieve

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_course_assistant(question: str) -> dict:
    chunks = retrieve(question, k=10)
    context = "\n\n".join(chunks)

    prompt = f"""You are a helpful TA for CMSC 389A: Modern Software Development with GenAI at UMD.

Answer the student's question using ONLY the course material provided below.
If the answer is not in the material, say "I don't have that information in the course materials."

Course Material:
{context}

Student Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": chunks
    }


def chat_course_assistant(messages: list[dict]) -> dict:
    conversation_lines = []
    last_user_question = ""

    for message in messages[-8:]:
        role = message.get("role", "")
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        if role == "user":
            conversation_lines.append(f"Student: {content}")
            last_user_question = content
        elif role == "assistant":
            conversation_lines.append(f"Assistant: {content}")

    if not last_user_question:
        raise ValueError("A user question is required.")

    chunks = retrieve(last_user_question, k=10)
    context = "\n\n".join(chunks)
    conversation = "\n".join(conversation_lines)

    prompt = f"""You are a helpful TA for CMSC 389A: Modern Software Development with GenAI at UMD.

Answer using ONLY the course material provided below.
Use the earlier conversation only to understand follow-up questions and references like "that week" or "that assignment".
If the answer is not in the course material, say: "I don't have that information in the course materials."
Keep the answer clear, direct, and student-friendly.

Course Material:
{context}

Conversation:
{conversation}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": chunks
    }
