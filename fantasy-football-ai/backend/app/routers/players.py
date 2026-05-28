"""Player-related API endpoints."""

import asyncio
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import AsyncSessionLocal, get_db
from ..models.game import GameLog
from ..models.player import Player
from ..services.sleeper_service import sleeper_service

router = APIRouter()


def _player_to_dict(player: Player) -> dict:
    return {
        "id": str(player.id),
        "sleeper_id": player.sleeper_id,
        "name": player.name,
        "position": player.position,
        "team": player.team,
        "age": player.age,
        "years_experience": player.years_experience,
        "injury_status": player.injury_status,
        "depth_chart_position": player.depth_chart_position,
        "adp_ppr": player.adp_ppr,
        "created_at": player.created_at,
        "updated_at": player.updated_at,
    }


def _game_log_to_dict(game_log: GameLog) -> dict:
    return {
        "id": str(game_log.id),
        "player_id": str(game_log.player_id),
        "season": game_log.season,
        "week": game_log.week,
        "opponent": game_log.opponent,
        "fantasy_points_ppr": game_log.fantasy_points_ppr,
        "receptions": game_log.receptions,
        "targets": game_log.targets,
        "receiving_yards": game_log.receiving_yards,
        "receiving_tds": game_log.receiving_tds,
        "carries": game_log.carries,
        "rushing_yards": game_log.rushing_yards,
        "rushing_tds": game_log.rushing_tds,
        "passing_yards": game_log.passing_yards,
        "passing_tds": game_log.passing_tds,
        "interceptions": game_log.interceptions,
        "snap_count_pct": game_log.snap_count_pct,
        "target_share": game_log.target_share,
        "air_yards_share": game_log.air_yards_share,
    }


async def _sync_players_task() -> None:
    player_map = await sleeper_service.get_all_players()
    async with AsyncSessionLocal() as session:
        for sleeper_id, payload in player_map.items():
            stmt = select(Player).where(Player.sleeper_id == sleeper_id)
            result = await session.execute(stmt)
            player = result.scalar_one_or_none()

            name = (
                payload.get("full_name")
                or payload.get("display_name")
                or f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
            )
            if not name:
                name = payload.get("player_id", sleeper_id)

            values = {
                "sleeper_id": sleeper_id,
                "name": name,
                "position": payload.get("position"),
                "team": payload.get("team"),
                "age": int(payload["age"]) if payload.get("age") is not None else None,
                "years_experience": int(payload.get("years_experience") or payload.get("years_exp") or 0),
                "injury_status": payload.get("injury_status"),
                "depth_chart_position": payload.get("depth_chart_position"),
                "adp_ppr": float(payload["adp_ppr"]) if payload.get("adp_ppr") is not None else None,
            }

            if player is None:
                session.add(Player(**values))
            else:
                for key, value in values.items():
                    setattr(player, key, value)
                session.add(player)

        await session.commit()


@router.get("")
async def list_players(
    position: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(Player)
    if position:
        stmt = stmt.where(Player.position == position)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    players = result.scalars().all()
    return [_player_to_dict(player) for player in players]


@router.get("/{player_id}")
async def get_player(player_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    stmt = select(Player).where(Player.id == player_id)
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return _player_to_dict(player)


@router.get("/{player_id}/gamelogs")
async def get_player_gamelogs(player_id: UUID, db: AsyncSession = Depends(get_db)) -> list[dict]:
    stmt = select(GameLog).where(GameLog.player_id == player_id).order_by(GameLog.season, GameLog.week)
    result = await db.execute(stmt)
    gamelogs = result.scalars().all()
    return [_game_log_to_dict(log) for log in gamelogs]


@router.get("/sync")
async def sync_players(background_tasks: BackgroundTasks) -> dict:
    background_tasks.add_task(asyncio.create_task, _sync_players_task())
    return {"status": "scheduled", "message": "Player sync has been scheduled in the background."}
