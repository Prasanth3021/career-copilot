"""Career Copilot MCP server — Alexa+ track entry.

Exposes three tools over the Model Context Protocol:
  1. track_application  — log / query job applications (SQLite)
  2. match_resume_to_jd — keyword-overlap scoring of a resume vs a job description
  3. interview_quiz     — CS/behavioral interview practice with loose answer checking

Run:  .venv/bin/python server.py   (stdio transport; point your MCP client at it)
"""

from mcp.server.fastmcp import FastMCP

from tools.applications import track_application as _track_application
from tools.matcher import match_resume_to_jd as _match_resume_to_jd
from tools.quiz import interview_quiz as _interview_quiz

mcp = FastMCP("career-copilot")


@mcp.tool()
def track_application(
    action: str,
    company: str = "",
    role: str = "",
    date_applied: str = "",
    status: str = "",
    link: str = "",
    application_id: int = 0,
) -> dict:
    """Log and query job applications.

    action: "add" | "update" | "list" | "get"
    - add:    requires company + role. Optional: date_applied (YYYY-MM-DD, defaults
              to today), status (applied/interviewing/offer/rejected/withdrawn,
              defaults to applied), link (posting URL).
    - update: requires application_id + status.
    - list:   optional status and/or company filters (omit for everything).
    - get:    requires application_id.
    """
    return _track_application(
        action=action,
        company=company,
        role=role,
        date_applied=date_applied,
        status=status,
        link=link,
        application_id=application_id,
    )


@mcp.tool()
def match_resume_to_jd(resume_text: str, jd_text: str, top_missing: int = 15) -> dict:
    """Score how well a resume matches a job description.

    Honest, simple method: tokenizes both texts, drops stopwords, then computes
    keyword overlap. score = 100 * |resume keywords ∩ jd keywords| / |jd keywords|.
    Returns the score, matched keywords, and the most important missing keywords
    (ranked by frequency in the JD). This is keyword coverage, NOT semantic
    understanding — it cannot tell whether you actually have the skill.
    """
    return _match_resume_to_jd(resume_text, jd_text, top_missing)


@mcp.tool()
def interview_quiz(
    action: str,
    session_id: str = "",
    category: str = "mixed",
    num_questions: int = 5,
    answer: str = "",
) -> dict:
    """Practice interview questions with loose answer checking.

    action: "start" | "answer" | "score" | "categories"
    - start:  begins a session. category: cs | behavioral | mixed. Returns a
              session_id and the first question.
    - answer: submit your answer text for the current question. It is checked
              loosely by keyword overlap against the question's key points —
              this rewards hitting the right concepts, not exact wording.
    - score:  current tally for a session.
    - categories: list available question categories.

    Note: quiz sessions live in memory and reset when the server restarts.
    """
    return _interview_quiz(
        action=action,
        session_id=session_id,
        category=category,
        num_questions=num_questions,
        answer=answer,
    )


if __name__ == "__main__":
    mcp.run()
