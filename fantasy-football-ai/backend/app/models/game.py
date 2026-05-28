"""Game model definitions."""

import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class GameLog(Base):
    __tablename__ = "game_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), index=True, nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    opponent = Column(String, nullable=False)
    fantasy_points_ppr = Column(Float, nullable=False)
    receptions = Column(Float, nullable=True)
    targets = Column(Float, nullable=True)
    receiving_yards = Column(Float, nullable=True)
    receiving_tds = Column(Float, nullable=True)
    carries = Column(Float, nullable=True)
    rushing_yards = Column(Float, nullable=True)
    rushing_tds = Column(Float, nullable=True)
    passing_yards = Column(Float, nullable=True)
    passing_tds = Column(Float, nullable=True)
    interceptions = Column(Float, nullable=True)
    snap_count_pct = Column(Float, nullable=True)
    target_share = Column(Float, nullable=True)
    air_yards_share = Column(Float, nullable=True)
