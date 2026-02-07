
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class LOType(str, Enum):
    CONCEPT = "concept"
    TASK = "task"
    TROUBLESHOOTING = "troubleshooting"
    REFERENCE = "reference"

class EvidenceItem(BaseModel):
    file: str
    symbol: str
    symbol_id: str
    snippet_hash: str

class LearningObject(BaseModel):
    id: str
    type: LOType
    title: str
    description: str
    prerequisites: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    
    # Context filters (simple for POC)
    roles: List[str] = Field(default_factory=list)
    skill_level: Optional[str] = None
