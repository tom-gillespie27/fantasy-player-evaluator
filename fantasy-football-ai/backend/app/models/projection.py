"""Projection model definitions."""

import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class Projection(Base):
    __tablename__ = "projections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), index=True, nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=True)
    projected_points_ppr = Column(Float, nullable=False)
    floor_points = Column(Float, nullable=False)
    ceiling_points = Column(Float, nullable=False)
    boom_probability = Column(Float, nullable=False)
    bust_probability = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
