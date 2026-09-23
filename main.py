import sqlite3
import pandas as pd
from src.screener.engine import load_screener_config, run_screener_preset, export_screener_excel
from src.analytics.peer import compute_peer_percentiles
from src.analytics.radar import generate_radar_charts
from src.analytics.export_peer_excel import export_peer_comparison_excel

def main():
    print("--- Running N100 Financial Intelligence Platform (Sprint 3) ---")
    
    # 1. Load Financial Ratios
    conn = sqlite3.connect("data/n100_platform.db")
    df = pd.read_sql_query("SELECT * FROM financial_ratios WHERE year = 2024", conn)
    conn.close()
    
    # Add dummy sector if missing
    if "broad_sector" not in df.columns:
        df["broad_sector"] = "IT"

    # 2. Run Screener Presets
    config = load_screener_config()
    preset_results = {}
    for preset_name, rules in config["presets"].items():
        preset_df = run_screener_preset(df, rules)
        preset_results[preset_name] = preset_df
        print(f"✓ Preset [{preset_name}]: {len(preset_df)} companies passed")
        
    export_screener_excel(preset_results)
    
    # 3. Compute Peer Percentiles & Radar Charts
    compute_peer_percentiles()
    generate_radar_charts(df)
    export_peer_comparison_excel()
    
    print("--- Pipeline Execution Complete! Deliverables updated in output/ and reports/ ---")

if __name__ == "__main__":
    main()
