"""NFL data integration service."""

import pandas as pd
import nfl_data_py as nfl


class NFLDataService:
    """Service wrapper around nfl_data_py data imports."""

    def get_seasonal_stats(self, seasons: list[int]) -> pd.DataFrame:
        return nfl.import_seasonal_stats(seasons, s_type="REG")

    def get_weekly_stats(self, seasons: list[int]) -> pd.DataFrame:
        return nfl.import_weekly_stats(seasons, s_type="REG")

    def get_rosters(self, seasons: list[int]) -> pd.DataFrame:
        return nfl.import_rosters(seasons)

    def get_schedules(self, seasons: list[int]) -> pd.DataFrame:
        return nfl.import_schedules(seasons)

    def get_snap_counts(self, seasons: list[int]) -> pd.DataFrame:
        return nfl.import_snap_counts(seasons)


nfl_data_service = NFLDataService()
