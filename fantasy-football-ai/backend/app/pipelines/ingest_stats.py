"""Statistics ingestion pipeline."""

import asyncio
from typing import List

import pandas as pd
from prefect import flow, task
from sqlalchemy import select

from ..database import AsyncSessionLocal
from ..models.game import GameLog
from ..models.player import Player
from ..services.nfl_data_service import nfl_data_service


@task
def fetch_weekly_stats(seasons: List[int]) -> pd.DataFrame:
    return nfl_data_service.get_weekly_stats(seasons)


@task
def fetch_snap_counts(seasons: List[int]) -> pd.DataFrame:
    return nfl_data_service.get_snap_counts(seasons)


@task
def merge_stats(weekly_df: pd.DataFrame, snaps_df: pd.DataFrame) -> pd.DataFrame:
    merged_df = weekly_df.merge(
        snaps_df,
        how="left",
        on=["player_id", "season", "week"],
        suffixes=("", "_snap"),
    )
    return merged_df


async def _save_to_database_async(merged_df: pd.DataFrame) -> None:
    async with AsyncSessionLocal() as session:
        for _, row in merged_df.iterrows():
            sleeper_id = row.get("sleeper_id") or row.get("player_id")
            season = int(row["season"])
            week = int(row["week"])

            if not sleeper_id:
                continue

            player_stmt = select(Player).where(Player.sleeper_id == sleeper_id)
            player_result = await session.execute(player_stmt)
            player = player_result.scalar_one_or_none()
            if player is None:
                continue

            game_stmt = select(GameLog).where(
                GameLog.player_id == player.id,
                GameLog.season == season,
                GameLog.week == week,
            )
            game_result = await session.execute(game_stmt)
            game_log = game_result.scalar_one_or_none()

            payload = {
                "player_id": player.id,
                "season": season,
                "week": week,
                "opponent": row.get("opponent"),
                "fantasy_points_ppr": row.get("fantasy_points_ppr"),
                "receptions": row.get("receptions"),
                "targets": row.get("targets"),
                "receiving_yards": row.get("receiving_yards"),
                "receiving_tds": row.get("receiving_tds"),
                "carries": row.get("carries"),
                "rushing_yards": row.get("rushing_yards"),
                "rushing_tds": row.get("rushing_tds"),
                "passing_yards": row.get("passing_yards"),
                "passing_tds": row.get("passing_tds"),
                "interceptions": row.get("interceptions"),
                "snap_count_pct": row.get("snap_count_pct"),
                "target_share": row.get("target_share"),
                "air_yards_share": row.get("air_yards_share"),
            }

            if game_log is None:
                game_log = GameLog(**payload)
                session.add(game_log)
            else:
                for key, value in payload.items():
                    setattr(game_log, key, value)
                session.add(game_log)
        await session.commit()


@task
def save_to_database(merged_df: pd.DataFrame) -> None:
    asyncio.run(_save_to_database_async(merged_df))


@flow(name="ingest_nfl_stats")
def ingest_nfl_stats(seasons: List[int]) -> pd.DataFrame:
    weekly_df = fetch_weekly_stats(seasons)
    snaps_df = fetch_snap_counts(seasons)
    merged_df = merge_stats(weekly_df, snaps_df)
    save_to_database(merged_df)
    return merged_df


if __name__ == "__main__":
    ingest_nfl_stats([2024])
