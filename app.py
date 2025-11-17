from flask import Flask, render_template, request, flash
from model import AlphaVantageAPI, StockData, validate_date_format, validate_date_range
from view import ChartGenerator
import csv
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

def load_symbols():
    """Load stock symbols from CSV file"""
    symbols = []
    csv_path = os.path.join(os.path.dirname(__file__), "stocks.csv")
    
    try:
        with open(csv_path, newline="", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get("Symbol")
                if symbol:
                    symbols.append(symbol.strip().upper())
        return sorted(set(symbols))
    except FileNotFoundError:
        print("Error: stocks.csv file not found!")
        return ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]  
    except Exception as e:
        print(f"Error loading symbols: {e}")
        return ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]  


@app.route("/", methods=["GET", "POST"])
def index():
    """Main route - displays form and handles chart generation"""
    symbols = load_symbols()
    chart_html = None
    selected_symbol = None

    if request.method == "POST":
        # Collect form input
        selected_symbol = request.form.get("symbol", "").strip().upper()
        chart_type = int(request.form.get("chart_type", "2"))
        time_series = int(request.form.get("time_series", "2"))
        start_date_str = request.form.get("start_date", "").strip()
        end_date_str = request.form.get("end_date", "").strip()

        # Validate inputs
        if not selected_symbol:
            flash("Please select a stock symbol.", "error")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        if not start_date_str or not end_date_str:
            flash("Please provide both start and end dates.", "error")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        # Validate date formats
        start_date = validate_date_format(start_date_str)
        end_date = validate_date_format(end_date_str)
        
        if not start_date or not end_date:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        if not validate_date_range(start_date, end_date):
            flash("End date must be on or after the start date.", "error")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        # Fetch data from API
        print(f"Fetching data for {selected_symbol}...")
        api = AlphaVantageAPI()
        raw_data = api.fetch_stock_data(selected_symbol, time_series)
        
        if not raw_data:
            flash("Failed to fetch stock data. Please check the symbol and try again.", "error")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        # Process and filter data
        stock_data = StockData(selected_symbol, raw_data, time_series)
        stock_data.filter_by_date_range(start_date, end_date)
        formatted_data = stock_data.get_formatted_data()
        
        if not formatted_data or not formatted_data.get('dates'):
            flash(f"No data found for {selected_symbol} in the date range {start_date_str} to {end_date_str}.", "warning")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        # Generate chart HTML
        print(f"Generating chart with {len(formatted_data['dates'])} data points...")
        chart_html = ChartGenerator.create_chart(
            formatted_data, 
            selected_symbol, 
            chart_type, 
            start_date_str, 
            end_date_str
        )

        if not chart_html:
            flash("Failed to generate chart.", "error")
            return render_template("index.html", symbols=symbols, chart_html=None, selected_symbol=selected_symbol)

        flash(f"Successfully generated chart for {selected_symbol} with {len(formatted_data['dates'])} data points.", "success")

    return render_template("index.html", symbols=symbols, chart_html=chart_html, selected_symbol=selected_symbol)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)