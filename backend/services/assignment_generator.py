import os
from groq import Groq
from dotenv import load_dotenv
from backend.rag.retriever import retrieve

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FEW_SHOT_EXAMPLES = """
Example 1:
Topic: Git & Version Control
Difficulty: Beginner
Assignment: Create a collaborative Git workflow where students fork a repo, create feature branches, make meaningful commits, open pull requests, and resolve merge conflicts. They must write clear commit messages and document their workflow in a README.
Rubric:
- Proper branching strategy (20%)
- Meaningful commit messages (20%)
- Successful pull request with description (20%)
- Merge conflict resolution (20%)
- README documentation (20%)

Example 2:
Topic: FastAPI Backend Development
Difficulty: Intermediate
Assignment: Build a REST API with FastAPI that includes at least 5 endpoints, input validation with Pydantic, error handling, and auto-generated documentation. Students must write unit tests for each endpoint and deploy locally with uvicorn.
Rubric:
- API design and endpoint structure (25%)
- Pydantic validation and error handling (25%)
- Unit test coverage above 70% (25%)
- Documentation and code quality (25%)
"""

def generate_assignment(topic: str, week: int, difficulty: str) -> dict:
    """
    Generate an assignment using few-shot prompting and reflection loop.

    Example:
        result = generate_assignment("Prompt Engineering", 3, "Intermediate")
        result["final"]    # polished final assignment
        result["rubric"]   # grading rubric
        result["draft"]    # original draft
        result["critique"] # what was improved
    """

    # Pull relevant syllabus context for this topic
    syllabus_chunks = retrieve(f"Week {week} {topic}", k=4)
    syllabus_context = "\n".join(syllabus_chunks)

    # Step 1: Generate draft using few-shot examples + syllabus context
    draft_prompt = f"""{FEW_SHOT_EXAMPLES}

Here is what the CMSC389A course syllabus says about this topic:
{syllabus_context}

Now create a new assignment strictly aligned with the course syllabus above:
Topic: {topic}
Week: {week}
Difficulty: {difficulty}

Write a clear, complete, practical assignment description for CMSC389A students.
Include: objective, description, deliverables."""

    draft_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": draft_prompt}],
        max_tokens=1024
    )
    draft = draft_response.choices[0].message.content

    # Step 2: Critique the draft
    critique_prompt = f"""You are a senior professor reviewing this assignment draft for CMSC389A.
Critique it specifically for: clarity, appropriate difficulty level, alignment with learning objectives, and practicality.
Be specific and concise about what needs improvement.

Assignment Draft:
{draft}

Critique:"""

    critique_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": critique_prompt}],
        max_tokens=512
    )
    critique = critique_response.choices[0].message.content

    # Step 3: Revise based on critique
    revise_prompt = f"""Improve this assignment based on the critique below.
Return only the improved assignment. Make it complete and well structured.

Original Draft:
{draft}

Critique:
{critique}

Improved Assignment:"""

    final_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": revise_prompt}],
        max_tokens=1024
    )
    final = final_response.choices[0].message.content

    # Step 4: Generate rubric
    rubric_prompt = f"""Create a grading rubric for this assignment with exactly 5 criteria, each worth 20%.
Each criterion must be specific and measurable. Format clearly.

Assignment:
{final}

Rubric:"""

    rubric_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": rubric_prompt}],
        max_tokens=512
    )
    rubric = rubric_response.choices[0].message.content

    # Step 5: Generate starter code
    starter_prompt = f"""Generate a Python starter code template for this assignment.
Include:
- Necessary imports
- Empty functions with docstrings explaining what students must implement
- TODO comments guiding students
- A main block to run the code

Assignment:
{final}

Python Starter Code:"""

    starter_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": starter_prompt}],
        max_tokens=1024
    )
    starter_code = starter_response.choices[0].message.content

    return {
        "draft": draft,
        "critique": critique,
        "final": final,
        "rubric": rubric,
        "starter_code": starter_code,
        "topic": topic,
        "week": week,
        "difficulty": difficulty,
        "syllabus_context": syllabus_context
    }
