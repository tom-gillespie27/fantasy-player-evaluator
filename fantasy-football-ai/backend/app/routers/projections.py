"""Projection-related API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.player import Player
from ..models.projection import Projection

router = APIRouter()


def _projection_to_dict(projection: Projection) -> dict:
    return {
        "id": str(projection.id),
        "player_id": str(projection.player_id),
        "season": projection.season,
        "week": projection.week,
        "projected_points_ppr": projection.projected_points_ppr,
        "floor_points": projection.floor_points,
        "ceiling_points": projection.ceiling_points,
        "boom_probability": projection.boom_probability,
        "bust_probability": projection.bust_probability,
        "model_version": projection.model_version,
        "created_at": projection.created_at,
    }


@router.get("")
async def list_projections(
    position: Optional[str] = None,
    season: Optional[int] = None,
    week: Optional[int] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(Projection)
    if position:
        stmt = stmt.join(Player, Player.id == Projection.player_id).where(Player.position == position)
    if season is not None:
        stmt = stmt.where(Projection.season == season)
    if week is not None:
        stmt = stmt.where(Projection.week == week)
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    projections = result.scalars().all()
    return [_projection_to_dict(proj) for proj in projections]


@router.get("/{player_id}")
async def get_player_projections(player_id: UUID, db: AsyncSession = Depends(get_db)) -> list[dict]:
    stmt = select(Projection).where(Projection.player_id == player_id)
    result = await db.execute(stmt)
    projections = result.scalars().all()
    if not projections:
        raise HTTPException(status_code=404, detail="No projections found for this player")
    return [_projection_to_dict(proj) for proj in projections]
