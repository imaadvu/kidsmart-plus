from __future__ import annotations
from typing import Optional, List, Set
from sqlalchemy.orm import Session
from db.models import Program
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def find_near_duplicate(db: Session, title: str, description: str | None, city: str | None, threshold: float) -> Optional[Program]:
    text = (title or "") + "\n" + (description or "")
    # Candidate set: recent 60 days or same city
    q = db.query(Program)
    if city:
        q = q.filter(Program.city == city)
    candidates = q.order_by(Program.created_at.desc()).limit(200).all()
    if not candidates:
        return None
    docs = [text] + [((c.title or "") + "\n" + (c.description_text or "")) for c in candidates]
    try:
        vec = TfidfVectorizer(min_df=1, stop_words="english")
        mat = vec.fit_transform(docs)
        sims = cosine_similarity(mat[0:1], mat[1:]).flatten()
        idx = int(np.argmax(sims))
        if sims[idx] >= threshold:
            return candidates[idx]
    except Exception:
        return None
    return None


def near_duplicate_indices(texts: List[str], threshold: float = 0.82) -> Set[int]:
    """Given a list of texts, return indices that are near-duplicates.
    Strategy: keep first occurrence in each near-dup cluster; suppress later ones.
    """
    if not texts:
        return set()
    try:
        vec = TfidfVectorizer(min_df=1, stop_words="english")
        mat = vec.fit_transform(texts)
        sims = cosine_similarity(mat)
    except Exception:
        return set()
    n = len(texts)
    suppress: Set[int] = set()
    for i in range(n):
        if i in suppress:
            continue
        for j in range(i + 1, n):
            if j in suppress:
                continue
            if sims[i, j] >= threshold:
                suppress.add(j)
    return suppress
