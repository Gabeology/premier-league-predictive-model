import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd

# 1. Connect to your local MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sql-passwd1",  # <-- Put your actual MySQL password here
    database="premier_league_26",
)

# 2. Query your complete dataset with shortened transfer strings to fit the table
query = """
    SELECT 
        ROW_NUMBER() OVER (ORDER BY (30 + (ts.goals * 3) + (t.clean_sheets * 2) + 
            CASE 
                WHEN m.transfer_summary LIKE '%In%' AND m.transfer_summary NOT LIKE '%Loan%' THEN 5
                WHEN m.transfer_summary LIKE '%Out%' THEN -3
                ELSE 0 
            END) DESC) AS Pos,
        t.team_name AS Team,
        ts.player_name AS Top_Scorer,
        ts.goals AS Goals,
        t.clean_sheets AS CS,
        SUBSTRING_INDEX(m.transfer_summary, ' (', 1) AS Key_Transfer,
        (30 + (ts.goals * 3) + (t.clean_sheets * 2) + 
            CASE 
                WHEN m.transfer_summary LIKE '%In%' AND m.transfer_summary NOT LIKE '%Loan%' THEN 5
                WHEN m.transfer_summary LIKE '%Out%' THEN -3
                ELSE 0 
            END) AS Pts
    FROM teams t
    JOIN top_scorers ts ON t.team_name = ts.team_name
    LEFT JOIN major_transfers m ON t.team_name = m.team_name
    ORDER BY Pts DESC;
"""

# Load data into a pandas DataFrame
df = pd.read_sql(query, con=db_connection)
db_connection.close()

# 3. Create a dark-themed visual table window (width=16, height=9)
fig, ax = plt.subplots(figsize=(16, 9))

# Set dark background color for the entire figure and axes window
fig.patch.set_facecolor("#121212")
ax.set_facecolor("#121212")
ax.axis("off")

# Render the dataframe as a table
table = ax.table(
    cellText=df.values,
    colLabels=df.columns,
    cellLoc="center",
    loc="center",
)

# Scale layout to give text plenty of breathing room
table.scale(1.0, 1.6)
table.auto_set_font_size(False)
table.set_fontsize(10)

# Adjust specific column widths
col_widths = [0.06, 0.18, 0.22, 0.10, 0.08, 0.26, 0.10]

# Dark Theme & Custom Color-Coding Logic
for (row, col), cell in table.get_celld().items():
  cell.set_width(col_widths[col])

  if row == 0:
    # Header styling (Dark modern blue header with crisp white text)
    cell.set_facecolor("#1f6feb")
    cell.set_text_props(weight="bold", color="white")
  else:
    # Text color default for dark mode
    cell.set_text_props(color="#e0e0e0")

    # 1. Position-based zone coloring (Top 4 Green, Bottom 4 Red)
    if col == 0:  # Position column highlighting
      if row in [1, 2, 3, 4]:  # Top 4 (Muted Emerald Green)
        cell.set_facecolor("#1b4332")
        cell.set_text_props(weight="bold", color="#52b788")
      elif row >= 17:  # Bottom 4 Relegation (Muted Dark Red)
        cell.set_facecolor("#4a151b")
        cell.set_text_props(weight="bold", color="#f28b82")
      else:
        cell.set_facecolor("#1e1e1e")

    # 2. Clean Sheets column highlighting (Arsenal's 19 CS gets a vibrant gold accent)
    elif col == 4:  # CS Column
      val = cell.get_text().get_text()
      if val == "19":  # Highlight Arsenal's 19 clean sheets
        cell.set_facecolor("#3b2f00")
        cell.set_text_props(weight="bold", color="#ffd700")
      else:
        cell.set_facecolor("#1e1e1e")

    # 3. Transfer column highlighting (Explicit checking for Niclas and Bruno with distinct colors)
    elif col == 5:  # Key_Transfer column
      transfer_text = cell.get_text().get_text()
      if "Bruno" in transfer_text:
        cell.set_facecolor(
            "#082032"
        )  # Distinct Deep Blue/Teal accent for Best Transfer In
        cell.set_text_props(weight="bold", color="#38bdf8")
      elif "Niclas" in transfer_text or "Füllkrug" in transfer_text:
        cell.set_facecolor(
            "#4a121a"
        )  # Distinct Vibrant Dark Red/Magenta accent for Worst Transfer Out
        cell.set_text_props(weight="bold", color="#ff5c5c")
      else:
        cell.set_facecolor("#1e1e1e")

    # 4. Standard rows background fallback
    else:
      if row % 2 == 0:
        cell.set_facecolor("#181818")
      else:
        cell.set_facecolor("#1e1e1e")

plt.title(
    "Premier League 2026/27 - Advanced Predictive Standings Model",
    fontsize=15,
    fontweight="bold",
    color="white",
    pad=25,
)

plt.tight_layout()

# Save the updated dark-mode image
plt.savefig(
    "premier_league_full_table_chart.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=fig.get_facecolor(),
    edgecolor="none",
)

# Show the interactive window
plt.show()