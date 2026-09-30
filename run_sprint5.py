import os
from src.nlp.parser import parse_analysis_text
from src.nlp.pros_cons_generator import generate_pros_cons
from src.analytics.cashflow_kpis import run_cashflow_intelligence
from src.reports.tearsheet import run_all_pdf_reports

def main():
    print("==========================================================")
    print("       STARTING SPRINT 5 EXECUTION (DAYS 29 - 35)         ")
    print("==========================================================\n")

    print("--- Day 29: Analysis Text Parser ---")
    parse_analysis_text()
    print()

    print("--- Day 30: Auto Pros/Cons Generator ---")
    generate_pros_cons()
    print()

    print("--- Day 31-32: Cash Flow Intelligence & Allocation ---")
    run_cashflow_intelligence()
    print()

    print("--- Day 33-35: Batch PDF Report Generation ---")
    run_all_pdf_reports()
    print()

    print("==========================================================")
    print("                 DEFINITION OF DONE CHECK                 ")
    print("==========================================================")
    
    tearsheets = len([f for f in os.listdir("reports/tearsheets") if f.endswith(".pdf")])
    sector_pdfs = len([f for f in os.listdir("reports/sector") if f.endswith(".pdf")])
    
    print(f"✔ Tearsheet PDFs: {tearsheets} / 92 generated")
    print(f"✔ Sector PDFs:    {sector_pdfs} / 11 generated")
    print(f"✔ Portfolio PDF:  {'EXISTS' if os.path.exists('reports/portfolio/portfolio_summary.pdf') else 'MISSING'}")
    print(f"✔ Cash Flow Excel:{'EXISTS' if os.path.exists('output/cashflow_intelligence.xlsx') else 'MISSING'}")
    print(f"✔ Pros/Cons CSV:  {'EXISTS' if os.path.exists('output/pros_cons_generated.csv') else 'MISSING'}")
    print("==========================================================")

if __name__ == "__main__":
    main()
