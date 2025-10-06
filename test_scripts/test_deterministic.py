import pandas as pd

from test_scripts.deterministic import (
    MATCH_THRESH,
    create_toy_data,
    deterministic_match,
    sweep_thresholds,
)


def test_records_with_missing_dob_are_excluded_by_blocking():
    left = pd.DataFrame(
        {
            "id_l": [1, 2],
            "first": ["Alice", "Beatrice"],
            "last": ["Andersson", "Berg"],
            "dob": ["1990-01-01", None],
            "city": ["Stockholm", "Uppsala"],
        }
    )
    right = pd.DataFrame(
        {
            "id_r": [10, 11],
            "first": ["Alicia", "Bea"],
            "last": ["Andersson", "Berg"],
            "dob": ["1990-01-01", "1985-06-06"],
            "city": ["Stockholm", "Uppsala"],
        }
    )

    scored = deterministic_match(left, right)

    assert len(scored) == 1
    assert int(scored.iloc[0]["id_l"]) == 1


def test_threshold_sweep_matches_default_decisions():
    left, right = create_toy_data()
    scored = deterministic_match(left, right)

    summary = sweep_thresholds(scored, [MATCH_THRESH, MATCH_THRESH - 0.1])
    summary_by_thresh = summary.set_index("match_thresh")

    default_counts = scored["decision"].value_counts()
    default_row = summary_by_thresh.loc[MATCH_THRESH]

    assert default_row["match"] == default_counts.get("match", 0)
    assert default_row["possible"] == default_counts.get("possible", 0)
    assert default_row["non-match"] == default_counts.get("non-match", 0)

    total_pairs = len(scored)
    for _, row in summary.iterrows():
        assert row["match"] + row["possible"] + row["non-match"] == total_pairs

    lower_threshold_row = summary_by_thresh.loc[MATCH_THRESH - 0.1]
    assert lower_threshold_row["match"] >= default_row["match"]

    assert summary.shape[0] == 2
