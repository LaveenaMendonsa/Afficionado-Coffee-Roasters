# Afficionado Coffee Roasters — Sales Analysis

## Project Overview
An interactive data analytics project exploring coffee sales, hourly demand, time-of-day performance, and store-level performance.

## Tools Used
- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Streamlit
- Jupyter Notebook

## Key Features
- Overall sales summary
- Hourly demand analysis
- Time-of-day performance
- Store-level comparison
- Interactive filters for store, hour range, and metric
- Automatic loading of the cleaned dataset

## Dataset
The project analyzes 149,116 transactions. The dataset contains transaction times but does not provide the actual transaction date, so reliable weekday and weekend analysis is not possible.

## Project Files
- `app.py` — Streamlit dashboard
- `requirements.txt` — Python dependencies
- `cleaned_coffee_sales.csv` — cleaned dataset used by the dashboard
- `coffee_sales_analysis.ipynb` — analysis notebook
- `Afficionado_Coffee_Sales_Research_Paper.pdf` — research paper
- `Afficionado Coffee Roasters.xlsx - Transactions.csv` — original dataset

## How to Run
Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```
