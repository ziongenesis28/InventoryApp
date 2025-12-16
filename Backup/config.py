# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLIENT_CONFIG = {
    'business_name': "My Bakery Shop",
    'currency': "₱",
    'excel_file': os.path.join(BASE_DIR, "data", "inventory.xlsx"),
    'date_format': "%Y-%m-%d",
    'low_stock_warning': 20
}

