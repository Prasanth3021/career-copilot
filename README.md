# Career Copilot — MCP Server

**Alexa+ track entry** for the *Build, Ship, Shape: Amazon Developer Hackathon* (Devpost).

Career Copilot is a Model Context Protocol (MCP) server that gives an AI
assistant three career tools for a job hunt:

1. **`track_application`** — log job applications (company, role, date, status,
   posting link) into a local SQLite database; update statuses; list/filter by
   status or company.
2. **`match_resume_to_jd`** — paste a resume and a job description, get a
   keyword-overlap match score plus the most important missing keywords.
   Honest, simple TF-based scoring — keyword coverage, not semantic magic.
3. **`interview_quiz`** — practice interview questions (CS fundamentals +
   behavioral) from a local bank. Answers are checked loosely by concept
   coverage; your score is tracked per session.

No API keys, no accounts, no network calls. Everything runs locally.

## Quick start

```bash
cd ~/workspace/hackathon/career-copilot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python server.py        # runs on stdio; keep it running
```

## Connect it to an MCP client

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "career-copilot": {
      "command": "/home/YOUR_USER/workspace/hackathon/career-copilot/.venv/bin/python",
      "args": ["/home/YOUR_USER/workspace/hackathon/career-copilot/server.py"]
    }
  }
}
```

Restart Claude Desktop afterwards. The three tools then appear as
`track_application`, `match_resume_to_jd`, and `interview_quiz`.

Any MCP-compatible client works the same way: point it at `server.py`
with the venv's Python over stdio.

## Tool reference

### track_application
| arg | notes |
|---|---|
| `action` | `add` \| `update` \| `list` \| `get` |
| `company`, `role` | required for `add` |
| `date_applied` | `YYYY-MM-DD`, defaults to today |
| `status` | `applied` (default) \| `interviewing` \| `offer` \| `rejected` \| `withdrawn` |
| `link` | posting URL (optional) |
| `application_id` | required for `update` / `get` |

Examples:
- add: `{action:"add", company:"Acme", role:"SWE Intern", link:"https://..."}`
- list interviewing: `{action:"list", status:"interviewing"}`
- update: `{action:"update", application_id:3, status:"rejected"}`

### match_resume_to_jd
| arg | notes |
|---|---|
| `resume_text` | full resume text |
| `jd_text` | full job description text |
| `top_missing` | how many missing keywords to return (default 15) |

Returns `score` (0–100), `matched_keywords`, `missing_keywords` ranked by
importance in the JD, and a reminder to only add keywords you can defend.

### interview_quiz
| arg | notes |
|---|---|
| `action` | `start` \| `answer` \| `score` \| `categories` |
| `category` | `cs` \| `behavioral` \| `mixed` (for `start`) |
| `num_questions` | 1–12 (for `start`, default 5) |
| `session_id` | returned by `start`; needed for `answer`/`score` |
| `answer` | your answer text (for `answer`) |

## Project layout

```
career-copilot/
├── server.py            # FastMCP server, tool definitions
├── tools/
│   ├── applications.py  # SQLite application tracker
│   ├── matcher.py       # keyword-overlap resume/JD scorer
│   └── quiz.py          # question bank + loose answer grading
├── data/                # SQLite DB lives here (created on first use)
├── requirements.txt
├── README.md
└── DEMO_SCRIPT.md
```

## Demo video

🎬 _Placeholder — Prasanth records a <3 min demo following DEMO_SCRIPT.md and
links it here._

## Amazon product feedback

_— Placeholder — Prasanth fills this in after building against Amazon's
developer tooling. Suggested prompts:_
- _Which Amazon tools/APIs did you use (e.g., Alexa+ SDKs, MCP docs)?_
- _What worked well?_
- _What was confusing, missing, or broken?_

## Notes / simplifications

- Quiz sessions are in-memory (reset on restart) — fine for a demo.
- The matcher is keyword overlap, not embeddings or an LLM call. Fast,
  explainable, offline — and honest about what it measures.
