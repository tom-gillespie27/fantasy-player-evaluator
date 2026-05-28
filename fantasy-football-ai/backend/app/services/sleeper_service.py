"""Sleeper API integration service."""

import logging

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class SleeperService:
    """Async client for Sleeper API integration."""

    def __init__(self) -> None:
        self.base_url = settings.SLEEPER_BASE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def get_all_players(self) -> dict:
        """Fetch the full Sleeper NFL player map.

        This endpoint is heavy (~5MB), so cache the result in Redis with a 24-hour TTL.
        """
        endpoint = "/players/nfl"
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Sleeper get_all_players failed: %s", exc)
            raise RuntimeError(
                f"Failed to fetch all players from Sleeper: {exc.response.status_code} {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Sleeper get_all_players request failed: %s", exc)
            raise RuntimeError(f"Sleeper request failed while fetching all players: {exc}") from exc

    async def get_player(self, player_id: str) -> dict:
        endpoint = f"/players/nfl/{player_id}"
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Sleeper get_player(%s) failed: %s", player_id, exc)
            raise RuntimeError(
                f"Failed to fetch player {player_id} from Sleeper: {exc.response.status_code} {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Sleeper get_player(%s) request failed: %s", player_id, exc)
            raise RuntimeError(
                f"Sleeper request failed while fetching player {player_id}: {exc}"
            ) from exc

    async def get_trending_players(self, type: str = "add", limit: int = 25) -> list:
        endpoint = f"/players/nfl/trending/{type}"
        params = {"limit": limit}
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Sleeper get_trending_players(%s, %s) failed: %s", type, limit, exc)
            raise RuntimeError(
                f"Failed to fetch trending players from Sleeper: {exc.response.status_code} {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Sleeper get_trending_players(%s, %s) request failed: %s", type, limit, exc)
            raise RuntimeError(
                f"Sleeper request failed while fetching trending players: {exc}"
            ) from exc

    async def get_adp(self, season: str, position: str = "ALL") -> list:
        endpoint = f"/stats/nfl/player/{season}"
        params = {"season_type": "regular", "position": position}
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Sleeper get_adp(%s, %s) failed: %s", season, position, exc)
            raise RuntimeError(
                f"Failed to fetch ADP data from Sleeper for season {season}: {exc.response.status_code} {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Sleeper get_adp(%s, %s) request failed: %s", season, position, exc)
            raise RuntimeError(
                f"Sleeper request failed while fetching ADP data: {exc}"
            ) from exc


sleeper_service = SleeperService()
