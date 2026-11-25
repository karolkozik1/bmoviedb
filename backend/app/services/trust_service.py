from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.trust import TRUST_POINTS, TrustEvent, get_trust_level
from app.models.trust_history import TrustHistory
from app.models.user import User

def get_trust_history(db: Session, user_id: int) -> list[TrustHistory]:
    statement = select(TrustHistory).where(TrustHistory.user_id == user_id).order_by(TrustHistory.created_at.desc(), TrustHistory.id.desc())
    return list(db.scalars(statement).all())

def apply_trust_event(db: Session, user_id: int, event_type: TrustEvent, source_id: str) -> TrustHistory | None:
    #Block na czas naliczania punktów
    user = db.scalar(select(User).where(User.id == user_id).with_for_update())
    if not user:
        raise ValueError("User not found")
    #Sprawdzenie czy zdarzenie już zostało naliczone
    existing_event = db.scalar(select(TrustHistory).where(
        TrustHistory.user_id == user_id, 
        TrustHistory.event_type == event_type, 
        TrustHistory.source_id == source_id
    ))
    if existing_event is not None:
        return None
    
    points = TRUST_POINTS[event_type]
    old_score = user.trust_score
    
    new_score = max(0, old_score + points)
    
    actual_change = new_score - old_score
    user.trust_score = new_score
    history = TrustHistory(
        user_id=user_id,
        event_type=event_type.value,
        source_id=source_id,
        points=actual_change,
        score_after=new_score
    )
    db.add(history)
    db.flush() 
    
    return history
    
def get_user_trust_summary(user: User) -> dict:
    return {
        "user_id": user.id,
        "trust_score": user.trust_score,
        "trust_level": get_trust_level(user.trust_score),
        "can_submit_movies": user.trust_score >= 300 or user.role in ("admin", "moderator"),
    }
    