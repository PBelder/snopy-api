import pandas as pd
import requests

def test_slickcharts():
    url = "https://www.slickcharts.com/sp500"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers)
        tables = pd.read_html(r.text)
        print(f"Slickcharts tables found: {len(tables)}")
        if tables:
            print("Slickcharts columns:", tables[0].columns)
            print(tables[0].head())
    except Exception as e:
        print(f"Slickcharts error: {e}")

def test_stockanalysis():
    url = "https://stockanalysis.com/list/sp-500-stocks/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers)
        tables = pd.read_html(r.text)
        print(f"StockAnalysis tables found: {len(tables)}")
        if tables:
            print("StockAnalysis columns:", tables[0].columns)
            print(tables[0].head())
    except Exception as e:
        print(f"StockAnalysis error: {e}")

print("--- Testing Slickcharts ---")
test_slickcharts()
print("\n--- Testing StockAnalysis ---")
test_stockanalysis()
