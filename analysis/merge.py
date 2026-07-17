import pandas as pd
import os

# Load cleaned files
std = pd.read_csv("data/cleaned/standard_stats.csv")
shoot = pd.read_csv("data/cleaned/shooting.csv")
misc = pd.read_csv("data/cleaned/miscellaneous.csv")
play = pd.read_csv("data/cleaned/playing_time.csv")

# Merge on Player
df = std.merge(
    shoot[["Player","Standard_Sh","Standard_SoT"]],
    on="Player",
    how="left"
)

df = df.merge(
    misc[["Player","Performance_TklW","Performance_Int"]],
    on="Player",
    how="left"
)

df = df.merge(
    play[["Player","Playing Time_Min"]],
    on="Player",
    how="left",
    suffixes=("","_play")
)

os.makedirs("data/final", exist_ok=True)

df.to_csv("data/final/master_dataset.csv",index=False)

print(df.head())
print("\nMaster Dataset Created!")