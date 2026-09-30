.PHONY: load ratios test report dashboard api clean

load:
	python3 -m src.data.load_db

ratios:
	python3 -m src.analytics.ratios

test:
	python3 -m pytest --html=reports/pytest_report.html --self-contained-html

report:
	python3 -m src.reports.generate_all

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage reports/pytest_report.html
