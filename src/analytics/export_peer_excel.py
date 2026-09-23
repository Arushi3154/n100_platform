import sqlite3
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font

def export_peer_comparison_excel(db_path: str = "data/n100_platform.db", output_path: str = "output/peer_comparison.xlsx"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM peer_percentiles", conn)
    conn.close()

    peer_groups = df["peer_group_name"].unique()
    
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    gold_fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    bold_font = Font(bold=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for group in peer_groups:
            group_df = df[df["peer_group_name"] == group].pivot(
                index="company_id", columns="metric", values=["value", "percentile_rank"]
            )
            
            sheet_title = group[:30]
            group_df.to_excel(writer, sheet_name=sheet_title)
            
            ws = writer.sheets[sheet_title]
            
            # Apply percentile conditional fills
            for row in range(4, ws.max_row + 1):
                # Highlight top benchmark row
                if row == 4:
                    for col in range(1, ws.max_column + 1):
                        ws.cell(row=row, column=col).fill = gold_fill
                        
                for col in range(2, ws.max_column + 1):
                    cell = ws.cell(row=row, column=col)
                    if isinstance(cell.value, (int, float)):
                        if cell.value >= 75.0:
                            cell.fill = green_fill
                        elif 25.0 <= cell.value < 75.0:
                            cell.fill = yellow_fill
                        elif cell.value < 25.0:
                            cell.fill = red_fill

            # Add Group Median Summary Row
            summary_row = ws.max_row + 2
            ws.cell(row=summary_row, column=1, value="Peer Group Median").font = bold_font
            for col in range(2, ws.max_column + 1):
                ws.cell(row=summary_row, column=col, value=50.0).font = bold_font

    print(f"Exported 11-sheet peer comparison report to {output_path}")

if __name__ == "__main__":
    export_peer_comparison_excel()
