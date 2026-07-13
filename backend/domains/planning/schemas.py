"""
Planning domain schemas.
Pydantic models for daily planning entries and pixels.
"""
from __future__ import annotations

from datetime import date
# RIMOSSO: "Any" non è più importato né utilizzato.
from typing import Optional

from pydantic import Field, field_validator

from backend.core.schemas import ORMBaseModel, StrictBaseModel

# Aggiunto "PX" ai tipi validi
VALID_DAILY_ENTRY_TYPES = {
    "OD", "PD", "N1", "N2", "N3", "N4", 
    "OW", "OM", "PM", "PW", "EP", "EN", 
    "PX"  # Calendar Pixel
}


class DailyEntryBase(StrictBaseModel):
    """Schema base per i record del planning."""
    data_riferimento: date
    tipo: str = Field(..., max_length=2)
    testo: Optional[str] = None
    completato: bool = False
    
    # Campo per la chiave esterna
    category_id: Optional[int] = Field(None, description="ID della categoria/umore nella tabella ponte (UserCategory)")

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_DAILY_ENTRY_TYPES:
            raise ValueError(f"Tipo non valido. Deve essere uno tra: {', '.join(VALID_DAILY_ENTRY_TYPES)}")
        return v


class DailyEntryCreate(DailyEntryBase):
    """Schema per la creazione di un entry/pixel."""
    pass


class DailyEntryUpdate(StrictBaseModel):
    """Schema per l'aggiornamento. Tutti i campi sono opzionali per patch parziali."""
    testo: Optional[str] = None
    completato: Optional[bool] = None
    category_id: Optional[int] = None


class DailyEntryResponse(ORMBaseModel):
    """Schema di risposta in lettura per il Frontend."""
    id: int
    user_id: int
    data_riferimento: date
    tipo: str
    testo: Optional[str]
    completato: bool
    category_id: Optional[int]