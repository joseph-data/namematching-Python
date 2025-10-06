# pip install rapidfuzz pandas
from difflib import SequenceMatcher

import pandas as pd

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover - exercised when rapidfuzz missing
    class _FallbackFuzz:
        @staticmethod
        def WRatio(a: str, b: str) -> float:
            return SequenceMatcher(None, a, b).ratio() * 100

    fuzz = _FallbackFuzz()

MATCH_THRESH = 0.85
POSSIBLE_THRESH = 0.75
DEFAULT_WEIGHTS = {
    "sim_last": 0.6,
    "sim_first": 0.3,
    "sim_city": 0.1,
}


def create_toy_data():
    """Return the toy dataframes used in the deterministic example."""
    left = pd.DataFrame(
        {
            "id_l": [1, 2, 3],
            "first": ["Joseph", "Jo", "Anne"],
            "last": ["Nyajuoga", "Smith", "Brown"],
            "dob": ["1994-05-02", "1988-11-20", "1990-01-01"],
            "city": ["Örebro", "Stockholm", "Gothenburg"],
        }
    )

    right = pd.DataFrame(
        {
            "id_r": [10, 11, 12],
            "first": ["Josef", "John", "Ann"],
            "last": ["Nyajuoga", "Smyth", "Brown"],
            "dob": ["1994-05-02", "1988-11-21", "1990-01-01"],
            "city": ["OREBRO", "Stockholm", "Göteborg"],
        }
    )

    return left, right


def norm(value):
    """Normalize strings while guarding against NaN."""
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Apply simple normalisation and derive the blocking key (year-of-birth)."""
    df = df.copy()
    df["first_n"] = df["first"].map(norm)
    df["last_n"] = df["last"].map(norm)
    df["city_n"] = df["city"].map(norm)
    df["yob"] = pd.to_datetime(df["dob"], errors="coerce").dt.year
    return df


def similarity(a: str, b: str) -> float:
    return fuzz.WRatio(a, b) / 100.0


def block_pairs(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    left_p = preprocess(left)
    right_p = preprocess(right)
    return left_p.merge(right_p, on="yob", how="inner", suffixes=("_l", "_r"))


def add_similarities(block: pd.DataFrame) -> pd.DataFrame:
    block = block.copy()
    if block.empty:
        block["sim_first"] = pd.Series(dtype=float)
        block["sim_last"] = pd.Series(dtype=float)
        block["sim_city"] = pd.Series(dtype=float)
        return block

    block["sim_first"] = block.apply(
        lambda row: similarity(row.first_n_l, row.first_n_r), axis=1
    )
    block["sim_last"] = block.apply(
        lambda row: similarity(row.last_n_l, row.last_n_r), axis=1
    )
    block["sim_city"] = block.apply(
        lambda row: similarity(row.city_n_l, row.city_n_r), axis=1
    )
    return block


def score_pairs(block: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    block = block.copy()
    weights = weights or DEFAULT_WEIGHTS
    block["score"] = 0.0
    for feature, wt in weights.items():
        block["score"] += wt * block.get(feature, 0)
    return block


def decide(score: float, match_thresh: float = MATCH_THRESH, possible_thresh: float = POSSIBLE_THRESH) -> str:
    if score >= match_thresh:
        return "match"
    if score >= possible_thresh:
        return "possible"
    return "non-match"


def assign_decisions(
    block: pd.DataFrame,
    match_thresh: float = MATCH_THRESH,
    possible_thresh: float = POSSIBLE_THRESH,
) -> pd.DataFrame:
    block = block.copy()
    block["decision"] = block["score"].map(
        lambda score: decide(score, match_thresh, possible_thresh)
    )
    return block


def deterministic_match(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    match_thresh: float = MATCH_THRESH,
    possible_thresh: float = POSSIBLE_THRESH,
    weights: dict | None = None,
) -> pd.DataFrame:
    block = block_pairs(left, right)
    block = add_similarities(block)
    block = score_pairs(block, weights)
    block = assign_decisions(block, match_thresh, possible_thresh)
    return block


def sweep_thresholds(
    scored_pairs: pd.DataFrame,
    match_thresholds: list[float],
    possible_thresh: float = POSSIBLE_THRESH,
) -> pd.DataFrame:
    """Return a summary of match/possible/non-match counts across thresholds."""
    results = []
    for match_t in match_thresholds:
        decisions = scored_pairs["score"].map(
            lambda score: decide(score, match_t, possible_thresh)
        )
        counts = decisions.value_counts()
        results.append(
            {
                "match_thresh": match_t,
                "possible_thresh": possible_thresh,
                "match": counts.get("match", 0),
                "possible": counts.get("possible", 0),
                "non-match": counts.get("non-match", 0),
            }
        )
    return pd.DataFrame(results)


def main() -> None:
    left, right = create_toy_data()
    scored = deterministic_match(left, right)
    cols = [
        "id_l",
        "first_l",
        "last_l",
        "id_r",
        "first_r",
        "last_r",
        "sim_first",
        "sim_last",
        "sim_city",
        "score",
        "decision",
    ]
    print(scored[cols].sort_values("score", ascending=False))


if __name__ == "__main__":
    main()