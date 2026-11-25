from enum import StrEnum

class TrustEvent(StrEnum):
    REVIEW_APPROVED = "review_approved"
    WATCHLIST_ADDED = "watchlist_added"
    MOVIE_APPROVED = "movie_approved"
    MOVIE_RATED = "movie_rated"
    CORRECTION_APPROVED = "correction_approved"
    MOVIE_REJECTED = "movie_rejected"
    RULE_VIOLATION = "rule_violation"
    
TRUST_POINTS ={
    TrustEvent.REVIEW_APPROVED: 5,
    TrustEvent.WATCHLIST_ADDED: 10,
    TrustEvent.MOVIE_APPROVED: 20,
    TrustEvent.MOVIE_RATED: 1,
    TrustEvent.CORRECTION_APPROVED: 10,
    TrustEvent.MOVIE_REJECTED: -10,
    TrustEvent.RULE_VIOLATION: -30,
}

TRUSTED_USER_THRESHOLD = 300
HIGH_TRUST_THRESHOLD = 700

def get_trust_level(score: int) -> str:
    if score >= HIGH_TRUST_THRESHOLD:
        return "high_trust"
    if score >= TRUSTED_USER_THRESHOLD:
        return "trusted"
    if score >= 100:
        return "active"
    
    return "new"