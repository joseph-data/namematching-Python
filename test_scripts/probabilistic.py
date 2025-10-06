# pip install recordlinkage pandas
import pandas as pd
import recordlinkage as rl

left = pd.DataFrame(
    {
        "id_l": [1, 2, 3, 4],
        "first": ["Joseph", "Jo", "Anne", "Maya"],
        "last": ["Nyajuoga", "Smith", "Brown", "Lind"],
        "dob": ["1994-05-02", "1988-11-20", "1990-01-01", "1992-03-01"],
        "zip": ["70210", "11120", "41105", "12630"],
    }
).set_index("id_l")

right = pd.DataFrame(
    {
        "id_r": [101, 102, 103, 104],
        "first": ["Josef", "John", "Ann", "Maja"],
        "last": ["Nyajuoga", "Smyth", "Brown", "Lindh"],
        "dob": ["1994-05-02", "1988-11-21", "1990-01-01", "1992-03-01"],
        "zip": ["70210", "11121", "41105", "12630"],
    }
).set_index("id_r")

# --- 1) Indexing / Blocking (by zip code to shrink pairs) ---
indexer = rl.Index()
indexer.block("zip")
candidates = indexer.index(left, right)  # MultiIndex of pair candidates

# --- 2) Compare fields to produce feature vectors (0..1) ---
comp = rl.Compare()
comp.string("first", "first", method="jarowinkler", threshold=0.85, label="first_sim")
comp.string("last", "last", method="jarowinkler", threshold=0.90, label="last_sim")
comp.exact("dob", "dob", label="dob_eq")

features = comp.compute(candidates, left, right)
# features is a DataFrame with columns like first_sim, last_sim, dob_eq

# --- 3) Probabilistic classifier (Fellegi–Sunter via EM) ---
# No labels needed; it estimates m/u parameters from the data.
ecm = rl.ECMClassifier(
    binarize=None
)  # keep similarities as-is; ECM handles probabilities
ecm.fit(features)
matches = ecm.predict(features)

# --- 4) Inspect matches & (optionally) posterior probabilities ---
posterior = ecm.prob(features)  # P(match | features)
out = (
    posterior.to_frame("p_match")
    .join(left, how="left")
    .join(right, how="left")
    .reset_index()
)
print(out.sort_values("p_match", ascending=False).head(10))
