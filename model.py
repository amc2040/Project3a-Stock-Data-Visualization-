
"""
Stock Data Visualizer - Model Layer
Handles data fetching, validation, and processing
"""

# Import necessary modules
import requests                      # For making HTTP requests to the API
from datetime import datetime        # For handling and validating dates
from config import API_KEY           # Import API key from config.py



# Class: AlphaVantageAPI

class AlphaVantageAPI:
    """Handles API communication with Alpha Vantage"""
    
    BASE_URL = "https://www.alphavantage.co/query"  # Base URL for the Alpha Vantage API
    
    def __init__(self):
        """Initialize the API client with API key"""
        self.api_key = API_KEY  # Store API key for authentication
    
    def fetch_stock_data(self, symbol, time_series):
        """
        Fetch stock data from Alpha Vantage API
        
        Args:
            symbol (str): Stock symbol (e.g., 'GOOGL')
            time_series (int): Time series function 
                               (1=Intraday, 2=Daily, 3=Weekly, 4=Monthly)
        
        Returns:
            dict: JSON response from API or None if an error occurs
        """
        # Map user’s choice (1–4) to the correct API function name
        function_map = {
            1: "TIME_SERIES_INTRADAY",
            2: "TIME_SERIES_DAILY",
            3: "TIME_SERIES_WEEKLY",
            4: "TIME_SERIES_MONTHLY"
        }
        
        # Set up API request parameters
        params = {
            'function': function_map[time_series],
            'symbol': symbol,
            'apikey': self.api_key,
            'outputsize': 'full'  # Get full historical data (up to 20 years)
        }
        
        # If user selects Intraday, add an interval
        if time_series == 1:
            params['interval'] = '60min'
        
        try:
            # Send GET request to API
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()  # Raises error for 4xx/5xx responses
            
            data = response.json()
            
            # Check if API returned an error message
            if "Error Message" in data:
                print(f"API Error: {data['Error Message']}")
                return None
            
            # Check if API returned a note (e.g., rate limit reached)
            if "Note" in data:
                print(f"API Note: {data['Note']}")
                return None
            
            # Return valid JSON data
            return data
            
        except requests.exceptions.RequestException as e:
            # Handle network or connection errors
            print(f"Network error: {e}")
            return None

# Class: StockData

class StockData:
    """Manages and processes stock data"""
    
    def __init__(self, symbol, raw_data, time_series):
        """
        Initialize stock data
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            raw_data (dict): Raw JSON data from API
            time_series (int): Time series type (1-4)
        """
        self.symbol = symbol
        self.raw_data = raw_data
        self.time_series = time_series
        self.filtered_data = {}  # To store filtered results
    
    def filter_by_date_range(self, start_date, end_date):
        """
        Filter stock data by date range
        
        Args:
            start_date (datetime): Begin date
            end_date (datetime): End date
        
        Returns:
            dict: Filtered data with dates as keys
        """
        # Determine the correct key for time series data based on user's selection
        time_series_key_map = {
            1: "Time Series (60min)",
            2: "Time Series (Daily)",
            3: "Weekly Time Series",
            4: "Monthly Time Series"
        }
        
        time_series_key = time_series_key_map[self.time_series]
        
        # Check that key exists in the API response
        if time_series_key not in self.raw_data:
            print(f"Error: Could not find '{time_series_key}' in API response")
            return {}
        
        time_series_data = self.raw_data[time_series_key]
        
        # Filter the data between the start and end dates
        self.filtered_data = {}
        for date_str, values in time_series_data.items():
            # Extract only the date portion (ignore time for intraday)
            date_only = date_str.split()[0]
            date_obj = datetime.strptime(date_only, '%Y-%m-%d')
            
            # Keep only entries within the specified date range
            if start_date <= date_obj <= end_date:
                self.filtered_data[date_str] = values
        
        return self.filtered_data
    
    def get_formatted_data(self):
        """
        Format filtered data for charting
        
        Returns:
            dict: Formatted data containing lists of dates and OHLC values
        """
        # If there’s no filtered data, return None
        if not self.filtered_data:
            return None
        
        dates = []
        open_prices = []
        high_prices = []
        low_prices = []
        close_prices = []
        
        # Sort entries by date to keep data in chronological order
        sorted_dates = sorted(self.filtered_data.keys())
        
        for date in sorted_dates:
            values = self.filtered_data[date]
            dates.append(date.split()[0])  # Use only the date part (ignore time)
            open_prices.append(float(values['1. open']))
            high_prices.append(float(values['2. high']))
            low_prices.append(float(values['3. low']))
            close_prices.append(float(values['4. close']))
        
        # Return a dictionary formatted for chart rendering
        return {
            'dates': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices
        }

# Validation Functions
def validate_date_format(date_string):
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_string (str): Date string to validate
    
    Returns:
        datetime object if valid, None otherwise
    """
    try:
        # Try to parse the date; if it fails, ValueError is raised
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        # Return None if the format is invalid
        return None


def validate_date_range(start_date, end_date):
    """
    Validate that end date is after start date
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Ensure the end date isn’t before the start date
    return end_date >= start_date