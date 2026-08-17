"""
Power BI Data Preparation Script
Generates clean, Power BI-optimized CSV files with human-readable column names.
"""
import csv
import os

# Paths
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(BASE)
MASTER_CSV = os.path.join(PROJECT, "data", "final", "master_dataset.csv")
OUTFIELD_CSV = os.path.join(PROJECT, "data", "final", "outfield_rankings.csv")
DREAM_CSV = os.path.join(PROJECT, "data", "final", "dream_xi.csv")
GK_CSV = os.path.join(PROJECT, "data", "cleaned", "goalkeepers.csv")
OUTPUT_DIR = os.path.join(PROJECT, "dashboard", "powerbi_data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Player", "").strip():
                rows.append(row)
    return rows

def safe_float(v, default=0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default

def safe_int(v, default=0):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return default

def parse_nation(squad):
    """Extract nation code and name from Squad field like 'fr France'"""
    if not squad:
        return "", ""
    parts = squad.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", squad

def parse_club(club):
    """Remove league prefix like '1.eng ' from club name"""
    if not club:
        return ""
    import re
    return re.sub(r'^\d+\.\w+\s+', '', club)

def parse_age(age_str):
    """Extract age in years from '25-268' format"""
    if not age_str:
        return 0
    parts = age_str.split("-")
    return safe_int(parts[0])

# ============================================================
# 1. ALL PLAYERS TABLE (for Power BI main table)
# ============================================================
print("Loading master dataset...")
master = read_csv(MASTER_CSV)

print("Loading outfield rankings...")
outfield = read_csv(OUTFIELD_CSV)
score_map = {}
for row in outfield:
    name = row.get("Player", "").strip()
    if name:
        score_map[name] = safe_float(row.get("Score", 0))

print("Loading Dream XI...")
dream_xi = read_csv(DREAM_CSV)
dream_names = set()
dream_scores = {}
for row in dream_xi:
    name = row.get("Player", "").strip()
    if name:
        dream_names.add(name)
        dream_scores[name] = safe_float(row.get("Score", 0))

print("Loading goalkeepers...")
gk_data = read_csv(GK_CSV)
gk_map = {}
for row in gk_data:
    name = row.get("Player", "").strip()
    if name:
        gk_map[name] = row

# Build clean all-players table
all_players = []
for row in master:
    name = row.get("Player", "").strip()
    if not name:
        continue
    
    nation_code, nation_name = parse_nation(row.get("Squad", ""))
    club = parse_club(row.get("Club", ""))
    pos = row.get("Pos", "")
    age = parse_age(row.get("Age", ""))
    
    score = dream_scores.get(name, score_map.get(name, 0))
    is_dream = "Yes" if name in dream_names else "No"
    
    minutes = safe_float(row.get("Playing Time_Min_play", 0)) or safe_float(row.get("Playing Time_Min", 0))
    
    player = {
        "Player": name,
        "Position": pos,
        "Nation Code": nation_code,
        "Nation": nation_name,
        "Club": club,
        "Age": age,
        "Born": row.get("Born", ""),
        "Matches Played": safe_int(row.get("Playing Time_MP", 0)),
        "Starts": safe_int(row.get("Playing Time_Starts", 0)),
        "Minutes Played": safe_int(minutes),
        "90s Played": round(safe_float(row.get("Playing Time_90s", 0)), 1),
        "Goals": safe_int(row.get("Performance_Gls", 0)),
        "Assists": safe_int(row.get("Performance_Ast", 0)),
        "Goals + Assists": safe_int(row.get("Performance_G+A", 0)),
        "Non-Penalty Goals": safe_int(row.get("Performance_G-PK", 0)),
        "Penalties Scored": safe_int(row.get("Performance_PK", 0)),
        "Penalties Attempted": safe_int(row.get("Performance_PKatt", 0)),
        "Yellow Cards": safe_int(row.get("Performance_CrdY", 0)),
        "Red Cards": safe_int(row.get("Performance_CrdR", 0)),
        "Goals per 90": round(safe_float(row.get("Per 90 Minutes_Gls", 0)), 2),
        "Assists per 90": round(safe_float(row.get("Per 90 Minutes_Ast", 0)), 2),
        "G+A per 90": round(safe_float(row.get("Per 90 Minutes_G+A", 0)), 2),
        "Shots": safe_int(row.get("Standard_Sh", 0)),
        "Shots on Target": safe_int(row.get("Standard_SoT", 0)),
        "Tackles Won": safe_int(row.get("Performance_TklW", 0)),
        "Interceptions": safe_int(row.get("Performance_Int", 0)),
        "Score": round(score, 4),
        "Dream XI": is_dream,
    }
    all_players.append(player)

# Sort by score descending
all_players.sort(key=lambda x: x["Score"], reverse=True)

# Add rank
for i, p in enumerate(all_players):
    p["Rank"] = i + 1

# Reorder columns with Rank first
columns_order = ["Rank"] + [k for k in all_players[0].keys() if k != "Rank"]

output_path = os.path.join(OUTPUT_DIR, "AllPlayers.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns_order)
    writer.writeheader()
    writer.writerows(all_players)
print(f"  -> AllPlayers.csv: {len(all_players)} rows")


# ============================================================
# 2. DREAM XI TABLE (separate table for slicers/highlights)
# ============================================================
dream_players = [p for p in all_players if p["Dream XI"] == "Yes"]

# Add position group for nice display
for p in dream_players:
    pos = p["Position"]
    if "GK" in pos:
        p["Position Group"] = "Goalkeeper"
        p["Formation Slot"] = 1
    elif "DF" in pos:
        p["Position Group"] = "Defender"
        p["Formation Slot"] = 2
    elif "MF" in pos:
        p["Position Group"] = "Midfielder"
        p["Formation Slot"] = 3
    elif "FW" in pos:
        p["Position Group"] = "Forward"
        p["Formation Slot"] = 4
    else:
        p["Position Group"] = "Other"
        p["Formation Slot"] = 5

dream_columns = columns_order + ["Position Group", "Formation Slot"]

output_path = os.path.join(OUTPUT_DIR, "DreamXI.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=dream_columns)
    writer.writeheader()
    writer.writerows(dream_players)
print(f"  -> DreamXI.csv: {len(dream_players)} rows")


# ============================================================
# 3. GOALKEEPERS TABLE (separate for GK-specific visuals)
# ============================================================
gk_players = []
for row in gk_data:
    name = row.get("Player", "").strip()
    if not name:
        continue
    nation_code, nation_name = parse_nation(row.get("Squad", ""))
    club = parse_club(row.get("Club", ""))
    
    gk_players.append({
        "Player": name,
        "Nation": nation_name,
        "Club": club,
        "Matches Played": safe_int(row.get("Playing Time_MP", 0)),
        "Minutes Played": safe_int(row.get("Playing Time_Min", 0)),
        "Goals Against": safe_int(row.get("Performance_GA", 0)),
        "Goals Against per 90": round(safe_float(row.get("Performance_GA90", 0)), 2),
        "Shots on Target Against": safe_int(row.get("Performance_SoTA", 0)),
        "Saves": safe_int(row.get("Performance_Saves", 0)),
        "Save %": round(safe_float(row.get("Performance_Save%", 0)), 1),
        "Wins": safe_int(row.get("Performance_W", 0)),
        "Draws": safe_int(row.get("Performance_D", 0)),
        "Losses": safe_int(row.get("Performance_L", 0)),
        "Clean Sheets": safe_int(row.get("Performance_CS", 0)),
        "Clean Sheet %": round(safe_float(row.get("Performance_CS%", 0)), 1),
        "PK Faced": safe_int(row.get("Penalty Kicks_PKatt", 0)),
        "PK Goals Allowed": safe_int(row.get("Penalty Kicks_PKA", 0)),
        "PK Saved": safe_int(row.get("Penalty Kicks_PKsv", 0)),
        "Dream XI": "Yes" if name in dream_names else "No",
    })

output_path = os.path.join(OUTPUT_DIR, "Goalkeepers.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=gk_players[0].keys())
    writer.writeheader()
    writer.writerows(gk_players)
print(f"  -> Goalkeepers.csv: {len(gk_players)} rows")


# ============================================================
# 4. SCORING WEIGHTS TABLE (for methodology visual)
# ============================================================
weights = [
    {"Position": "Forward", "Metric": "Goals", "Weight": 0.45},
    {"Position": "Forward", "Metric": "Assists", "Weight": 0.20},
    {"Position": "Forward", "Metric": "Shots", "Weight": 0.20},
    {"Position": "Forward", "Metric": "Shots on Target", "Weight": 0.15},
    {"Position": "Midfielder", "Metric": "Goals", "Weight": 0.30},
    {"Position": "Midfielder", "Metric": "Assists", "Weight": 0.30},
    {"Position": "Midfielder", "Metric": "Tackles Won", "Weight": 0.20},
    {"Position": "Midfielder", "Metric": "Interceptions", "Weight": 0.10},
    {"Position": "Midfielder", "Metric": "Minutes Played", "Weight": 0.10},
    {"Position": "Defender", "Metric": "Tackles Won", "Weight": 0.45},
    {"Position": "Defender", "Metric": "Interceptions", "Weight": 0.35},
    {"Position": "Defender", "Metric": "Minutes Played", "Weight": 0.20},
    {"Position": "Goalkeeper", "Metric": "Save %", "Weight": 0.45},
    {"Position": "Goalkeeper", "Metric": "Clean Sheets", "Weight": 0.35},
    {"Position": "Goalkeeper", "Metric": "Saves", "Weight": 0.20},
    {"Position": "Goalkeeper", "Metric": "Goals Against (penalty)", "Weight": -0.15},
]

output_path = os.path.join(OUTPUT_DIR, "ScoringWeights.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Position", "Metric", "Weight"])
    writer.writeheader()
    writer.writerows(weights)
print(f"  -> ScoringWeights.csv: {len(weights)} rows")


# ============================================================
# 5. POSITION SUMMARY TABLE (for KPI cards)
# ============================================================
from collections import defaultdict

pos_stats = defaultdict(lambda: {"Count": 0, "Goals": 0, "Assists": 0, "Minutes": 0})
for p in all_players:
    pos = p["Position"]
    if "GK" in pos:
        grp = "Goalkeeper"
    elif "DF" in pos:
        grp = "Defender"
    elif "MF" in pos:
        grp = "Midfielder"
    elif "FW" in pos:
        grp = "Forward"
    else:
        grp = "Other"
    pos_stats[grp]["Count"] += 1
    pos_stats[grp]["Goals"] += p["Goals"]
    pos_stats[grp]["Assists"] += p["Assists"]
    pos_stats[grp]["Minutes"] += p["Minutes Played"]

summary = []
for grp, stats in sorted(pos_stats.items()):
    summary.append({
        "Position Group": grp,
        "Player Count": stats["Count"],
        "Total Goals": stats["Goals"],
        "Total Assists": stats["Assists"],
        "Total Minutes": stats["Minutes"],
    })

output_path = os.path.join(OUTPUT_DIR, "PositionSummary.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)
print(f"  -> PositionSummary.csv: {len(summary)} rows")


# ============================================================
# 6. TOP PERFORMERS TABLE (pre-computed top lists)
# ============================================================
# Top 15 scorers
top_scorers = sorted([p for p in all_players if p["Goals"] > 0], key=lambda x: (-x["Goals"], -x["Goals per 90"]))[:15]
for i, p in enumerate(top_scorers):
    p["Goals Rank"] = i + 1

# Top 15 assisters
top_assists = sorted([p for p in all_players if p["Assists"] > 0], key=lambda x: (-x["Assists"], -x["Assists per 90"]))[:15]
for i, p in enumerate(top_assists):
    p["Assists Rank"] = i + 1

# Combine into one table
top_performers = []
seen = set()
for p in top_scorers + top_assists:
    name = p["Player"]
    if name not in seen:
        top_performers.append({
            "Player": p["Player"],
            "Position": p["Position"],
            "Nation": p["Nation"],
            "Club": p["Club"],
            "Goals": p["Goals"],
            "Assists": p["Assists"],
            "G+A": p["Goals + Assists"],
            "Goals per 90": p["Goals per 90"],
            "Assists per 90": p["Assists per 90"],
            "Shots": p["Shots"],
            "Shots on Target": p["Shots on Target"],
            "Minutes Played": p["Minutes Played"],
            "Dream XI": p["Dream XI"],
            "Goals Rank": p.get("Goals Rank", ""),
            "Assists Rank": p.get("Assists Rank", ""),
        })
        seen.add(name)

output_path = os.path.join(OUTPUT_DIR, "TopPerformers.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=top_performers[0].keys())
    writer.writeheader()
    writer.writerows(top_performers)
print(f"  -> TopPerformers.csv: {len(top_performers)} rows")


print(f"\n✅ All Power BI data files created in: {OUTPUT_DIR}")
print("   Import these CSVs into Power BI Desktop using Get Data > Text/CSV")
