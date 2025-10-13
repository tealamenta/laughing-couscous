"""Configuration du systeme de recommandation."""

HYBRID_WEIGHTS = {
    "balanced": {"tfidf": 0.5, "bert": 0.5},
    "precision": {"tfidf": 0.6, "bert": 0.4},
    "semantic": {"tfidf": 0.4, "bert": 0.6},
}

DEFAULT_HYBRID_CONFIG = "balanced"
