"""Feature engineering for fantasy football predictions."""

import pandas as pd


class FeatureEngineer:
    """Build features from weekly game log data."""

    def __init__(self) -> None:
        self.feature_columns: list[str] = []

    def add_rolling_features(self, df: pd.DataFrame, windows: list[int] = [3, 5]) -> pd.DataFrame:
        df = df.copy()
        sort_columns = [col for col in ["player_id", "season", "week"] if col in df.columns]
        if sort_columns:
            df = df.sort_values(sort_columns)

        rolling_columns = ["fantasy_points_ppr", "target_share", "snap_count_pct", "air_yards_share"]
        for window in windows:
            for col in rolling_columns:
                if col not in df.columns:
                    continue
                feature_name = f"{col}_rolling_{window}"
                df[feature_name] = (
                    df.groupby("player_id")[col]
                    .rolling(window, min_periods=1)
                    .mean()
                    .reset_index(level=0, drop=True)
                )
        return df

    def add_opportunity_score(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["carries"] = df.get("carries", pd.Series(dtype="float"))
        df["targets"] = df.get("targets", pd.Series(dtype="float"))
        df["air_yards_share"] = df.get("air_yards_share", pd.Series(dtype="float"))

        def _score(row: pd.Series) -> float:
            position = str(row.get("position", "")).upper()
            carries = float(row.get("carries") or 0)
            targets = float(row.get("targets") or 0)
            air_share = float(row.get("air_yards_share") or 0)
            if position == "RB":
                return carries * 1.0 + targets * 0.5
            if position in {"WR", "TE"}:
                return targets * 1.0 + air_share * 10
            return 0.0

        df["opportunity_score"] = df.apply(_score, axis=1)
        return df

    def add_boom_bust_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["boom"] = (df.get("fantasy_points_ppr", 0) >= 25).astype(int)
        df["bust"] = (df.get("fantasy_points_ppr", 0) <= 5).astype(int)
        return df

    def add_schedule_difficulty(self, df: pd.DataFrame, schedules_df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        schedules_df = schedules_df.copy()

        if "season" in df.columns:
            seasons = sorted(df["season"].dropna().unique())
            last_seasons = seasons[-3:]
            schedules_df = schedules_df[schedules_df["season"].isin(last_seasons)]

        if {"opponent", "position", "points_allowed"}.issubset(schedules_df.columns):
            opponent_rank = (
                schedules_df.groupby(["opponent", "position"])["points_allowed"]
                .mean()
                .reset_index()
                .rename(columns={"points_allowed": "opponent_avg_points_allowed"})
            )
            df = df.merge(
                opponent_rank,
                how="left",
                on=["opponent", "position"],
            )
        else:
            df["opponent_avg_points_allowed"] = pd.NA

        df["sos_score"] = df["opponent_avg_points_allowed"].fillna(0.0)
        return df

    def build_feature_matrix(self, df: pd.DataFrame, schedules_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        df = self.add_rolling_features(df)
        df = self.add_opportunity_score(df)
        df = self.add_boom_bust_flags(df)
        df = self.add_schedule_difficulty(df, schedules_df)

        feature_cols = []
        for col in df.columns:
            if col in {"player_id", "season", "week", "opponent", "position", "name", "fantasy_points_ppr"}:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                feature_cols.append(col)

        self.feature_columns = [col for col in feature_cols if col != "fantasy_points_ppr"]
        X = df[self.feature_columns].copy()
        y = df["fantasy_points_ppr"].copy() if "fantasy_points_ppr" in df.columns else pd.Series(dtype="float")
        X = X.dropna()
        return X, y.loc[X.index]
