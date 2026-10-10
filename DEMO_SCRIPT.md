# Demo script — Career Copilot (~2 minutes)

Target: under 3 minutes. Record screen + voiceover. Show, don't just tell.

## 0:00–0:15 — Hook
> "I'm Prasanth, and this is Career Copilot — an MCP server for the Alexa+
> track that turns any AI assistant into a job-hunt copilot. Three tools:
> application tracking, resume-to-JD matching, and interview practice."

_Show: terminal with the project folder, or the MCP client with the three
tools listed._

## 0:15–0:50 — Tool 1: track_application
> "First, tracking. I log an application — company, role, link — and it goes
> into a local SQLite database. I can update the status as I move through
> interviews, and filter by status or company."

_Do: call `track_application` action=add with a real example (e.g. company
"BB Insight", role "Engineering Trainee"). Then action=list to show it
stored. Then action=update to "interviewing"._

## 0:50–1:25 — Tool 2: match_resume_to_jd
> "Second, matching. I paste my resume and a job description, and it scores
> keyword overlap and tells me the most important missing keywords — so I
> know what to add, honestly."

_Do: call `match_resume_to_jd` with a short resume excerpt and a short JD.
Point at the score and the missing-keywords list. Mention it's honest
keyword coverage, not fake AI._

## 1:25–1:55 — Tool 3: interview_quiz
> "Third, practice. It quizzes me on CS fundamentals and behavioral
> questions, checks my answers against the key concepts, and tracks my
> score."

_Do: `interview_quiz` action=start, category=cs, num_questions=2. Answer the
first question out loud, submit via action=answer, show the verdict and
feedback. Then action=score._

## 1:55–2:10 — Close
> "Everything runs locally — no API keys, no accounts. Built with the
> official MCP Python SDK. GitHub repo linked below. Thanks!"

_Show: the repo/README one last time. End._

## Checklist before recording
- [ ] `pip install -r requirements.txt` done in `.venv`
- [ ] MCP client (e.g. Claude Desktop) connected to `server.py`
- [ ] Sample resume + JD text ready to paste
- [ ] Delete any test applications from `data/applications.db` (or keep —
      real data looks good)
