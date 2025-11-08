from pydantic import BaseModel
from typing import List

class JournalistProfile(BaseModel):
    name: str
    topics: List[str]
    tone: str
    bias: str
    credibilityScore: int
    controversies: List[str]
