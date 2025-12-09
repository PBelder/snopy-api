from flask import Flask, jsonify
import pandas as pd
import requests
import pandas as pd
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

def parse_market_cap(cap_str):
    if not isinstance(cap_str, str):
        return 0
    
    cap_str = cap_str.strip()
    multiplier = 1
    if cap_str.endswith('T'):
        multiplier = 1_000_000_000_000
        cap_str = cap_str[:-1]
    elif cap_str.endswith('B'):
        multiplier = 1_000_000_000
        cap_str = cap_str[:-1]
    elif cap_str.endswith('M'):
        multiplier = 1_000_000
        cap_str = cap_str[:-1]
    
    try:
        return float(cap_str) * multiplier
    except:
        return 0

def get_sp500_companies():
    url = "https://stockanalysis.com/list/sp-500-stocks/"
    try:
        # Add User-Agent to avoid 403
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        
        df = None
        for table in tables:
            if 'Market Cap' in table.columns:
                df = table
                break
        
        if df is None:
            return None, "Could not find S&P 500 table in StockAnalysis page"

        # Rename columns to match desired output
        # StockAnalysis columns: No., Symbol, Company Name, Market Cap, Stock Price, % Change, Revenue
        df = df.rename(columns={'Company Name': 'companyName', 'Symbol': 'symbol', 'Stock Price': 'stockPrice'})
        
        # Convert to list of dictionaries
        companies = df.to_dict(orient='records')
        
        # Parse market cap and clean up
        for company in companies:
            # Keep only relevant fields
            keys_to_keep = ['symbol', 'companyName', 'Market Cap', 'stockPrice']
            for k in list(company.keys()):
                if k not in keys_to_keep:
                    del company[k]
            
            # Parse market cap string to number
            raw_cap = company.get('Market Cap', '0')
            company['marketCap'] = parse_market_cap(raw_cap)
            # Remove old key
            if 'Market Cap' in company:
                del company['Market Cap']
            
            # Clean stock price
            try:
                price = company.get('stockPrice', 0)
                # Handle if it's a string
                if isinstance(price, str):
                    price = float(price.replace(',', '').strip())
                company['stockPrice'] = round(float(price), 2)
            except:
                company['stockPrice'] = 0.0

            # Add logo URL
            # Handle special cases for FMP if needed, but usually standard tickers work
            # For dual listings like BRK.B, FMP often uses BRK-B
            ticker_for_image = company['symbol'].replace('.', '-')
            company['logoUrl'] = f"https://financialmodelingprep.com/image-stock/{ticker_for_image}.png"
            
        # Sort by marketCap descending
        companies.sort(key=lambda x: x.get('marketCap', 0), reverse=True)

        return companies, None
    except Exception as e:
        print(f"Error fetching S&P 500 data: {e}")
        return None, str(e)

@app.route('/')
def hello():
    return "Welcome to the S&P 500 API! Access /sp500 to get the list of companies."

@app.route('/sp500')
def sp500():
    companies, error = get_sp500_companies()
    if companies:
        # Get current time in Israel
        israel_tz = pytz.timezone('Asia/Jerusalem')
        israel_time = datetime.now(israel_tz)
        
        response = {
            "generatedAt": israel_time.strftime("%B %d, %Y %H:%M:%S"),
            "companies": companies
        }
        return jsonify(response)
    else:
        return jsonify({"error": f"Failed to fetch data: {error}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
