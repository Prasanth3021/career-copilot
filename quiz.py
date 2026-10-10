"""Interview practice: question bank + loose answer checking.

How answer checking works (deliberately simple):
  - Each question has `key_points`: the concepts a good answer should mention.
  - An answer "hits" a key point if any of its significant words appear in the
    answer text.
  - Verdicts: >=70% of key points hit -> "strong"; >=40% -> "partial";
    otherwise "missed". This rewards covering the right concepts, not wording.

Sessions are kept in a module-level dict, so they reset on server restart.
That is fine for a demo; a production version would persist them.
"""

import re
import uuid

# A small, fixed bank. Each entry: question, category, key_points.
QUESTION_BANK = [
    {
        "category": "cs",
        "question": "Explain the difference between a list and a dictionary in Python. When would you use each?",
        "key_points": ["list ordered", "index", "dictionary key", "lookup", "hash"],
    },
    {
        "category": "cs",
        "question": "What is Big-O notation? Compare the time complexity of searching a sorted list with binary search versus a linear scan.",
        "key_points": ["big-o", "growth", "binary log", "linear", "complexity"],
    },
    {
        "category": "cs",
        "question": "Explain object-oriented programming. What are encapsulation, inheritance, and polymorphism?",
        "key_points": ["encapsulation", "inheritance", "polymorphism", "class", "object"],
    },
    {
        "category": "cs",
        "question": "What is the difference between SQL JOIN types — INNER, LEFT, and FULL OUTER?",
        "key_points": ["inner match", "left all", "null", "outer", "join"],
    },
    {
        "category": "cs",
        "question": "What happens when you call an API endpoint and it returns a 500 error? How would you debug it?",
        "key_points": ["server error", "logs", "reproduce", "stack trace", "debug"],
    },
    {
        "category": "cs",
        "question": "Explain what a REST API is and what makes an API 'RESTful'.",
        "key_points": ["http", "stateless", "resources", "verbs", "get post"],
    },
    {
        "category": "cs",
        "question": "What is a hash table and how does it achieve O(1) average lookup time?",
        "key_points": ["hash function", "bucket", "collision", "o(1)", "key"],
    },
    {
        "category": "cs",
        "question": "Describe the difference between processes and threads.",
        "key_points": ["memory", "shared", "concurrency", "parallel", "thread"],
    },
    {
        "category": "behavioral",
        "question": "Tell me about a time you debugged a difficult production issue. What was your process?",
        "key_points": ["reproduce", "logs", "hypothesis", "fix", "verify"],
    },
    {
        "category": "behavioral",
        "question": "Describe a disagreement you had with a teammate and how you resolved it.",
        "key_points": ["listen", "perspective", "compromise", "communicate", "resolve"],
    },
    {
        "category": "behavioral",
        "question": "Tell me about a project you are most proud of. What was your contribution?",
        "key_points": ["problem", "built", "impact", "learned", "contribution"],
    },
    {
        "category": "behavioral",
        "question": "How do you prioritize when you have multiple deadlines at once?",
        "key_points": ["prioritize", "impact", "communicate", "deadline", "plan"],
    },
]

_VALID_CATEGORIES = {"cs", "behavioral", "mixed"}
_VALID_ACTIONS = {"start", "answer", "score", "categories"}

_sessions: dict = {}


def _significant_words(text: str) -> set:
    words = set(re.findall(r"[a-z]{3,}", text.lower()))
    return words


def _grade(question: dict, answer: str) -> dict:
    ans_words = _significant_words(answer)
    hits = []
    for point in question["key_points"]:
        point_words = _significant_words(point)
        if point_words & ans_words:
            hits.append(point)
    total = len(question["key_points"])
    pct = round(100.0 * len(hits) / total, 1) if total else 0.0
    if pct >= 70:
        verdict = "strong"
    elif pct >= 40:
        verdict = "partial"
    else:
        verdict = "missed"
    missed = [p for p in question["key_points"] if p not in hits]
    return {"verdict": verdict, "coverage_pct": pct, "hit_points": hits,
            "missed_points": missed}


def interview_quiz(action: str, session_id: str = "", category: str = "mixed",
                   num_questions: int = 5, answer: str = "") -> dict:
    action = (action or "").strip().lower()
    if action not in _VALID_ACTIONS:
        return {"ok": False,
                "error": f"Unknown action '{action}'. Use one of: {sorted(_VALID_ACTIONS)}."}

    if action == "categories":
        return {"ok": True, "categories": sorted(_VALID_CATEGORIES)}

    if action == "start":
        category = (category or "mixed").strip().lower()
        if category not in _VALID_CATEGORIES:
            return {"ok": False,
                    "error": f"Unknown category '{category}'. Use one of: {sorted(_VALID_CATEGORIES)}."}
        try:
            num_questions = max(1, min(int(num_questions), len(QUESTION_BANK)))
        except (TypeError, ValueError):
            num_questions = 5
        pool = [q for q in QUESTION_BANK
                if category == "mixed" or q["category"] == category]
        selected = pool[:num_questions]
        sid = uuid.uuid4().hex[:8]
        _sessions[sid] = {"questions": selected, "index": 0,
                          "results": [], "category": category}
        q = selected[0]
        return {"ok": True, "session_id": sid, "category": category,
                "total_questions": len(selected),
                "question_number": 1,
                "question": q["question"]}

    # answer / score need a live session
    session = _sessions.get(session_id)
    if not session:
        return {"ok": False,
                "error": "Unknown or expired session_id. Start a new quiz with action='start'."}

    if action == "score":
        results = session["results"]
        strong = sum(1 for r in results if r["verdict"] == "strong")
        return {"ok": True, "session_id": session_id,
                "answered": len(results),
                "total_questions": len(session["questions"]),
                "strong_answers": strong,
                "results": results}

    # action == "answer"
    if session["index"] >= len(session["questions"]):
        return {"ok": False, "error": "Quiz already finished. Check 'score'."}
    if not answer or not answer.strip():
        return {"ok": False, "error": "Please provide a non-empty 'answer'."}
    q = session["questions"][session["index"]]
    grade = _grade(q, answer)
    session["results"].append({
        "question_number": session["index"] + 1,
        "question": q["question"],
        "verdict": grade["verdict"],
        "coverage_pct": grade["coverage_pct"],
        "missed_points": grade["missed_points"],
    })
    session["index"] += 1
    done = session["index"] >= len(session["questions"])
    response = {"ok": True, "session_id": session_id,
                "verdict": grade["verdict"],
                "coverage_pct": grade["coverage_pct"],
                "feedback": ("Key points you hit: " + ", ".join(grade["hit_points"])
                             if grade["hit_points"] else "No key points hit yet."),
                "missed_points": grade["missed_points"],
                "finished": done}
    if not done:
        nq = session["questions"][session["index"]]
        response["question_number"] = session["index"] + 1
        response["total_questions"] = len(session["questions"])
        response["next_question"] = nq["question"]
    else:
        strong = sum(1 for r in session["results"] if r["verdict"] == "strong")
        response["final"] = (f"Quiz complete: {strong}/{len(session['results'])} "
                             f"strong answers.")
    return response
