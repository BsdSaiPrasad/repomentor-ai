import os

from dotenv import load_dotenv
from backend.llm.groq_client import extract_groq_text, groq_chat_completion

from backend.rag.retriever import retrieve

load_dotenv()


def _extract_week(syllabus_context: str) -> int | None:
    import re

    match = re.search(r"week\s+(\d+)", syllabus_context, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _is_supported_topic(topic: str, syllabus_context: str) -> bool:
    lowered_context = syllabus_context.lower()
    lowered_topic = topic.strip().lower()
    if not lowered_topic:
        return False
    if lowered_topic in lowered_context:
        return True
    topic_words = [word for word in lowered_topic.split() if len(word) > 3]
    return bool(topic_words) and all(word in lowered_context for word in topic_words)


def _needs_starter_code(topic: str, assignment_text: str) -> bool:
    lowered = f"{topic}\n{assignment_text}".lower()
    starter_signals = [
        "mcp",
        "build",
        "implement",
        "api",
        "backend",
        "client",
        "server",
        "code",
        "python",
        "fastapi",
        "repository",
    ]
    return any(signal in lowered for signal in starter_signals)


def generate_assignment(topic: str, difficulty: str, refinement_notes: str = "") -> dict:
    syllabus_chunks = retrieve(topic, k=4)
    syllabus_context = "\n".join(syllabus_chunks)

    if not _is_supported_topic(topic, syllabus_context):
        raise ValueError(
            "This topic is not clearly supported by the CMSC389A course materials."
        )

    inferred_topic = topic
    inferred_week = _extract_week(syllabus_context)

    refinement_block = (
        f"\nFaculty refinement notes:\n{refinement_notes.strip()}\n"
        if refinement_notes.strip()
        else "\nFaculty refinement notes:\nNone provided.\n"
    )

    draft_prompt = f"""Here is what the CMSC389A course syllabus says about this topic:
{syllabus_context}

Create one new assignment strictly aligned with the course material above.

Requested topic: {topic}
Course-grounded topic: {inferred_topic}
Difficulty: {difficulty}
Inferred week: {inferred_week}
{refinement_block}

Write a concise, realistic assignment handout for CMSC389A students.
It must be clearly understandable on first read and actually doable in one week.
Do not invent unrelated domains, hobbies, datasets, tools, codebases, or instructor logistics.
Do not invent external APIs, repos, or infrastructure unless they are clearly supported by the course context.
Prefer practical software-development tasks that match the syllabus.
If faculty refinement notes are provided, follow them unless they conflict with the course context.

Use exactly these sections in this order:
Title
Why This Matters
Learning Goals
Student Task
Deliverables
Constraints
Submission Checklist
Estimated Effort

Keep it specific, short, and directly usable by a professor. Avoid filler, repetition, and generic AI phrasing."""

    draft_response = groq_chat_completion(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": draft_prompt}],
        max_tokens=1024,
    )
    draft = extract_groq_text(draft_response)

    final = draft
    critique = "Stable mode: detailed critique step disabled to reduce latency and failure points."
    student_doubts = "Stable mode: student-doubts step disabled to reduce latency and failure points."
    validation_notes = "Stable mode."

    rubric_prompt = f"""Create a grading rubric for this assignment with exactly 5 criteria, each worth 20%.
Each criterion must be specific, measurable, and directly tied to the deliverables.
Do not mention tools or requirements that are not clearly present in the assignment itself.
Format it as:
- Criterion name
- What excellent work includes
- Common misses

Assignment:
{final}

Rubric:"""

    rubric_response = groq_chat_completion(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": rubric_prompt}],
        max_tokens=512,
    )
    rubric = extract_groq_text(rubric_response)

    if _needs_starter_code(topic, final):
        starter_prompt = f"""You are helping a professor prepare lightweight starter material for a CMSC389A assignment.

Create a small, practical starter scaffold for the assignment below.

Rules:
- Keep it minimal and beginner-friendly.
- Use only a few files.
- Include short code snippets, not a full finished solution.
- Prefer Python when the assignment is implementation-oriented.
- Include a suggested file structure.
- Include brief notes on what students still need to implement.
- Do not solve the assignment completely.
- If the assignment does not truly need code, say so clearly.

Assignment:
{final}

Return the starter material in markdown with these sections:
Starter Files
Code Skeleton
What Students Must Complete
"""

        starter_response = groq_chat_completion(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": starter_prompt}],
            max_tokens=700,
        )
        starter_code = extract_groq_text(starter_response)
    else:
        starter_code = (
            "No starter code needed. This assignment should be understandable and "
            "doable from the handout alone."
        )

    return {
        "draft": draft,
        "critique": critique,
        "student_doubts": student_doubts,
        "validation_notes": validation_notes,
        "final": final,
        "rubric": rubric,
        "starter_code": starter_code,
        "topic": topic,
        "week": inferred_week,
        "difficulty": difficulty,
        "refinement_notes": refinement_notes,
        "assignment_format": None,
        "provided_context": "",
        "syllabus_context": syllabus_context,
    }
