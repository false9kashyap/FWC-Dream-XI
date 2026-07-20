import pandas as pd
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("data/final/master_dataset.csv")

# Fill NaN
df = df.fillna(0)

# Normalize
cols = [
    "Performance_Gls",
    "Performance_Ast",
    "Standard_Sh",
    "Standard_SoT",
    "Performance_TklW",
    "Performance_Int",
    "Playing Time_Min"
]

scaler = MinMaxScaler()

df[cols] = scaler.fit_transform(df[cols])

# Initialize score
df["Score"] = pd.Series(0.0, index=df.index)

# Forward
fw = df["Pos"].str.contains("FW", na=False)

df.loc[fw,"Score"] = (
    0.45*df.loc[fw,"Performance_Gls"] +
    0.20*df.loc[fw,"Performance_Ast"] +
    0.20*df.loc[fw,"Standard_Sh"] +
    0.15*df.loc[fw,"Standard_SoT"]
)

# Midfielder
mf = df["Pos"].str.contains("MF", na=False)

df.loc[mf, "Score"] = (
    0.30 * df.loc[mf, "Performance_Ast"] +
    0.30 * df.loc[mf, "Performance_Gls"] +
    0.20 * df.loc[mf, "Performance_TklW"] +
    0.10 * df.loc[mf, "Performance_Int"] +
    0.10 * df.loc[mf, "Playing Time_Min"]
)

# Defender
dfn = df["Pos"].str.contains("DF", na=False)

df.loc[dfn,"Score"] = (
    0.45*df.loc[dfn,"Performance_TklW"] +
    0.35*df.loc[dfn,"Performance_Int"] +
    0.20*df.loc[dfn,"Playing Time_Min"]
)

df.to_csv("data/final/outfield_rankings.csv",index=False)

print("Scoring Complete!")