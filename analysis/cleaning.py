import pandas as pd
import os

INPUT = "csv"
OUTPUT = "data/cleaned"

os.makedirs(OUTPUT, exist_ok=True)

files = [
    "standard.csv",
    "shooting.csv",
    "time.csv",
    "goalkeeping.csv",
    "miscellaneous.csv"
]

for file in files:
    print(f"Cleaning {file}...")

    # FBref CSVs usually have 2 header rows
    df = pd.read_csv(
        os.path.join(INPUT, file),
        header=[0, 1]
    )

    # Flatten the MultiIndex columns
    df.columns = [
        "_".join([str(x) for x in col if "Unnamed" not in str(x)]).strip("_")
        for col in df.columns
    ]

    # Remove repeated header rows inside the data
    if "Player" in df.columns:
        df = df[df["Player"] != "Player"]

    out = os.path.join(OUTPUT, file)

    df.to_csv(out, index=False)

    print(f"Saved -> {out}")