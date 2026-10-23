"""One-click demo for the Career Copilot hackathon video.

Run:  python demo_run.py
It exercises all three tools and prints the results — record the terminal.
"""
import json
import time

from tools.applications import track_application
from tools.matcher import match_resume_to_jd
from tools.quiz import interview_quiz


def show(title, result):
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print()
    time.sleep(1)


print("\n>>> Career Copilot — live demo <<<\n")

# Tool 1: application tracker
show("TOOL 1: track_application (add)",
     track_application(action="add", company="BB Insight",
                       role="Engineering Trainee",
                       date_applied="2026-10-09",
                       link="https://careers.bbinsight.com"))
show("TOOL 1: track_application (list)",
     track_application(action="list"))
show("TOOL 1: track_application (update -> interviewing)",
     track_application(action="update", application_id=1,
                       status="interviewing"))

# Tool 2: resume-vs-JD matcher
resume = ("Python developer with experience in FastAPI, REST APIs, SQL, "
          "Docker, AWS, RAG pipelines, LLMs, AI agents, and prompt "
          "engineering. Built microservices and data pipelines.")
jd = ("We are hiring a Python backend intern. Requirements: Python, "
      "FastAPI, REST APIs, SQL, Docker, Kubernetes, CI/CD, debugging, "
      "and unit testing.")
show("TOOL 2: match_resume_to_jd", match_resume_to_jd(resume, jd))

# Tool 3: interview quiz
start = interview_quiz(action="start", category="cs", num_questions=1)
show("TOOL 3: interview_quiz (start)", start)
sid = start["session_id"]
answer = ("A list is an ordered collection accessed by index, while a "
          "dictionary is a key-value lookup structure implemented with "
          "a hash table.")
show("TOOL 3: interview_quiz (answer)",
     interview_quiz(action="answer", session_id=sid, answer=answer))
show("TOOL 3: interview_quiz (score)",
     interview_quiz(action="score", session_id=sid))

print("Demo complete.")
