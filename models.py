from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class Provider(BaseModel):
    id: uuid.UUID
    name: str
    service_type: str
    location: str
    phone_number: Optional[str]
    avg_rating: float
    total_reviews: int

class Review(BaseModel):
    provider_id: uuid.UUID
    reviewer_phone: str
    ratings: Dict[str, int]  # {punctuality: 5, skill: 4, politeness: 5, pricing: 3}
    review_text: str

class AIInsight(BaseModel):
    provider_id: uuid.UUID
    top_praise: Dict[str, float]
    top_concerns: Dict[str, float]
    emerging_mentions: Dict[str, float]
