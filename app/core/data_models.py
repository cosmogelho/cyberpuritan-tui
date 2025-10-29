# app/core/data_models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Record:
    id: int
    category: str
    titulo: str
    author: Optional[str]
    context: Optional[str]
    data: Optional[str]
    passagem_principal: Optional[str]
    anotacoes: Optional[str]
    aplicacoes: Optional[str]

@dataclass
class Resolution:
    id: int
    text: str
    category: Optional[str]
    created_at: Optional[str]
    last_reviewed_at: Optional[str]
    review_count: int