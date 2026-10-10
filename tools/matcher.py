"""Keyword-overlap scoring of a resume against a job description.

Method (deliberately simple and honest):
  1. Lowercase, strip punctuation, drop English stopwords and tokens < 3 chars.
  2. Count keyword frequencies in the JD.
  3. score = 100 * |resume_keywords ∩ jd_keywords| / |jd_keywords|
  4. Missing keywords ranked by JD frequency (most important gaps first).

This measures *keyword coverage only*. It does not understand meaning, cannot
tell whether you truly have a skill, and rewards keyword stuffing — say so in
the demo rather than overselling it.
"""

import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will", "have",
    "has", "this", "that", "from", "they", "their", "them", "its", "not",
    "but", "all", "can", "who", "what", "when", "where", "how", "why",
    "about", "into", "over", "such", "than", "then", "well", "also", "may",
    "more", "most", "other", "some", "any", "each", "few", "per", "via",
    "using", "used", "use", "able", "including", "include", "within",
    "between", "both", "being", "been", "were", "was", "is", "are", "be",
    "as", "at", "by", "on", "in", "of", "to", "a", "an", "or", "we", "us",
    "our", "work", "working", "team", "teams", "role", "join", "new",
    "including", "across", "help", "helps", "day", "etc",
}


def _keywords(text: str) -> Counter:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]*", text.lower())
    cleaned = []
    for tok in tokens:
        tok = tok.strip(".-")
        if len(tok) < 3:
            continue
        if tok in STOPWORDS:
            continue
        cleaned.append(tok)
    return Counter(cleaned)


def match_resume_to_jd(resume_text: str, jd_text: str, top_missing: int = 15) -> dict:
    if not resume_text or not resume_text.strip():
        return {"ok": False, "error": "resume_text is empty."}
    if not jd_text or not jd_text.strip():
        return {"ok": False, "error": "jd_text is empty."}
    try:
        top_missing = int(top_missing)
    except (TypeError, ValueError):
        top_missing = 15
    top_missing = max(1, min(top_missing, 50))

    resume_kw = set(_keywords(resume_text))
    jd_counts = _keywords(jd_text)
    jd_kw = set(jd_counts)

    if not jd_kw:
        return {"ok": False, "error": "No keywords extracted from jd_text."}

    matched = sorted(resume_kw & jd_kw)
    missing = sorted(jd_kw - resume_kw, key=lambda k: (-jd_counts[k], k))
    score = round(100.0 * len(matched) / len(jd_kw), 1)

    return {
        "ok": True,
        "score": score,
        "method": "keyword-overlap (not semantic matching)",
        "jd_keyword_count": len(jd_kw),
        "matched_count": len(matched),
        "matched_keywords": matched,
        "missing_count": len(missing),
        "missing_keywords": missing[:top_missing],
        "note": ("Add missing keywords to your resume ONLY if you can honestly "
                 "defend them in an interview."),
    }
