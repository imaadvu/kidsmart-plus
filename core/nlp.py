from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import re
import hashlib


LANG_LIT_KEYWORDS = {
    "language": 3,
    "literature": 3,
    "reading": 2,
    "writing": 2,
    "storytime": 4,
    "book": 1,
    "phonics": 4,
}

EARLY_CHILD_KEYWORDS = {
    "early childhood": 4,
    "toddler": 3,
    "preschool": 3,
    "kindergarten": 2,
    "parent-child": 2,
}


def normalize_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


def compute_dedupe_hash(title: str, date_str: str | None, city: str | None) -> str:
    key = f"{normalize_text(title).lower()}|{(date_str or '').lower()}|{(city or '').lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


@dataclass
class TagResult:
    category: str | None
    tags: List[str]
    free_flag: bool | None
    online_flag: bool | None
    reasons: List[str]


def rule_based_tags(title: str, description: str) -> TagResult:
    text = f"{title} {description}".lower()
    score_lang = sum(w for k, w in LANG_LIT_KEYWORDS.items() if k in text)
    score_early = sum(w for k, w in EARLY_CHILD_KEYWORDS.items() if k in text)
    category = None
    reasons: List[str] = []
    tags: List[str] = []
    if score_lang > score_early and score_lang > 0:
        category = "Language & Literature"
        reasons += [f"keyword:{k}" for k in LANG_LIT_KEYWORDS if k in text]
    elif score_early > 0:
        category = "Early Childhood Education"
        reasons += [f"keyword:{k}" for k in EARLY_CHILD_KEYWORDS if k in text]

    if re.search(r"\bfree\b", text):
        tags.append("free")
        free_flag = True
        reasons.append("keyword:free")
    else:
        free_flag = None

    online_flag = True if re.search(r"online|virtual|webinar|zoom", text) else None
    if online_flag:
        tags.append("online")
        reasons.append("keyword:online")

    return TagResult(category=category, tags=tags, free_flag=free_flag, online_flag=online_flag, reasons=list(dict.fromkeys(reasons)))

