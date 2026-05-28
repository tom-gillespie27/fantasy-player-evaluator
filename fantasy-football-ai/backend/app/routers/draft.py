"""Draft recommendation API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.player import Player
from ..models.projection import Projection

router = APIRouter()


def _ranking_to_dict(player: Player, projection: Projection) -> dict:
    return {
        "player_id": str(player.id),
        "name": player.name,
        "position": player.position,
        "team": player.team,
        "season": projection.season,
        "week": projection.week,
        "projected_points_ppr": projection.projected_points_ppr,
    }


def _board_item(player: Player, projection: Projection, rank: int) -> dict:
    return {
        "rank": rank,
        "player_id": str(player.id),
        "name": player.name,
        "position": player.position,
        "team": player.team,
        "season": projection.season,
        "week": projection.week,
        "projection": {
            "projected_points_ppr": projection.projected_points_ppr,
            "floor_points": projection.floor_points,
            "ceiling_points": projection.ceiling_points,
        },
        "boom_probability": projection.boom_probability,
        "bust_probability": projection.bust_probability,
        "ai_summary": "",
    }


@router.get("/rankings")
async def get_rankings(
    position: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(Player, Projection).join(Projection, Projection.player_id == Player.id)
    if position:
        stmt = stmt.where(Player.position == position)
    stmt = stmt.order_by(desc(Projection.projected_points_ppr)).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    return [_ranking_to_dict(player, projection) for player, projection in rows]


@router.get("/board")
async def get_draft_board(
    position: Optional[str] = None,
    season: Optional[int] = None,
    limit: int = 200,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(Player, Projection).join(Projection, Projection.player_id == Player.id)
    if position:
        stmt = stmt.where(Player.position == position)
    if season is not None:
        stmt = stmt.where(Projection.season == season)
    stmt = stmt.order_by(desc(Projection.projected_points_ppr)).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    return [_board_item(player, projection, rank + 1) for rank, (player, projection) in enumerate(rows)]
