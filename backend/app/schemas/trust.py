from datetime import datetime

from pydantic import BaseModel, ConfigDict

class TrustHistoryRead(BaseModel):
    id: int
    user_id: int
    event_type: str
    source_id: str
    points: int
    score_after: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class TrustSummaryRead(BaseModel):
    user_id: int
    trust_score: int
    trust_level: str
    can_submit_movies: bool

