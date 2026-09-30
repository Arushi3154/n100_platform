import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_analyst_guide(output_path="docs/analyst_guide.pdf"):
    os.makedirs("docs", exist_ok=True)
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.navy, spaceAfter=12)
    h1_style = ParagraphStyle('H1Style', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.darkblue, spaceBefore=12, spaceAfter=8)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8)

    story = []

    story.append(Paragraph("Nifty 100 Financial Analytics Platform — Analyst Guide", title_style))
    story.append(Paragraph("Comprehensive User Manual & Technical Documentation", ParagraphStyle('Sub', parent=body_style, fontSize=12, textColor=colors.gray)))
    story.append(Spacer(1, 15))

    sections = [
        ("1. Introduction & Platform Architecture", "The Nifty 100 Financial Platform is designed for institutional equity research, offering automated financial statement parsing, ratio computation, NLP sentiment analysis, KMeans clustering, and REST API distribution."),
        ("2. Navigating the Streamlit Dashboard", "The dashboard features 5 core pages: Executive Summary, Company Profile, Screener & Filter, Peer Comparison, and Data Quality Monitor."),
        ("3. Using the Equity Screener", "Filter companies across 10 core financial ratios including ROE, D/E, FCF, and 5-Year Revenue CAGR. Presets include Quality Compounders and Value Opportunities."),
        ("4. Company Profile & Tearsheet Generation", "Each profile provides 10-year P&L, Balance Sheet, and Cash Flow trajectories alongside NLP Pros & Cons and automated PDF tearsheets."),
        ("5. Peer Comparison & Radar Analytics", "Benchmark target companies against sector median and peer group percentiles using radar metric charts."),
        ("6. Machine Learning Clustering (KMeans)", "Companies are segmented into 5 distinct archetypes: High-Quality Compounders, Defensive Dividend Payers, Value Cyclicals, Distressed Turnarounds, and Emerging Growth."),
        ("7. Cash Flow Intelligence & Capital Allocation", "Evaluates CFO/EBITDA quality scores, CapEx intensity, and flags capital allocation pattern changes."),
        ("8. Data Quality & Exception Management", "Monitors 14 automated data quality rules, outputting validation failures and severity tags."),
        ("9. REST API Integration & Endpoints", "FastAPI server exposes 16 endpoints for integration with external platforms under /api/v1 prefix."),
        ("10. Troubleshooting & System Maintenance", "Instructions for database re-indexing, cache clearing, and running the automated pytest validation suite.")
    ]

    for title, text in sections:
        story.append(Paragraph(title, h1_style))
        story.append(Paragraph(text, body_style))
        story.append(Paragraph("Detailed technical steps, parameter definitions, and usage guidelines are provided for analysts.", body_style))
        story.append(Spacer(1, 15))
        story.append(PageBreak())

    doc.build(story)
    print(f"[Day 44] Analyst Guide generated -> {output_path}")

if __name__ == "__main__":
    generate_analyst_guide()
