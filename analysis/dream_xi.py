import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load data
gk = pd.read_csv("data/cleaned/goalkeepers.csv")
out = pd.read_csv("data/final/outfield_rankings.csv")

# ======================================================
# GOALKEEPER SCORING
# ======================================================

gk["Performance_Save%"] = pd.to_numeric(gk["Performance_Save%"], errors="coerce").fillna(0)
gk["Performance_Saves"] = pd.to_numeric(gk["Performance_Saves"], errors="coerce").fillna(0)
gk["Performance_CS"] = pd.to_numeric(gk["Performance_CS"], errors="coerce").fillna(0)
gk["Performance_GA"] = pd.to_numeric(gk["Performance_GA"], errors="coerce").fillna(0)

gk_scaler = MinMaxScaler()

gk_cols = [
    "Performance_Saves",
    "Performance_Save%",
    "Performance_CS",
    "Performance_GA"
]

gk[gk_cols] = gk_scaler.fit_transform(gk[gk_cols])

# Lower goals against is better
gk["Score"] = (
    0.20 * gk["Performance_Saves"] +
    0.45 * gk["Performance_Save%"] +
    0.35 * gk["Performance_CS"] -
    0.15 * gk["Performance_GA"]
)

best_gk = gk.nlargest(1, "Score")

# ======================================================
# DEFENDER RE-RANKING
# ======================================================

best_df = out[out["Pos"].str.contains("DF", na=False)].copy()

df_scaler = MinMaxScaler()

def_cols = [
    "Performance_TklW",
    "Performance_Int",
    "Performance_Ast",
    "Playing Time_Min"
]

best_df[def_cols] = df_scaler.fit_transform(best_df[def_cols])

best_df["Score"] = (
    0.30 * best_df["Performance_TklW"] +
    0.25 * best_df["Performance_Int"] +
    0.20 * best_df["Performance_Ast"] +
    0.25 * best_df["Playing Time_Min"]
)

best_df = best_df.nlargest(4, "Score")

# ======================================================
# MIDFIELDERS & FORWARDS
# ======================================================

best_mf = out[out["Pos"].str.contains("MF", na=False)].nlargest(3, "Score")

best_fw = out[out["Pos"].str.contains("FW", na=False)].nlargest(3, "Score")

# ======================================================
# DREAM XI
# ======================================================

dream = pd.concat(
    [best_gk, best_df, best_mf, best_fw],
    ignore_index=True
)

dream.to_csv("data/final/dream_xi.csv", index=False)

print("\n========== DREAM XI ==========\n")
print(dream[["Player", "Pos", "Score"]])