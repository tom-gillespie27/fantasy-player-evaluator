"""Player model definitions."""

import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    sleeper_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    position = Column(String)
    team = Column(String)
    age = Column(Integer)
    years_experience = Column(Integer)
    injury_status = Column(String, nullable=True)
    depth_chart_position = Column(Integer, nullable=True)
    adp_ppr = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
