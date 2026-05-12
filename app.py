import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from io import BytesIO
import json
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import secrets
import csv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'pos_secret_key_2024')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
CORS(app, supports_credentials=True)

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_SENDER = os.getenv('SMTP_SENDER', SMTP_USERNAME)
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

# In-memory data store (fallback if MongoDB not available)
USE_MEMORY_DB = False
memory_db = None
client = None
db = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client['pos_supermarket']
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    print("Using in-memory fallback database")
    USE_MEMORY_DB = True

    class MemoryDB:
        def __init__(self):
            self.products = []
            self.categories = []
            self.product_groups = []
            self.product_comments = []
            self.sales = []
            self.users = []
            self.vendors = []
            self.purchase_orders = []
            self.product_prices = []
            self.write_offs = []
            self._init_data()

        def _init_data(self):
            categories = ["Fruits", "Dairy", "Bakery", "Grains", "Meat", "Beverages", "Vegetables", "Snacks", "Clothing", "Shoes", "Grocery"]
            self.categories = [{"_id": str(i+1), "name": cat} for i, cat in enumerate(categories)]

            # Product Groups
            groups = [
                {"name": "Electronics", "description": "Electronic devices and accessories"},
                {"name": "Clothing", "description": "Apparel and fashion items"},
                {"name": "Food & Beverages", "description": "Edible items and drinks"},
                {"name": "Home & Kitchen", "description": "Household and kitchen products"},
                {"name": "Personal Care", "description": "Health and beauty products"},
            ]
            for i, g in enumerate(groups):
                g['_id'] = str(i + 1)
            self.product_groups = groups

            sample_products = [
                {"name": "Apple", "price": 2.50, "category": "Fruits", "barcode": "100001", "stock": 100, "unit": "kg", "supplier": "Fresh Farms", "cost_price": 1.50, "mrp": 3.00, "reorder_level": 20, "tax_rate": 5, "hsn_code": "0808", "expiry_date": "2026-08-15", "batch_no": "BT001", "manufacturer": "Fresh Farms Co"},
                {"name": "Banana", "price": 1.80, "category": "Fruits", "barcode": "100002", "stock": 150, "unit": "kg", "supplier": "Fresh Farms", "cost_price": 0.90, "mrp": 2.50, "reorder_level": 30, "tax_rate": 5, "hsn_code": "0808", "expiry_date": "2026-07-20", "batch_no": "BT002", "manufacturer": "Fresh Farms Co"},
                {"name": "Orange", "price": 3.20, "category": "Fruits", "barcode": "100003", "stock": 80, "unit": "kg", "supplier": "Citrus Valley", "cost_price": 2.00, "mrp": 4.00, "reorder_level": 20, "tax_rate": 5, "hsn_code": "0808", "expiry_date": "2026-09-10", "batch_no": "BT003", "manufacturer": "Citrus Valley Ltd"},
                {"name": "Milk", "price": 4.50, "category": "Dairy", "barcode": "200001", "stock": 50, "unit": "liter", "supplier": "DairyBest", "cost_price": 3.00, "mrp": 5.50, "reorder_level": 15, "tax_rate": 12, "hsn_code": "0401", "expiry_date": "2026-06-25", "batch_no": "BT004", "manufacturer": "DairyBest Inc"},
                {"name": "Cheese", "price": 8.99, "category": "Dairy", "barcode": "200002", "stock": 30, "unit": "piece", "supplier": "DairyBest", "cost_price": 5.50, "mrp": 10.00, "reorder_level": 10, "tax_rate": 12, "hsn_code": "0406", "expiry_date": "2026-10-01", "batch_no": "BT005", "manufacturer": "DairyBest Inc"},
                {"name": "Yogurt", "price": 2.20, "category": "Dairy", "barcode": "200003", "stock": 40, "unit": "cup", "supplier": "DairyBest", "cost_price": 1.20, "mrp": 3.00, "reorder_level": 15, "tax_rate": 12, "hsn_code": "0401", "expiry_date": "2026-07-30", "batch_no": "BT006", "manufacturer": "DairyBest Inc"},
                {"name": "Bread", "price": 3.50, "category": "Bakery", "barcode": "300001", "stock": 60, "unit": "loaf", "supplier": "Golden Bakery", "cost_price": 2.00, "mrp": 4.50, "reorder_level": 15, "tax_rate": 5, "hsn_code": "1905", "expiry_date": "2026-06-20", "batch_no": "BT007", "manufacturer": "Golden Bakery"},
                {"name": "Croissant", "price": 1.99, "category": "Bakery", "barcode": "300002", "stock": 45, "unit": "piece", "supplier": "Golden Bakery", "cost_price": 1.00, "mrp": 2.50, "reorder_level": 10, "tax_rate": 5, "hsn_code": "1905", "expiry_date": "2026-07-15", "batch_no": "BT008", "manufacturer": "Golden Bakery"},
                {"name": "Cookies", "price": 4.25, "category": "Bakery", "barcode": "300003", "stock": 55, "unit": "pack", "supplier": "Sweet Treats", "cost_price": 2.50, "mrp": 5.50, "reorder_level": 15, "tax_rate": 12, "hsn_code": "1905", "expiry_date": "2026-12-01", "batch_no": "BT009", "manufacturer": "Sweet Treats Co"},
                {"name": "Rice", "price": 12.99, "category": "Grains", "barcode": "400001", "stock": 70, "unit": "kg", "supplier": "Grain House", "cost_price": 8.00, "mrp": 15.00, "reorder_level": 20, "tax_rate": 5, "hsn_code": "1006", "expiry_date": "2027-01-15", "batch_no": "BT010", "manufacturer": "Grain House Ltd"},
                {"name": "Pasta", "price": 2.99, "category": "Grains", "barcode": "400002", "stock": 85, "unit": "pack", "supplier": "Grain House", "cost_price": 1.50, "mrp": 4.00, "reorder_level": 20, "tax_rate": 12, "hsn_code": "1902", "expiry_date": "2026-11-30", "batch_no": "BT011", "manufacturer": "Grain House Ltd"},
                {"name": "T-Shirt", "price": 15.99, "category": "Clothing", "barcode": "500001", "stock": 60, "unit": "piece", "supplier": "StyleWear", "cost_price": 8.00, "mrp": 20.00, "reorder_level": 15, "tax_rate": 5, "hsn_code": "6109", "expiry_date": "2027-06-01", "batch_no": "BT012", "manufacturer": "StyleWear Inc"},
                {"name": "Jeans", "price": 29.99, "category": "Clothing", "barcode": "500002", "stock": 40, "unit": "piece", "supplier": "StyleWear", "cost_price": 15.00, "mrp": 35.00, "reorder_level": 10, "tax_rate": 5, "hsn_code": "6204", "expiry_date": "2027-06-01", "batch_no": "BT013", "manufacturer": "StyleWear Inc"},
                {"name": "Running Shoes", "price": 45.99, "category": "Shoes", "barcode": "600001", "stock": 30, "unit": "pair", "supplier": "FootFit", "cost_price": 25.00, "mrp": 55.00, "reorder_level": 8, "tax_rate": 5, "hsn_code": "6403", "expiry_date": "2027-12-31", "batch_no": "BT014", "manufacturer": "FootFit Ltd"},
                {"name": "Sneakers", "price": 35.99, "category": "Shoes", "barcode": "600002", "stock": 25, "unit": "pair", "supplier": "FootFit", "cost_price": 20.00, "mrp": 42.00, "reorder_level": 8, "tax_rate": 5, "hsn_code": "6404", "expiry_date": "2027-12-31", "batch_no": "BT015", "manufacturer": "FootFit Ltd"},
                {"name": "Chicken", "price": 9.99, "category": "Meat", "barcode": "700001", "stock": 25, "unit": "kg", "supplier": "Farm Fresh", "cost_price": 6.00, "mrp": 12.00, "reorder_level": 8, "tax_rate": 5, "hsn_code": "0207", "expiry_date": "2026-06-15", "batch_no": "BT016", "manufacturer": "Farm Fresh Co"},
                {"name": "Beef", "price": 15.99, "category": "Meat", "barcode": "700002", "stock": 20, "unit": "kg", "supplier": "Farm Fresh", "cost_price": 10.00, "mrp": 18.00, "reorder_level": 8, "tax_rate": 5, "hsn_code": "0201", "expiry_date": "2026-06-10", "batch_no": "BT017", "manufacturer": "Farm Fresh Co"},
                {"name": "Fish", "price": 12.50, "category": "Meat", "barcode": "700003", "stock": 15, "unit": "kg", "supplier": "Sea Foods Ltd", "cost_price": 8.00, "mrp": 15.00, "reorder_level": 5, "tax_rate": 5, "hsn_code": "0306", "expiry_date": "2026-06-08", "batch_no": "BT018", "manufacturer": "Sea Foods Ltd"},
                {"name": "Coke", "price": 1.99, "category": "Beverages", "barcode": "800001", "stock": 200, "unit": "bottle", "supplier": "Beverage World", "cost_price": 0.80, "mrp": 2.50, "reorder_level": 50, "tax_rate": 12, "hsn_code": "2201", "expiry_date": "2026-10-15", "batch_no": "BT019", "manufacturer": "Beverage World"},
                {"name": "Juice", "price": 3.49, "category": "Beverages", "barcode": "800002", "stock": 120, "unit": "bottle", "supplier": "Beverage World", "cost_price": 1.50, "mrp": 4.00, "reorder_level": 30, "tax_rate": 12, "hsn_code": "2202", "expiry_date": "2026-09-30", "batch_no": "BT020", "manufacturer": "Beverage World"},
                {"name": "Water", "price": 0.99, "category": "Beverages", "barcode": "800003", "stock": 300, "unit": "bottle", "supplier": "Beverage World", "cost_price": 0.40, "mrp": 1.50, "reorder_level": 50, "tax_rate": 5, "hsn_code": "2201", "expiry_date": "2026-11-20", "batch_no": "BT021", "manufacturer": "Beverage World"},
                {"name": "Carrot", "price": 1.50, "category": "Vegetables", "barcode": "900001", "stock": 80, "unit": "kg", "supplier": "Green Valley", "cost_price": 0.70, "mrp": 2.00, "reorder_level": 20, "tax_rate": 5, "hsn_code": "0706", "expiry_date": "2026-06-20", "batch_no": "BT022", "manufacturer": "Green Valley Farms"},
                {"name": "Potato", "price": 1.20, "category": "Vegetables", "barcode": "900002", "stock": 100, "unit": "kg", "supplier": "Green Valley", "cost_price": 0.50, "mrp": 1.80, "reorder_level": 30, "tax_rate": 5, "hsn_code": "0701", "expiry_date": "2026-07-25", "batch_no": "BT023", "manufacturer": "Green Valley Farms"},
                {"name": "Snack Mix", "price": 3.99, "category": "Snacks", "barcode": "100001", "stock": 90, "unit": "pack", "supplier": "Crunchy Foods", "cost_price": 2.00, "mrp": 5.00, "reorder_level": 20, "tax_rate": 12, "hsn_code": "1904", "expiry_date": "2026-11-15", "batch_no": "BT024", "manufacturer": "Crunchy Foods Ltd"},
                {"name": "Ice Cream", "price": 2.50, "category": "Grocery", "barcode": "110001", "stock": 40, "unit": "liter", "supplier": "Cool Creams", "cost_price": 1.20, "mrp": 3.50, "reorder_level": 10, "tax_rate": 12, "hsn_code": "2105", "expiry_date": "2026-07-10", "batch_no": "BT025", "manufacturer": "Cool Creams Co"},
            ]
            for i, p in enumerate(sample_products):
                p['_id'] = str(i + 1)
            self.products = sample_products

            admin_pass_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            self.users = [
                {
                    "_id": "1", "username": "admin", "password": admin_pass_hash.decode('utf-8'),
                    "role": "admin", "full_name": "System Admin", "email": "admin@pos.com",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]

            self.vendors = [
                {"_id": "1", "name": "Fresh Farms", "contact": "John Doe", "phone": "+1234567890",
                 "email": "fresh@farms.com", "address": "123 Farm Road", "status": "active",
                 "payment_terms": "Net 30", "created_at": datetime.utcnow().isoformat()},
                {"_id": "2", "name": "DairyBest", "contact": "Jane Smith", "phone": "+1234567891",
                 "email": "contact@dairybest.com", "address": "456 Dairy Lane", "status": "active",
                 "payment_terms": "Net 15", "created_at": datetime.utcnow().isoformat()},
                {"_id": "3", "name": "StyleWear", "contact": "Mike Brown", "phone": "+1234567892",
                 "email": "info@stylewear.com", "address": "789 Fashion Ave", "status": "active",
                 "payment_terms": "Net 45", "created_at": datetime.utcnow().isoformat()},
            ]

            # Colors
            colors = [
                {"_id": "1", "value": "red", "label": "Red"},
                {"_id": "2", "value": "blue", "label": "Blue"},
                {"_id": "3", "value": "green", "label": "Green"},
                {"_id": "4", "value": "yellow", "label": "Yellow"},
                {"_id": "5", "value": "orange", "label": "Orange"},
                {"_id": "6", "value": "purple", "label": "Purple"},
                {"_id": "7", "value": "pink", "label": "Pink"},
                {"_id": "8", "value": "black", "label": "Black"},
                {"_id": "9", "value": "white", "label": "White"},
                {"_id": "10", "value": "gray", "label": "Gray"},
                {"_id": "11", "value": "brown", "label": "Brown"},
                {"_id": "12", "value": "navy", "label": "Navy"},
                {"_id": "13", "value": "teal", "label": "Teal"},
                {"_id": "14", "value": "maroon", "label": "Maroon"},
                {"_id": "15", "value": "olive", "label": "Olive"},
                {"_id": "16", "value": "silver", "label": "Silver"},
                {"_id": "17", "value": "gold", "label": "Gold"},
                {"_id": "18", "value": "multi", "label": "Multi-Color"},
            ]
            self.colors = colors

            # Units of Measure
            units = [
                {"_id": "1", "name": "piece"},
                {"_id": "2", "name": "kg"},
                {"_id": "3", "name": "liter"},
                {"_id": "4", "name": "meter"},
                {"_id": "5", "name": "pack"},
                {"_id": "6", "name": "box"},
                {"_id": "7", "name": "pair"},
                {"_id": "8", "name": "set"},
            ]
            self.units = units

        def count_documents(self, collection_name, query=None):
            collection = getattr(self, collection_name, [])
            if query:
                if collection_name == 'users':
                    return len([u for u in collection if all(u.get(k) == v for k, v in query.items() if k != 'password')])
                return len([p for p in collection if all(p.get(k) == v for k, v in query.items())])
            return len(collection)

        def find(self, collection_name, query=None):
            collection = getattr(self, collection_name, [])
            if collection_name == 'users':
                return [u for u in collection]
            if query and '_id' in query:
                pid = str(query['_id'])
                return [p for p in collection if str(p.get('_id')) == pid]
            elif query and 'category' in query:
                return [p for p in collection if p.get('category') == query['category']]
            elif query and 'vendor_name' in query:
                return [p for p in collection if query['vendor_name'].lower() in (p.get('supplier') or '').lower()]
            return collection[:]

        def find_one(self, collection_name, query):
            collection = getattr(self, collection_name, [])
            if collection_name == 'users':
                if 'username' in query:
                    for u in collection:
                        if u.get('username') == query['username']:
                            return u
                if '_id' in query:
                    uid = str(query['_id'])
                    for u in collection:
                        if str(u.get('_id')) == uid:
                            return u
                return None
            if '_id' in query:
                pid = str(query['_id'])
                for p in collection:
                    if str(p.get('_id')) == pid:
                        return p
            return None

        def insert_one(self, collection_name, doc):
            collection = getattr(self, collection_name, [])
            next_id = str(len(collection) + 1)
            doc['_id'] = next_id
            collection.append(doc)
            setattr(self, collection_name, collection)
            class Result:
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            return Result(next_id)

        def update_one(self, collection_name, query, update):
            collection = getattr(self, collection_name, [])
            pid = str(query['_id'])
            for i, item in enumerate(collection):
                if str(item.get('_id')) == pid:
                    for k, v in update.get('$set', {}).items():
                        collection[i][k] = v
                    class Result:
                        def __init__(self, modified):
                            self.modified_count = modified
                    return Result(1)
            class Result:
                def __init__(self, modified):
                    self.modified_count = modified
            return Result(0)

        def delete_one(self, collection_name, query):
            collection = getattr(self, collection_name, [])
            pid = str(query['_id'])
            for i, item in enumerate(collection):
                if str(item.get('_id')) == pid:
                    del collection[i]
                    setattr(self, collection_name, collection)
                    class Result:
                        def __init__(self, deleted):
                            self.deleted_count = deleted
                    return Result(1)
            class Result:
                def __init__(self, deleted):
                    self.deleted_count = deleted
            return Result(0)

        def find_many(self, collection_name, query=None):
            collection = getattr(self, collection_name, [])
            if not query:
                return collection[:]
            results = []
            for item in collection:
                match = True
                for k, v in query.items():
                    if str(item.get(k, '')) != str(v):
                        match = False
                        break
                if match:
                    results.append(item)
            return results

        def aggregate(self, pipeline):
            results = []
            for sale in self.sales:
                results.append(sale)
            return results

    memory_db = MemoryDB()
    db = memory_db
    print("Using in-memory database (data will not persist after restart)")

# Initialize database collections
def init_db():
    """Initialize database with sample data if empty"""
    if not USE_MEMORY_DB:
        if db.products.count_documents({}) == 0:
            sample_products = [
                {"name": "Apple", "price": 2.50, "category": "Fruits", "barcode": "100001", "stock": 100, "unit": "kg",
                 "supplier": "Fresh Farms", "cost_price": 1.50, "mrp": 3.00, "reorder_level": 20, "tax_rate": 5,
                 "hsn_code": "0808", "expiry_date": "2026-08-15", "batch_no": "BT001", "manufacturer": "Fresh Farms Co",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "Banana", "price": 1.80, "category": "Fruits", "barcode": "100002", "stock": 150, "unit": "kg",
                 "supplier": "Fresh Farms", "cost_price": 0.90, "mrp": 2.50, "reorder_level": 30, "tax_rate": 5,
                 "hsn_code": "0808", "expiry_date": "2026-07-20", "batch_no": "BT002", "manufacturer": "Fresh Farms Co",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "Rice", "price": 12.99, "category": "Grains", "barcode": "400001", "stock": 70, "unit": "kg",
                 "supplier": "Grain House", "cost_price": 8.00, "mrp": 15.00, "reorder_level": 20, "tax_rate": 5,
                 "hsn_code": "1006", "expiry_date": "2027-01-15", "batch_no": "BT010", "manufacturer": "Grain House Ltd",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "T-Shirt", "price": 15.99, "category": "Clothing", "barcode": "500001", "stock": 60, "unit": "piece",
                 "supplier": "StyleWear", "cost_price": 8.00, "mrp": 20.00, "reorder_level": 15, "tax_rate": 5,
                 "hsn_code": "6109", "expiry_date": "2027-06-01", "batch_no": "BT012", "manufacturer": "StyleWear Inc",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "Running Shoes", "price": 45.99, "category": "Shoes", "barcode": "600001", "stock": 30, "unit": "pair",
                 "supplier": "FootFit", "cost_price": 25.00, "mrp": 55.00, "reorder_level": 8, "tax_rate": 5,
                 "hsn_code": "6403", "expiry_date": "2027-12-31", "batch_no": "BT014", "manufacturer": "FootFit Ltd",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "Chicken", "price": 9.99, "category": "Meat", "barcode": "700001", "stock": 25, "unit": "kg",
                 "supplier": "Farm Fresh", "cost_price": 6.00, "mrp": 12.00, "reorder_level": 8, "tax_rate": 5,
                 "hsn_code": "0207", "expiry_date": "2026-06-15", "batch_no": "BT016", "manufacturer": "Farm Fresh Co",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "Coke", "price": 1.99, "category": "Beverages", "barcode": "800001", "stock": 200, "unit": "bottle",
                 "supplier": "Beverage World", "cost_price": 0.80, "mrp": 2.50, "reorder_level": 50, "tax_rate": 12,
                 "hsn_code": "2201", "expiry_date": "2026-10-15", "batch_no": "BT019", "manufacturer": "Beverage World",
                 "created_at": datetime.utcnow().isoformat()},
            ]
            db.products.insert_many(sample_products)
            print("Sample products initialized")

        if db.categories.count_documents({}) == 0:
            categories = ["Fruits", "Dairy", "Bakery", "Grains", "Meat", "Beverages", "Vegetables", "Snacks", "Clothing", "Shoes", "Grocery"]
            db.categories.insert_many([{"name": cat} for cat in categories])
            print("Categories initialized")

        if db.vendors.count_documents({}) == 0:
            vendors = [
                {"name": "Fresh Farms", "contact": "John Doe", "phone": "+1234567890", "email": "fresh@farms.com",
                 "address": "123 Farm Road", "status": "active", "payment_terms": "Net 30",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "DairyBest", "contact": "Jane Smith", "phone": "+1234567891", "email": "contact@dairybest.com",
                 "address": "456 Dairy Lane", "status": "active", "payment_terms": "Net 15",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "StyleWear", "contact": "Mike Brown", "phone": "+1234567892", "email": "info@stylewear.com",
                 "address": "789 Fashion Ave", "status": "active", "payment_terms": "Net 45",
                 "created_at": datetime.utcnow().isoformat()},
            ]
            db.vendors.insert_many(vendors)
            print("Vendors initialized")

        if db.vendors.count_documents({}) == 0:
            vendors = [
                {"name": "Fresh Farms", "contact": "John Doe", "phone": "+1234567890", "email": "fresh@farms.com",
                 "address": "123 Farm Road", "status": "active", "payment_terms": "Net 30",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "DairyBest", "contact": "Jane Smith", "phone": "+1234567891", "email": "contact@dairybest.com",
                 "address": "456 Dairy Lane", "status": "active", "payment_terms": "Net 15",
                 "created_at": datetime.utcnow().isoformat()},
                {"name": "StyleWear", "contact": "Mike Brown", "phone": "+1234567892", "email": "info@stylewear.com",
                 "address": "789 Fashion Ave", "status": "active", "payment_terms": "Net 45",
                 "created_at": datetime.utcnow().isoformat()},
            ]
            db.vendors.insert_many(vendors)
            print("Vendors initialized")

        # Initialize product groups
        if USE_MEMORY_DB:
            if len(db.product_groups) == 0:
                groups = [
                    {"name": "Electronics", "description": "Electronic devices and accessories"},
                    {"name": "Clothing", "description": "Apparel and fashion items"},
                    {"name": "Food & Beverages", "description": "Edible items and drinks"},
                    {"name": "Home & Kitchen", "description": "Household and kitchen products"},
                    {"name": "Personal Care", "description": "Health and beauty products"},
                ]
                for i, g in enumerate(groups):
                    g['_id'] = str(i + 1)
                db.product_groups.extend(groups)
                print("Product groups initialized")
        else:
            if db.product_groups.count_documents({}) == 0:
                groups = [
                    {"name": "Electronics", "description": "Electronic devices and accessories"},
                    {"name": "Clothing", "description": "Apparel and fashion items"},
                    {"name": "Food & Beverages", "description": "Edible items and drinks"},
                    {"name": "Home & Kitchen", "description": "Household and kitchen products"},
                    {"name": "Personal Care", "description": "Health and beauty products"},
                ]
                db.product_groups.insert_many(groups)
                print("Product groups initialized")

    # Initialize admin user
    if USE_MEMORY_DB:
        if len(db.users) == 0:
            admin_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            db.insert_one('users', {
                "username": "admin", "password": admin_hash.decode('utf-8'),
                "role": "admin", "full_name": "System Admin", "email": "admin@pos.com",
                "created_at": datetime.utcnow().isoformat()
            })
            print("Default admin user created (admin/admin123)")
    else:
        if db.users.count_documents({}) == 0:
            admin_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({
                "username": "admin", "password": admin_hash.decode('utf-8'),
                "role": "admin", "full_name": "System Admin", "email": "admin@pos.com",
                "created_at": datetime.utcnow().isoformat()
            })
            print("Default admin user created (admin/admin123)")

def serialize_doc(doc):
    if USE_MEMORY_DB:
        return doc
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


def generate_reset_token():
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)


def send_password_reset_email(user_email, token, username, flask_request):
    """Send password reset email via SMTP"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD]):
        print(f"[DEMO MODE] Password reset token for {user_email}: {token}")
        print(f"Reset URL: {flask_request.scheme}://{flask_request.host}/reset-password?token={token}")
        return False

    try:
        reset_url = f"{flask_request.scheme}://{flask_request.host}/reset-password?token={token}"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'POS System - Password Reset Request'
        msg['From'] = SMTP_SENDER
        msg['To'] = user_email

        html = f"""
        <html>
        <body style="font-family: Segoe UI, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f5f6fa;">
            <div style="background: white; padding: 32px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 24px;">
                    <h2 style="color: #2c3e50; margin-bottom: 8px;">Password Reset</h2>
                    <p style="color: #7f8c8d;">Hello {username},</p>
                </div>
                <p style="color: #555; line-height: 1.6;">
                    We received a request to reset your password for your POS System account.
                    Click the button below to choose a new password:
                </p>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{reset_url}"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="font-size: 12px; color: #999; line-height: 1.6;">
                    If you didn't request a password reset, you can ignore this email.<br>
                    This link will expire in 24 hours for security reasons.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
                <p style="font-size: 11px; color: #bbb; text-align: center;">
                    POS System - Departmental Store Management
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER, user_email, msg.as_string())

        print(f"Password reset email sent to {user_email}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def get_next_id(collection_name):
    if USE_MEMORY_DB:
        collection = getattr(db, collection_name, [])
        if not collection:
            return "1"
        ids = [int(str(item.get('_id', '0'))) for item in collection]
        return str(max(ids) + 1)
    else:
        collection = getattr(db, collection_name)
        last = collection.find_one(sort=[('_id', -1)])
        if last:
            try:
                return str(int(str(last['_id'])) + 1)
            except:
                pass
        return "1"


# =============================================================================
# AUTH ROUTES
# =============================================================================

@app.before_request
def require_auth():
    """Protect dashboard and API routes that require authentication"""
    protected_paths = [
        '/dashboard', '/admin-dashboard', '/procurement-dashboard', '/sales-dashboard',
        '/api/users', '/api/products', '/api/categories', '/api/vendors',
        '/api/purchase-orders', '/api/prices', '/api/write-offs',
        '/api/reports', '/pos', '/reports',
        '/api/product-groups', '/api/comments', '/api/generate-barcode', '/api/colors',
        '/products'
    ]

    for path in protected_paths:
        if request.path.startswith(path):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect_to_dashboard(session.get('role'))
    return render_template('login.html')


@app.route('/api/auth/login', methods=['POST'])
def login_api():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    if USE_MEMORY_DB:
        user = db.find_one('users', {'username': username})
    else:
        user = db.users.find_one({'username': username})

    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    stored_hash = user.get('password', '')
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user.get('full_name', user['username'])
        return jsonify({
            'success': True,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'role': user['role'],
                'full_name': user.get('full_name', user['username'])
            }
        })
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({'success': True})
    return jsonify({'success': True})


@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')


@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'success': False, 'message': 'Email address is required'}), 400

    # Find user by email
    if USE_MEMORY_DB:
        user = None
        for u in db.users:
            if u.get('email', '').lower() == email:
                user = u
                break
    else:
        user = db.users.find_one({'email': {'$regex': f'^{email}$', '$options': 'i'}})

    # Always return success to prevent email enumeration
    if not user:
        return jsonify({'success': True, 'message': 'If the email exists in our system, a password reset link has been sent.'})

    # Generate reset token
    reset_token = generate_reset_token()
    reset_expiry = datetime.utcnow() + timedelta(hours=24)

    # Save token to user record
    if USE_MEMORY_DB:
        user['reset_token'] = reset_token
        user['reset_token_expiry'] = reset_expiry.isoformat()
    else:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {
                'reset_token': reset_token,
                'reset_token_expiry': reset_expiry
            }}
        )

    # Send email (will print token to console if SMTP not configured)
    username = user.get('username', 'User')
    email_sent = send_password_reset_email(email, reset_token, username, request)

    response = {
        'success': True,
        'message': 'If the email exists in our system, a password reset link has been sent.'
    }

    # In demo mode (no SMTP), include token for testing
    if not email_sent and not SMTP_SERVER:
        response['demo_token'] = reset_token
        response['demo_url'] = f"/reset-password?token={reset_token}"

    return jsonify(response)


@app.route('/reset-password')
def reset_password_page():
    token = request.args.get('token', '')
    return render_template('reset_password.html', token=token)


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token', '').strip()
    new_password = data.get('password', '')

    if not token or not new_password:
        return jsonify({'success': False, 'message': 'Token and new password are required'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Find user by token
    if USE_MEMORY_DB:
        user = None
        for u in db.users:
            if u.get('reset_token') == token:
                user = u
                break
    else:
        user = db.users.find_one({'reset_token': token})

    if not user:
        return jsonify({'success': False, 'message': 'Invalid or expired reset token'}), 400

    # Check token expiry
    expiry_str = user.get('reset_token_expiry')
    if expiry_str:
        if isinstance(expiry_str, str):
            expiry = datetime.fromisoformat(expiry_str)
        else:
            expiry = expiry_str
        if datetime.utcnow() > expiry:
            return jsonify({'success': False, 'message': 'Reset token has expired'}), 400

    # Update password
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    if USE_MEMORY_DB:
        user['password'] = new_hash.decode('utf-8')
        user['reset_token'] = None
        user['reset_token_expiry'] = None
    else:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'password': new_hash.decode('utf-8')},
             '$unset': {'reset_token': '', 'reset_token_expiry': ''}}
        )

    return jsonify({'success': True, 'message': 'Password has been reset successfully'})


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'sales_person')

    if not username or not password or not full_name:
        return jsonify({'success': False, 'message': 'Username, password and full name are required'}), 400

    if USE_MEMORY_DB:
        existing = db.find_one('users', {'username': username})
    else:
        existing = db.users.find_one({'username': username})

    if existing:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_doc = {
        'username': username, 'password': password_hash, 'role': role,
        'full_name': full_name, 'email': email,
        'created_at': datetime.utcnow().isoformat(),
        'created_by': session.get('user_id', 'system')
    }

    if USE_MEMORY_DB:
        result = db.insert_one('users', user_doc)
    else:
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = str(result.inserted_id)

    return jsonify({
        'success': True, 'message': 'User created successfully',
        'user': {'id': str(result.inserted_id), 'username': username, 'role': role, 'full_name': full_name}
    }), 201


@app.route('/api/users', methods=['GET'])
def get_users():
    if USE_MEMORY_DB:
        users = db.find('users')
    else:
        users = list(db.users.find())
    safe_users = []
    for u in users:
        safe_u = {}
        for k, v in u.items():
            if k == '_id':
                safe_u[k] = str(v)
            elif k != 'password':
                safe_u[k] = v
        safe_users.append(safe_u)
    return jsonify(safe_users)


@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if USE_MEMORY_DB:
        result = db.delete_one('users', {'_id': user_id})
    else:
        try:
            result = db.users.delete_one({'_id': ObjectId(user_id)})
        except Exception:
            return jsonify({'success': False, 'message': 'Invalid user ID'}), 400
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'User deleted'})
    return jsonify({'success': False, 'message': 'User not found'}), 404


# =============================================================================
# DASHBOARD ROUTES
# =============================================================================

def redirect_to_dashboard(role):
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'procurement_manager':
        return redirect(url_for('procurement_dashboard'))
    elif role == 'sales_person':
        return redirect(url_for('sales_dashboard'))
    else:
        return redirect(url_for('login_page'))


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect_to_dashboard(session.get('role'))
    return redirect(url_for('login_page'))


@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', user=session.get('full_name'), role=session.get('role'))


@app.route('/procurement-dashboard')
def procurement_dashboard():
    return render_template('procurement_dashboard.html', user=session.get('full_name'), role=session.get('role'))


@app.route('/sales-dashboard')
def sales_dashboard():
    return render_template('sales_dashboard.html', user=session.get('full_name'), role=session.get('role'))


@app.route('/pos')
def pos():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html', current_time=datetime.now().strftime('%a, %d %b %Y %H:%M'))


@app.route('/products')
def products_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    role = session.get('role')
    if role not in ['admin', 'procurement_manager']:
        return redirect_to_dashboard(role)
    return render_template('products.html', user=session.get('full_name'), role=session.get('role'))


# =============================================================================
# PRODUCTS API (Procurement Accessible)
# =============================================================================

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    search = request.args.get('search')
    query = {}
    if category:
        query['category'] = category
    if search:
        query['name'] = {'$regex': search, '$options': 'i'} if not USE_MEMORY_DB else {}

    if USE_MEMORY_DB:
        results = db.find('products', query) if query else db.find('products', {})
        if search and not query:
            results = [p for p in results if search.lower() in p['name'].lower()]
        return jsonify([serialize_doc(p) for p in results])

    products = list(db.products.find(query))
    return jsonify([serialize_doc(p) for p in products])


@app.route('/api/products/<id>', methods=['GET'])
def get_product(id):
    oid = id if USE_MEMORY_DB else ObjectId(id)
    if USE_MEMORY_DB and not any(c.isalnum() for c in id):
        oid = id
    product = db.products.find_one({'_id': oid}) if not USE_MEMORY_DB else db.find_one('products', {'_id': id})
    if product:
        return jsonify(serialize_doc(product))
    return jsonify({'error': 'Product not found'}), 404


@app.route('/api/products', methods=['POST'])
def add_product():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    required = ['name', 'price', 'category']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    product = {
        'name': data['name'],
        'code': data.get('code', ''),
        'barcode': data.get('barcode', ''),
        'qr_code': data.get('qr_code', secrets.token_hex(8)),
        'unit': data.get('unit', 'piece'),
        'category': data['category'],
        'group_id': data.get('group_id', ''),
        'group_name': data.get('group_name', ''),
        'supplier': data.get('supplier', ''),
        'cost_price': float(data.get('cost_price', 0)),
        'markup_percent': float(data.get('markup_percent', 0)),
        'price': float(data.get('price', 0)),
        'mrp': float(data.get('mrp', 0)),
        'price_includes_tax': data.get('price_includes_tax', False),
        'tax_rate': float(data.get('tax_rate', 0)),
        'price_change_allowed': data.get('price_change_allowed', True),
        'stock': int(data.get('stock', 0)),
        'default_quantity': int(data.get('default_quantity', 1)),
        'is_service': data.get('is_service', False),
        'low_stock_enabled': data.get('low_stock_enabled', False),
        'low_stock_quantity': int(data.get('low_stock_quantity', 0)),
        'reorder_level': int(data.get('reorder_level', 10)),
        'preferred_quantity': int(data.get('preferred_quantity', 0)),
        'age_restriction_years': int(data.get('age_restriction_years', 0)),
        'color': data.get('color', ''),
        'image_url': data.get('image_url', ''),
        'description': data.get('description', ''),
        'status': data.get('status', 'active'),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    if USE_MEMORY_DB:
        result = db.insert_one('products', product)
    else:
        result = db.products.insert_one(product)
    product['_id'] = str(result.inserted_id)
    return jsonify(product), 201


@app.route('/api/products/<id>', methods=['PUT'])
def update_product(id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    update_data = {}
    editable_fields = [
        'name', 'code', 'barcode', 'unit', 'category', 'group_id', 'group_name',
        'supplier', 'cost_price', 'markup_percent', 'price', 'mrp',
        'price_includes_tax', 'tax_rate', 'price_change_allowed',
        'stock', 'default_quantity', 'is_service', 'low_stock_enabled',
        'low_stock_quantity', 'reorder_level', 'preferred_quantity',
        'age_restriction_years', 'color', 'image_url', 'description', 'status'
    ]
    for field in editable_fields:
        if field in data:
            if field in ['price', 'cost_price', 'markup_percent', 'mrp', 'weight', 'discount_percent']:
                update_data[field] = float(data[field])
            elif field in ['stock', 'default_quantity', 'low_stock_quantity', 'reorder_level', 'preferred_quantity', 'age_restriction_years']:
                update_data[field] = int(data[field])
            elif field in ['price_includes_tax', 'price_change_allowed', 'is_service', 'low_stock_enabled']:
                update_data[field] = bool(data[field])
            else:
                update_data[field] = data[field]
    update_data['updated_at'] = datetime.utcnow().isoformat()

    if not update_data:
        return jsonify({'error': 'No fields to update'}), 400

    if USE_MEMORY_DB:
        result = db.update_one('products', {'_id': id}, {'$set': update_data})
        if result.modified_count > 0:
            product = db.find_one('products', {'_id': id})
            return jsonify(product)
        return jsonify({'error': 'Product not found'}), 404

    result = db.products.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    if result.modified_count > 0:
        product = db.products.find_one({'_id': ObjectId(id)})
        return jsonify(serialize_doc(product))
    return jsonify({'error': 'Product not found'}), 404


@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    comment = request.args.get('comment', 'No comment')
    doc_id = id if USE_MEMORY_DB else ObjectId(id)
    product = db.products.find_one({'_id': doc_id}) if not USE_MEMORY_DB else db.find_one('products', {'_id': id})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Record write-off
    write_off_doc = {
        'product_id': id,
        'product_name': product.get('name', ''),
        'quantity': product.get('stock', 0),
        'reason': comment,
        'written_off_by': session.get('username', 'unknown'),
        'timestamp': datetime.utcnow().isoformat()
    }
    if USE_MEMORY_DB:
        db.write_offs.append(write_off_doc)
        result = db.delete_one('products', {'_id': id})
    else:
        db.write_offs.insert_one(write_off_doc)
        result = db.products.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Product deleted', 'write_off_recorded': True})
    return jsonify({'error': 'Product not found'}), 404


# =============================================================================
# VENDORS API
# =============================================================================

@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    if USE_MEMORY_DB:
        vendors = db.find('vendors', {})
        return jsonify([serialize_doc(v) for v in vendors])
    vendors = list(db.vendors.find())
    return jsonify([serialize_doc(v) for v in vendors])


@app.route('/api/vendors/<vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    if USE_MEMORY_DB:
        vendor = db.find_one('vendors', {'_id': vendor_id})
    else:
        vendor = db.vendors.find_one({'_id': ObjectId(vendor_id)})
    if vendor:
        return jsonify(serialize_doc(vendor))
    return jsonify({'error': 'Vendor not found'}), 404


@app.route('/api/vendors', methods=['POST'])
def add_vendor():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    required = ['name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    vendor = {
        'name': data['name'],
        'contact_person': data.get('contact_person', ''),
        'phone': data.get('phone', ''),
        'email': data.get('email', ''),
        'address': data.get('address', ''),
        'city': data.get('city', ''),
        'status': data.get('status', 'active'),
        'payment_terms': data.get('payment_terms', 'Net 30'),
        'credit_limit': float(data.get('credit_limit', 0)),
        'tax_id': data.get('tax_id', ''),
        'notes': data.get('notes', ''),
        'created_at': datetime.utcnow().isoformat()
    }

    if USE_MEMORY_DB:
        result = db.insert_one('vendors', vendor)
    else:
        result = db.vendors.insert_one(vendor)
    vendor['_id'] = str(result.inserted_id)
    return jsonify(vendor), 201


@app.route('/api/vendors/<vendor_id>', methods=['PUT'])
def update_vendor(vendor_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    update_data = {}
    for field in ['name', 'contact_person', 'phone', 'email', 'address', 'city', 'status',
                  'payment_terms', 'credit_limit', 'tax_id', 'notes']:
        if field in data:
            if field == 'credit_limit':
                update_data[field] = float(data[field])
            else:
                update_data[field] = data[field]

    oid = vendor_id if USE_MEMORY_DB else ObjectId(vendor_id)
    if USE_MEMORY_DB:
        result = db.update_one('vendors', {'_id': vendor_id}, {'$set': update_data})
    else:
        result = db.vendors.update_one({'_id': ObjectId(vendor_id)}, {'$set': update_data})

    if result.modified_count > 0:
        if USE_MEMORY_DB:
            vendor = db.find_one('vendors', {'_id': vendor_id})
        else:
            vendor = db.vendors.find_one({'_id': ObjectId(vendor_id)})
        return jsonify(serialize_doc(vendor))
    return jsonify({'error': 'Vendor not found'}), 404


@app.route('/api/vendors/<vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    if USE_MEMORY_DB:
        result = db.delete_one('vendors', {'_id': vendor_id})
    else:
        result = db.vendors.delete_one({'_id': ObjectId(vendor_id)})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Vendor deleted'})
    return jsonify({'error': 'Vendor not found'}), 404


# =============================================================================
# PURCHASE ORDERS API
# =============================================================================

@app.route('/api/purchase-orders', methods=['GET'])
def get_purchase_orders():
    if USE_MEMORY_DB:
        orders = getattr(db, 'purchase_orders', [])
        return jsonify([serialize_doc(o) for o in orders])
    orders = list(db.purchase_orders.find().sort('order_date', -1))
    return jsonify([serialize_doc(o) for o in orders])


@app.route('/api/purchase-orders', methods=['POST'])
def create_purchase_order():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    required = ['vendor_id', 'items']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    total = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in data['items'])

    order_doc = {
        'vendor_id': data['vendor_id'],
        'vendor_name': data.get('vendor_name', ''),
        'items': data['items'],
        'total_amount': total,
        'paid_amount': data.get('paid_amount', 0),
        'pending_amount': total - data.get('paid_amount', 0),
        'payment_status': data.get('payment_status', 'pending'),
        'order_date': data.get('order_date', datetime.utcnow().isoformat()),
        'expected_delivery': data.get('expected_delivery', ''),
        'notes': data.get('notes', ''),
        'created_by': session.get('username', 'unknown'),
        'created_at': datetime.utcnow().isoformat()
    }

    if USE_MEMORY_DB:
        if not hasattr(db, 'purchase_orders'):
            db.purchase_orders = []
        order_doc['_id'] = str(len(db.purchase_orders) + 1)
        db.purchase_orders.append(order_doc)
        result_id = order_doc['_id']
    else:
        result = db.purchase_orders.insert_one(order_doc)
        result_id = str(result.inserted_id)

    return jsonify({'message': 'Purchase order created', 'order_id': result_id}), 201


# =============================================================================
# PRODUCT GROUPS API
# =============================================================================

@app.route('/api/product-groups', methods=['GET'])
def get_product_groups():
    if USE_MEMORY_DB:
        groups = getattr(db, 'product_groups', [])
        return jsonify([serialize_doc(g) for g in groups])
    groups = list(db.product_groups.find())
    return jsonify([serialize_doc(g) for g in groups])


@app.route('/api/product-groups', methods=['POST'])
def add_product_group():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Group name is required'}), 400
    group = {
        'name': name,
        'description': data.get('description', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    if USE_MEMORY_DB:
        if not hasattr(db, 'product_groups'):
            db.product_groups = []
        group['_id'] = str(len(db.product_groups) + 1)
        db.product_groups.append(group)
    else:
        result = db.product_groups.insert_one(group)
        group['_id'] = str(result.inserted_id)
    return jsonify(group), 201


@app.route('/api/product-groups/<group_id>', methods=['PUT'])
def update_product_group(group_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    update_data = {}
    for field in ['name', 'description']:
        if field in data:
            update_data[field] = data[field]
    if not update_data:
        return jsonify({'error': 'No fields to update'}), 400
    if USE_MEMORY_DB:
        groups = getattr(db, 'product_groups', [])
        for i, g in enumerate(groups):
            if str(g.get('_id')) == str(group_id):
                groups[i].update(update_data)
                return jsonify(serialize_doc(groups[i]))
        return jsonify({'error': 'Group not found'}), 404
    result = db.product_groups.update_one({'_id': ObjectId(group_id)}, {'$set': update_data})
    if result.modified_count > 0:
        group = db.product_groups.find_one({'_id': ObjectId(group_id)})
        return jsonify(serialize_doc(group))
    return jsonify({'error': 'Group not found'}), 404


@app.route('/api/product-groups/<group_id>', methods=['DELETE'])
def delete_product_group(group_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    if USE_MEMORY_DB:
        groups = getattr(db, 'product_groups', [])
        for i, g in enumerate(groups):
            if str(g.get('_id')) == str(group_id):
                del groups[i]
                return jsonify({'success': True, 'message': 'Group deleted'})
        return jsonify({'error': 'Group not found'}), 404
    result = db.product_groups.delete_one({'_id': ObjectId(group_id)})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Group deleted'})
    return jsonify({'error': 'Group not found'}), 404


# =============================================================================
# PRODUCT COMMENTS API
# =============================================================================

@app.route('/api/products/<product_id>/comments', methods=['GET'])
def get_product_comments(product_id):
    if USE_MEMORY_DB:
        comments = getattr(db, 'product_comments', [])
        product_comments = [c for c in comments if str(c.get('product_id')) == str(product_id)]
        return jsonify([serialize_doc(c) for c in product_comments])
    product_comments = list(db.product_comments.find({'product_id': product_id}).sort('created_at', -1))
    return jsonify([serialize_doc(c) for c in product_comments])


@app.route('/api/products/<product_id>/comments', methods=['POST'])
def add_product_comment(product_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    data = request.json
    comment_text = data.get('comment', '').strip()
    if not comment_text:
        return jsonify({'error': 'Comment text is required'}), 400
    comment = {
        'product_id': product_id,
        'comment': comment_text,
        'created_by': session.get('username', 'unknown'),
        'created_at': datetime.utcnow().isoformat()
    }
    if USE_MEMORY_DB:
        if not hasattr(db, 'product_comments'):
            db.product_comments = []
        comment['_id'] = str(len(db.product_comments) + 1)
        db.product_comments.append(comment)
    else:
        result = db.product_comments.insert_one(comment)
        comment['_id'] = str(result.inserted_id)
    return jsonify(comment), 201


@app.route('/api/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    if USE_MEMORY_DB:
        comments = getattr(db, 'product_comments', [])
        for i, c in enumerate(comments):
            if str(c.get('_id')) == str(comment_id):
                del comments[i]
                return jsonify({'success': True, 'message': 'Comment deleted'})
        return jsonify({'error': 'Comment not found'}), 404
    result = db.product_comments.delete_one({'_id': ObjectId(comment_id)})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Comment deleted'})
    return jsonify({'error': 'Comment not found'}), 404


# =============================================================================
# PRODUCT PRICES API (Date-wise pricing)
# =============================================================================
# PRODUCT PRICES API (Date-wise pricing)
# =============================================================================

@app.route('/api/prices', methods=['GET'])
def get_price_history():
    product_id = request.args.get('product_id')
    if USE_MEMORY_DB:
        prices = db.find_many('product_prices', {'product_id': product_id} if product_id else {})
        return jsonify([serialize_doc(p) for p in prices])

    query = {}
    if product_id:
        query['product_id'] = product_id
    prices = list(db.product_prices.find(query).sort('effective_date', -1))
    return jsonify([serialize_doc(p) for p in prices])


@app.route('/api/prices', methods=['POST'])
def add_product_price():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    required = ['product_id', 'price', 'effective_date']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    price_doc = {
        'product_id': data['product_id'],
        'product_name': data.get('product_name', ''),
        'price': float(data['price']),
        'old_price': float(data.get('old_price', 0)),
        'effective_date': data['effective_date'],
        'reason': data.get('reason', ''),
        'changed_by': session.get('username', 'unknown'),
        'created_at': datetime.utcnow().isoformat()
    }

    if USE_MEMORY_DB:
        db.product_prices.append(price_doc)
        price_doc['_id'] = str(len(db.product_prices))
    else:
        result = db.product_prices.insert_one(price_doc)
        price_doc['_id'] = str(result.inserted_id)

    return jsonify(price_doc), 201


# =============================================================================
# WRITE-OFFS API
# =============================================================================

@app.route('/api/write-offs', methods=['GET'])
def get_write_offs():
    if USE_MEMORY_DB:
        write_offs = getattr(db, 'write_offs', [])
        return jsonify(write_offs)
    write_offs = list(db.write_offs.find().sort('timestamp', -1))
    return jsonify([serialize_doc(w) for w in write_offs])


# =============================================================================
# UTILITY API
# =============================================================================

@app.route('/api/generate-barcode', methods=['GET'])
def generate_barcode():
    """Generate a unique numeric barcode (EAN-13 format)"""
    import random
    digits = [random.randint(0, 9) for _ in range(12)]
    total = sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(digits))
    check_digit = (10 - (total % 10)) % 10
    barcode = ''.join(str(d) for d in digits) + str(check_digit)
    return jsonify({'barcode': barcode})


@app.route('/api/colors', methods=['GET'])
def get_colors():
    """Return list of colors for product color dropdown"""
    if USE_MEMORY_DB:
        colors = getattr(db, 'colors', [])
        return jsonify([serialize_doc(c) for c in colors])
    colors = list(db.colors.find())
    return jsonify([serialize_doc(c) for c in colors])


@app.route('/api/colors', methods=['POST'])
def add_color():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    if not data.get('value') or not data.get('label'):
        return jsonify({'error': 'Value and label are required'}), 400
    if USE_MEMORY_DB:
        colors = getattr(db, 'colors', [])
        if any(c['value'] == data['value'] for c in colors):
            return jsonify({'error': 'Color value already exists'}), 400
        new_color = {'_id': str(len(colors) + 1), 'value': data['value'], 'label': data['label']}
        colors.append(new_color)
        return jsonify(serialize_doc(new_color)), 201
    else:
        existing = db.colors.find_one({'value': data['value']})
        if existing:
            return jsonify({'error': 'Color value already exists'}), 400
        result = db.colors.insert_one({'value': data['value'], 'label': data['label']})
        new_color = db.colors.find_one({'_id': result.inserted_id})
        return jsonify(serialize_doc(new_color)), 201


@app.route('/api/colors/<color_id>', methods=['PUT'])
def update_color(color_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    if not data.get('value') or not data.get('label'):
        return jsonify({'error': 'Value and label are required'}), 400
    update_data = {'value': data['value'], 'label': data['label']}
    if USE_MEMORY_DB:
        colors = getattr(db, 'colors', [])
        for i, c in enumerate(colors):
            if str(c.get('_id')) == str(color_id):
                if any(other['value'] == data['value'] and str(other.get('_id')) != str(color_id) for other in colors):
                    return jsonify({'error': 'Color value already exists'}), 400
                colors[i].update(update_data)
                return jsonify(serialize_doc(colors[i]))
        return jsonify({'error': 'Color not found'}), 404
    else:
        existing = db.colors.find_one({'value': data['value'], '_id': {'$ne': ObjectId(color_id)}})
        if existing:
            return jsonify({'error': 'Color value already exists'}), 400
        result = db.colors.update_one({'_id': ObjectId(color_id)}, {'$set': update_data})
        if result.modified_count > 0:
            color = db.colors.find_one({'_id': ObjectId(color_id)})
            return jsonify(serialize_doc(color))
        return jsonify({'error': 'Color not found'}), 404


@app.route('/api/colors/<color_id>', methods=['DELETE'])
def delete_color(color_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    if USE_MEMORY_DB:
        colors = getattr(db, 'colors', [])
        for i, c in enumerate(colors):
            if str(c.get('_id')) == str(color_id):
                del colors[i]
                return jsonify({'success': True, 'message': 'Color deleted'})
        return jsonify({'error': 'Color not found'}), 404
    result = db.colors.delete_one({'_id': ObjectId(color_id)})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Color deleted'})
    return jsonify({'error': 'Color not found'}), 404


# =============================================================================
# UNITS OF MEASURE API
# =============================================================================

@app.route('/api/units', methods=['GET'])
def get_units():
    if USE_MEMORY_DB:
        units = getattr(db, 'units', [])
        return jsonify([serialize_doc(u) for u in units])
    units = list(db.units.find())
    return jsonify([serialize_doc(u) for u in units])


@app.route('/api/units', methods=['POST'])
def add_unit():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Unit name is required'}), 400
    if USE_MEMORY_DB:
        units = getattr(db, 'units', [])
        if any(u['name'] == name for u in units):
            return jsonify({'error': 'Unit already exists'}), 400
        new_unit = {'_id': str(len(units) + 1), 'name': name}
        units.append(new_unit)
        return jsonify(serialize_doc(new_unit)), 201
    else:
        existing = db.units.find_one({'name': name})
        if existing:
            return jsonify({'error': 'Unit already exists'}), 400
        result = db.units.insert_one({'name': name})
        new_unit = db.units.find_one({'_id': result.inserted_id})
        return jsonify(serialize_doc(new_unit)), 201


@app.route('/api/units/<unit_id>', methods=['PUT'])
def update_unit(unit_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Unit name is required'}), 400
    if USE_MEMORY_DB:
        units = getattr(db, 'units', [])
        for i, u in enumerate(units):
            if str(u.get('_id')) == str(unit_id):
                if any(other['name'] == name and str(other.get('_id')) != str(unit_id) for other in units):
                    return jsonify({'error': 'Unit name already exists'}), 400
                units[i]['name'] = name
                return jsonify(serialize_doc(units[i]))
        return jsonify({'error': 'Unit not found'}), 404
    else:
        existing = db.units.find_one({'name': name, '_id': {'$ne': ObjectId(unit_id)}})
        if existing:
            return jsonify({'error': 'Unit name already exists'}), 400
        result = db.units.update_one({'_id': ObjectId(unit_id)}, {'$set': {'name': name}})
        if result.modified_count > 0:
            unit = db.units.find_one({'_id': ObjectId(unit_id)})
            return jsonify(serialize_doc(unit))
        return jsonify({'error': 'Unit not found'}), 404


@app.route('/api/units/<unit_id>', methods=['DELETE'])
def delete_unit(unit_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    if USE_MEMORY_DB:
        units = getattr(db, 'units', [])
        for i, u in enumerate(units):
            if str(u.get('_id')) == str(unit_id):
                del units[i]
                return jsonify({'success': True, 'message': 'Unit deleted'})
        return jsonify({'error': 'Unit not found'}), 404
    result = db.units.delete_one({'_id': ObjectId(unit_id)})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Unit deleted'})
    return jsonify({'error': 'Unit not found'}), 404




# =============================================================================
# REPORTS API
# =============================================================================

@app.route('/api/reports/daily-products', methods=['GET'])
def daily_products_report():
    """Daily products registered report"""
    date_filter = request.args.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
    vendor_filter = request.args.get('vendor')
    category_filter = request.args.get('category')

    if USE_MEMORY_DB:
        products = db.find('products', {})
        if vendor_filter:
            products = [p for p in products if vendor_filter.lower() in (p.get('supplier', '') or '').lower()]
        if category_filter:
            products = [p for p in products if p.get('category') == category_filter]
        return jsonify(products)

    query = {}
    if vendor_filter:
        query['supplier'] = {'$regex': vendor_filter, '$options': 'i'}
    if category_filter:
        query['category'] = category_filter
    products = list(db.products.find(query))
    return jsonify([serialize_doc(p) for p in products])


@app.route('/api/reports/stock-report', methods=['GET'])
def stock_report():
    """Remaining stock report"""
    vendor = request.args.get('vendor')
    product_id = request.args.get('product')
    sort_by_stock = request.args.get('sort', 'stock')

    if USE_MEMORY_DB:
        products = db.find('products', {})
        if vendor:
            products = [p for p in products if vendor.lower() in (p.get('supplier', '') or '').lower()]
        if product_id:
            products = [p for p in products if str(p.get('_id')) == str(product_id)]
        products = sorted(products, key=lambda x: x.get('stock', 0))
        return jsonify([serialize_doc(p) for p in products])

    query = {}
    if vendor:
        query['supplier'] = {'$regex': vendor, '$options': 'i'}
    if product_id:
        query['_id'] = ObjectId(product_id)

    products = list(db.products.find(query).sort('stock', 1))
    return jsonify([serialize_doc(p) for p in products])


@app.route('/api/reports/expiry-report', methods=['GET'])
def expiry_report():
    """Expiry report"""
    vendor = request.args.get('vendor')
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    if USE_MEMORY_DB:
        products = db.find('products', {})
        results = []
        for p in products:
            exp = p.get('expiry_date', '')
            if exp:
                if vendor and vendor.lower() not in (p.get('supplier', '') or '').lower():
                    continue
                if date_from and exp < date_from:
                    continue
                if date_to and exp > date_to:
                    continue
                results.append(p)
        return jsonify(results)

    query = {'expiry_date': {'$exists': True, '$ne': ''}}
    if vendor:
        query['supplier'] = {'$regex': vendor, '$options': 'i'}
    if date_from and date_to:
        query['expiry_date'] = {'$gte': date_from, '$lte': date_to}
    elif date_from:
        query['expiry_date'] = {'$gte': date_from}
    elif date_to:
        query['expiry_date'] = {'$lte': date_to}

    products = list(db.products.find(query))
    return jsonify([serialize_doc(p) for p in products])


@app.route('/api/reports/price-list', methods=['GET'])
def price_list_report():
    """Product price list"""
    vendor = request.args.get('vendor')

    if USE_MEMORY_DB:
        products = db.find('products', {})
        if vendor:
            products = [p for p in products if vendor.lower() in (p.get('supplier', '') or '').lower()]
        result = []
        for p in products:
            result.append({
                'name': p['name'],
                'barcode': p.get('barcode', ''),
                'category': p.get('category', ''),
                'supplier': p.get('supplier', ''),
                'selling_price': p['price'],
                'cost_price': p.get('cost_price', 0),
                'mrp': p.get('mrp', 0),
                'discount_percent': p.get('discount_percent', 0),
                'effective_price': round(p['price'] * (1 - p.get('discount_percent', 0) / 100), 2),
            })
        return jsonify(result)

    query = {}
    if vendor:
        query['supplier'] = {'$regex': vendor, '$options': 'i'}
    products = list(db.products.find(query))
    result = []
    for p in products:
        result.append({
            'name': p['name'],
            'barcode': p.get('barcode', ''),
            'category': p.get('category', ''),
            'supplier': p.get('supplier', ''),
            'selling_price': p['price'],
            'cost_price': p.get('cost_price', 0),
            'mrp': p.get('mrp', 0),
            'discount_percent': p.get('discount_percent', 0),
            'effective_price': round(p['price'] * (1 - p.get('discount_percent', 0) / 100), 2),
        })
    return jsonify(result)


@app.route('/api/reports/slow-moving', methods=['GET'])
def slow_moving_report():
    """Slow moving items report"""
    data = slow_moving_report_data()
    # Serialize for JSON response
    if USE_MEMORY_DB:
        return jsonify(data)
    else:
        # Convert ObjectId in _id field to string for each item
        serialized = []
        for item in data:
            if '_id' in item and not isinstance(item['_id'], str):
                item['_id'] = str(item['_id'])
            serialized.append(item)
        return jsonify(serialized)


@app.route('/api/reports/vendor-payment', methods=['GET'])
def vendor_payment_report():
    """Vendor payment report"""
    vendor_id = request.args.get('vendor_id')
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    if USE_MEMORY_DB:
        orders = getattr(db, 'purchase_orders', [])
        if vendor_id:
            orders = [o for o in orders if o.get('vendor_id') == vendor_id]
        return jsonify(orders)

    query = {}
    if vendor_id:
        query['vendor_id'] = vendor_id
    orders = list(db.purchase_orders.find(query).sort('order_date', -1))
    return jsonify([serialize_doc(o) for o in orders])


# =============================================================================
# QR CODE ENDPOINT
# =============================================================================

@app.route('/api/products/qr/<product_id>', methods=['GET'])
def get_product_qr(product_id):
    """Generate QR code info for a product"""
    if USE_MEMORY_DB:
        product = db.find_one('products', {'_id': product_id})
    else:
        product = db.products.find_one({'_id': ObjectId(product_id)})

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    qr_data = {
        'product_id': str(product['_id']),
        'name': product['name'],
        'price': product['price'],
        'barcode': product.get('barcode', ''),
        'qr_code': product.get('qr_code', ''),
        'discount_percent': product.get('discount_percent', 0),
        'discounted_price': round(product['price'] * (1 - product.get('discount_percent', 0) / 100), 2)
    }
    return jsonify(qr_data)


# =============================================================================
# CATEGORIES API
# =============================================================================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    if USE_MEMORY_DB:
        cats = db.find('categories', {})
        return jsonify([{'_id': c.get('_id'), 'name': c['name']} for c in cats])
    categories = list(db.categories.find())
    return jsonify([serialize_doc(c) for c in categories])


@app.route('/api/categories', methods=['POST'])
def add_category():
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Category name required'}), 400
    name = data['name'].strip()

    if USE_MEMORY_DB:
        categories = getattr(db, 'categories', [])
        if any(c['name'] == name for c in categories):
            return jsonify({'error': 'Category already exists'}), 400
        result = db.insert_one('categories', {'name': name})
    else:
        existing = db.categories.find_one({'name': name})
        if existing:
            return jsonify({'error': 'Category already exists'}), 400
        result = db.categories.insert_one({'name': name})
    return jsonify({'_id': str(result.inserted_id), 'name': name}), 201

@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    if 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Category name is required'}), 400
    new_name = data['name'].strip()
    if USE_MEMORY_DB:
        categories = getattr(db, 'categories', [])
        for i, cat in enumerate(categories):
            if str(cat.get('_id')) == str(category_id):
                if any(c['name'] == new_name and str(c.get('_id')) != str(category_id) for c in categories):
                    return jsonify({'error': 'Category name already exists'}), 400
                categories[i]['name'] = new_name
                return jsonify(categories[i])
        return jsonify({'error': 'Category not found'}), 404
    else:
        existing = db.categories.find_one({'name': new_name, '_id': {'$ne': ObjectId(category_id)}})
        if existing:
            return jsonify({'error': 'Category name already exists'}), 400
        result = db.categories.update_one({'_id': ObjectId(category_id)}, {'$set': {'name': new_name}})
        if result.modified_count > 0:
            cat = db.categories.find_one({'_id': ObjectId(category_id)})
            return jsonify(serialize_doc(cat))
        return jsonify({'error': 'Category not found'}), 404

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    if USE_MEMORY_DB:
        categories = getattr(db, 'categories', [])
        for i, cat in enumerate(categories):
            if str(cat.get('_id')) == str(category_id):
                del categories[i]
                return jsonify({'success': True, 'message': 'Category deleted'})
        return jsonify({'error': 'Category not found'}), 404
    result = db.categories.delete_one({'_id': ObjectId(category_id)})
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Category deleted'})
    return jsonify({'error': 'Category not found'}), 404

# =============================================================================
# SALES API
# =============================================================================

@app.route('/api/sales', methods=['POST'])
def create_sale():
    if session.get('role') not in ['admin', 'procurement_manager', 'sales_person', 'cashier']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    if 'items' not in data or not data['items']:
        return jsonify({'error': 'No items in cart'}), 400

    total = 0
    sale_items = []
    product_ids = [str(item['product_id']) for item in data['items']]

    if USE_MEMORY_DB:
        products = {p['_id']: p for p in db.find('products', {}) if p['_id'] in product_ids}
    else:
        product_objs = db.products.find({'_id': {'$in': [ObjectId(pid) for pid in product_ids]}})
        products = {str(p['_id']): p for p in product_objs}

    for item in data['items']:
        pid = str(item['product_id'])
        if pid in products:
            product = products[pid]
            quantity = item['quantity']
            price = product['price']
            subtotal = price * quantity
            total += subtotal
            sale_items.append({
                'product_id': pid,
                'product_name': product['name'],
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            })
            if USE_MEMORY_DB:
                p = db.find_one('products', {'_id': pid})
                if p:
                    p['stock'] = p.get('stock', 0) - quantity
            else:
                db.products.update_one({'_id': ObjectId(pid)}, {'$inc': {'stock': -quantity}})

    payment_method = data.get('payment_method', 'cash')
    customer_name = data.get('customer_name', '')

    sale_doc = {
        'items': sale_items,
        'total': total,
        'payment_method': payment_method,
        'customer_name': customer_name,
        'timestamp': datetime.utcnow()
    }

    if USE_MEMORY_DB:
        sale_doc['_id'] = get_next_id('sales')
        db.sales.append(sale_doc)
        result_id = sale_doc['_id']
    else:
        result = db.sales.insert_one(sale_doc)
        result_id = str(result.inserted_id)

    # Prepare response (do not mutate stored doc in memory mode)
    response_sale = sale_doc.copy()
    response_sale['_id'] = result_id
    if isinstance(response_sale.get('timestamp'), datetime):
        response_sale['timestamp'] = response_sale['timestamp'].isoformat()
    return jsonify({
        'message': 'Sale completed',
        'sale': response_sale,
        'receipt_number': result_id[:8]
    }), 201


@app.route('/api/sales', methods=['GET'])
def get_sales():
    if session.get('role') not in ['admin', 'procurement_manager', 'sales_person', 'cashier']:
        return jsonify({'error': 'Unauthorized'}), 403
    limit = int(request.args.get('limit', 50))
    if USE_MEMORY_DB:
        sales = sorted(getattr(db, 'sales', []), key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        for s in sales:
            if '_id' in s and not isinstance(s['_id'], str):
                s['_id'] = str(s['_id'])
            if isinstance(s.get('timestamp'), datetime):
                s['timestamp'] = s['timestamp'].isoformat()
        return jsonify(sales)
    sales = list(db.sales.find().sort('timestamp', -1).limit(limit))
    for s in sales:
        s['_id'] = str(s['_id'])
        if isinstance(s.get('timestamp'), datetime):
            s['timestamp'] = s['timestamp'].isoformat()
    return jsonify(sales)


@app.route('/api/stats/today', methods=['GET'])
def today_stats():
    if USE_MEMORY_DB:
        today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        sales = getattr(db, 'sales', [])
        today_sales = [s for s in sales if isinstance(s.get('timestamp'), datetime) and s['timestamp'] >= today_start]
        total_sales = sum(s['total'] for s in today_sales)
        transactions = len(today_sales)
        product_count = db.count_documents('products', {})
        low_stock = len([p for p in db.find('products', {}) if p.get('stock', 0) < (p.get('reorder_level') or 10)])
        return jsonify({
            'today_sales': total_sales,
            'today_transactions': transactions,
            'total_products': product_count,
            'low_stock_products': low_stock
        })
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    today_end = datetime.combine(datetime.utcnow().date(), datetime.max.time())
    pipeline = [
        {'$match': {'timestamp': {'$gte': today_start, '$lte': today_end}}},
        {'$group': {
            '_id': None,
            'total_sales': {'$sum': '$total'},
            'total_transactions': {'$sum': 1}
        }}
    ]
    summary = list(db.sales.aggregate(pipeline))
    product_count = db.products.count_documents({})
    low_stock = db.products.count_documents({
        '$expr': {
            '$lt': ['$stock', {'$ifNull': ['$reorder_level', 10]}]
        }
    })
    if summary:
        return jsonify({
            'today_sales': summary[0]['total_sales'],
            'today_transactions': summary[0]['total_transactions'],
            'total_products': product_count,
            'low_stock_products': low_stock
        })
    return jsonify({
        'today_sales': 0,
        'today_transactions': 0,
        'total_products': product_count,
        'low_stock_products': low_stock
    })


@app.route('/api/sales/by-category', methods=['GET'])
def sales_by_category():
    if USE_MEMORY_DB:
        product_sales = {}
        for sale in getattr(db, 'sales', []):
            for item in sale.get('items', []):
                pid = item.get('product_id')
                prod = db.find_one('products', {'_id': pid})
                name = (prod.get('name') if prod else 'Unknown')
                if name not in product_sales:
                    product_sales[name] = {'quantity_sold': 0, 'revenue': 0}
                product_sales[name]['quantity_sold'] += item.get('quantity', 0)
                product_sales[name]['revenue'] += item.get('subtotal', 0)
        result = [{'name': k, 'quantity_sold': v['quantity_sold'], 'revenue': v['revenue']} for k, v in product_sales.items()]
        result.sort(key=lambda x: x['revenue'], reverse=True)
        return jsonify(result[:20])
    pipeline = [
        {'$unwind': '$items'},
        {'$group': {
            '_id': '$items.product_name',
            'quantity_sold': {'$sum': '$items.quantity'},
            'revenue': {'$sum': '$items.subtotal'}
        }},
        {'$sort': {'revenue': -1}},
        {'$limit': 20}
    ]
    results = list(db.sales.aggregate(pipeline))
    for r in results:
        r['name'] = r.pop('_id')
    return jsonify(results)


# =============================================================================
# UPLOAD PRODUCTS (Existing)
# =============================================================================

@app.route('/api/upload/products', methods=['POST'])
def upload_products():
    """Upload products from CSV/JSON file"""
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        content = file.read().decode('utf-8')
        file_format = file.filename.rsplit('.', 1)[-1].lower()

        if file_format == 'csv':
            import csv
            from io import StringIO
            reader = csv.DictReader(StringIO(content))
            products_data = list(reader)
        elif file_format in ('json', 'txt'):
            products_data = json.loads(content)
            if isinstance(products_data, dict) and 'products' in products_data:
                products_data = products_data['products']
        else:
            return jsonify({'error': 'Unsupported file format. Use CSV or JSON'}), 400

        inserted = 0
        errors = []
        for i, item in enumerate(products_data):
            try:
                product = {
                    'name': item.get('name', f'Product {i+1}'),
                    'price': float(item.get('price', 0)),
                    'category': item.get('category', 'General'),
                    'barcode': item.get('barcode', ''),
                    'stock': int(item.get('stock', 0)),
                    'unit': item.get('unit', 'piece'),
                    'supplier': item.get('supplier', ''),
                    'cost_price': float(item.get('cost_price', 0)),
                    'mrp': float(item.get('mrp', 0)),
                    'discount_percent': float(item.get('discount_percent', 0)),
                    'reorder_level': int(item.get('reorder_level', 10)),
                    'tax_rate': float(item.get('tax_rate', 0)),
                    'hsn_code': item.get('hsn_code', ''),
                    'expiry_date': item.get('expiry_date', ''),
                    'batch_no': item.get('batch_no', ''),
                    'manufacturer': item.get('manufacturer', ''),
                    'qr_code': item.get('qr_code', secrets.token_hex(8)),
                    'created_at': datetime.utcnow().isoformat()
                }
                if USE_MEMORY_DB:
                    db.insert_one('products', product)
                else:
                    db.products.insert_one(product)
                inserted += 1
            except Exception as e:
                errors.append(f'Row {i+1}: {str(e)}')

        return jsonify({
            'message': f'Upload complete',
            'inserted': inserted,
            'errors': len(errors),
            'error_details': errors[:10]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 400


@app.route('/api/upload/excel-products', methods=['POST'])
def upload_excel_products():
    """Upload products from Excel file with duplicate/merge options"""
    if session.get('role') not in ['admin', 'procurement_manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Get options from form data
    skip_duplicates = request.form.get('skip_duplicates', 'true').lower() == 'true'
    merge_duplicates = request.form.get('merge_duplicates', 'true').lower() == 'true'
    upload_type = request.form.get('upload_type', 'inventory')  # inventory or purchase
    default_category = request.form.get('category', '').strip()
    default_group = request.form.get('product_group', '').strip()
    default_quantity = request.form.get('default_quantity', '').strip()
    default_expiry = request.form.get('default_expiry', '').strip()
    default_color = request.form.get('color', '').strip()

    try:
        from openpyxl import load_workbook
        from io import BytesIO

        wb = load_workbook(filename=BytesIO(file.read()), read_only=True)
        ws = wb.active

        products_data = []
        headers = None

        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                headers = [str(h).strip() if h else f'col_{i}' for i, h in enumerate(row)]
                continue
            if not any(row):
                continue
            row_dict = {}
            for idx, val in enumerate(row):
                if idx < len(headers):
                    row_dict[headers[idx]] = val
            products_data.append(row_dict)

        wb.close()

        inserted = 0
        updated = 0
        skipped = 0
        errors = []

        for i, item in enumerate(products_data):
            try:
                product_name = str(item.get('Name', f'Product {i+1}')).strip()
                if not product_name or product_name == 'None':
                    continue

                cost = float(item.get('Cost') or item.get('cost') or 0)
                markup = float(item.get('Markup') or item.get('markup') or 0)
                price = float(item.get('Price') or item.get('price') or (cost * (1 + markup / 100)) or 0)
                mrp = float(item.get('Price') or item.get('mrp') or price)

                barcode_val = item.get('Barcode') or item.get('barcode') or ''
                barcode_str = str(barcode_val) if barcode_val else ''

                product = {
                    'name': product_name,
                    'code': str(item.get('SKU') or item.get('code') or ''),
                    'barcode': barcode_str,
                    'qr_code': secrets.token_hex(8),
                    'unit': str(item.get('Measurement unit') or item.get('unit') or 'piece'),
                    'category': str(item.get('Product group') or item.get('category') or default_category or 'General'),
                    'group_name': str(item.get('Product group') or default_group or ''),
                    'supplier': str(item.get('Supplier') or item.get('supplier') or ''),
                    'cost_price': cost,
                    'markup_percent': markup,
                    'price': price,
                    'mrp': mrp,
                    'price_includes_tax': str(item.get('Tax inclusive price') or '').lower() in ('true', '1', 'yes') if item.get('Tax inclusive price') else False,
                    'tax_rate': float(item.get('Tax') or item.get('tax_rate') or 0),
                    'price_change_allowed': str(item.get('Price change allowed') or '').lower() in ('true', '1', 'yes') if item.get('Price change allowed') else True,
                    'stock': int(item.get('Quantity') or item.get('stock') or (int(default_quantity) if default_quantity else 0)),
                    'default_quantity': int(item.get('Using default quantity') or item.get('default_quantity') or 1),
                    'expiry_date': str(item.get('Expiry date') or item.get('expiry_date') or default_expiry or ''),
                    'color': str(item.get('Color') or item.get('color') or default_color or ''),
                    'is_service': str(item.get('Service (not using stock)') or '').lower() in ('true', '1', 'yes') if item.get('Service (not using stock)') else False,
                    'enabled': str(item.get('Enabled') or '').lower() in ('true', '1', 'yes') if item.get('Enabled') else True,
                    'low_stock_enabled': str(item.get('Low stock warning') or '').lower() in ('true', '1', 'yes') if item.get('Low stock warning') else False,
                    'low_stock_quantity': int(item.get('Low stock warning quantity') or item.get('low_stock_quantity') or 0),
                    'reorder_level': int(item.get('Reorder point') or item.get('reorder_level') or 10),
                    'preferred_quantity': int(item.get('Preferred quantity') or item.get('preferred_quantity') or 0),
                    'description': str(item.get('Description') or ''),
                    'status': 'active' if item.get('Enabled') is None or str(item.get('Enabled')).lower() in ('true', '1', 'yes') else 'inactive',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }

                existing = None
                if USE_MEMORY_DB:
                    for p in db.find('products', {}):
                        if p.get('barcode') and str(p.get('barcode')) == barcode_str:
                            existing = p
                            break
                        if str(p.get('name', '')).lower() == product_name.lower() and not barcode_str:
                            existing = p
                            break
                else:
                    if barcode_str:
                        existing = db.products.find_one({'barcode': barcode_str})
                    if not existing:
                        existing = db.products.find_one({'name': {'$regex': f'^{product_name}$', '$options': 'i'}})

                if existing:
                    if skip_duplicates and not merge_duplicates:
                        skipped += 1
                        continue
                    elif merge_duplicates:
                        update_data = {k: v for k, v in product.items() if k not in ('_id', 'created_at')}
                        update_data['updated_at'] = datetime.utcnow().isoformat()
                        if USE_MEMORY_DB:
                            db.update_one('products', {'_id': existing['_id']}, {'$set': update_data})
                        else:
                            db.products.update_one({'_id': ObjectId(existing['_id'])}, {'$set': update_data})
                        updated += 1
                        continue

                if USE_MEMORY_DB:
                    db.insert_one('products', product)
                else:
                    db.products.insert_one(product)
                inserted += 1

            except Exception as e:
                errors.append(f'Row {i+2}: {str(e)}')

        type_msg = 'Inventory' if upload_type == 'inventory' else 'Purchase'
        return jsonify({
            'message': f'{type_msg} upload complete',
            'inserted': inserted,
            'updated': updated,
            'skipped': skipped,
            'errors': len(errors),
            'error_details': errors[:10]
        })

    except Exception as e:
        return jsonify({'error': f'Failed to process Excel file: {str(e)}'}), 400


# =============================================================================
# LEGACY ROUTES (backward compatible)
# =============================================================================

@app.route('/dashboard')
def dashboard_legacy():
    return render_template('dashboard.html')


# =============================================================================
# REPORT VIEWER & EXPORT
# =============================================================================

@app.route('/reports/<report_type>')
def report_viewer(report_type):
    """HTML report viewer page"""
    valid_reports = [
        'stock-report', 'expiry-report', 'price-list',
        'slow-moving', 'vendor-payment', 'daily-products'
    ]
    if report_type not in valid_reports:
        return "Invalid report type", 404
    return render_template('report_viewer.html', report_type=report_type)


def dicts_to_csv(data, headers):
    """Convert list of dicts to CSV string"""
    import io
    import csv
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction='ignore')
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()


@app.route('/api/reports/stock-report/excel')
def stock_report_excel():
    data = stock_report_data()  # Will call existing function after defined
    headers = ['name', 'category', 'supplier', 'stock', 'unit', 'price']
    csv_data = dicts_to_csv(data, headers)
    return excel_response(csv_data, 'stock_report')


@app.route('/api/reports/expiry-report/excel')
def expiry_report_excel():
    data = expiry_report_data()
    headers = ['name', 'batch_no', 'expiry_date', 'stock']
    csv_data = dicts_to_csv(data, headers)
    return excel_response(csv_data, 'expiry_report')


@app.route('/api/reports/price-list/excel')
def price_list_excel():
    data = price_list_report_data()
    headers = ['name', 'barcode', 'category', 'supplier', 'selling_price', 'cost_price', 'mrp', 'discount_percent']
    csv_data = dicts_to_csv(data, headers)
    return excel_response(csv_data, 'price_list')


@app.route('/api/reports/slow-moving/excel')
def slow_moving_excel():
    data = slow_moving_report_data()
    headers = ['name', 'category', 'stock', 'last_sold', 'days_since']
    csv_data = dicts_to_csv(data, headers)
    return excel_response(csv_data, 'slow_moving')


@app.route('/api/reports/vendor-payment/excel')
def vendor_payment_excel():
    data = vendor_payment_report_data()
    headers = ['_id', 'vendor_name', 'order_date', 'total_amount', 'paid_amount', 'pending_amount', 'payment_status']
    csv_data = dicts_to_csv(data, headers)
    return excel_response(csv_data, 'vendor_payment')


@app.route('/api/reports/daily-products/excel')
def daily_products_excel():
    data = daily_products_report_data()
    headers = ['name', 'category', 'supplier', 'stock']
    csv_data = dicts_to_csv(data, headers)
    return excel_response(csv_data, 'daily_products')


def excel_response(csv_content, filename):
    """Return CSV as Excel downloadable response"""
    from io import BytesIO
    bio = BytesIO(csv_content.encode('utf-8-sig'))  # BOM for Excel
    bio.seek(0)
    from flask import send_file
    return send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{filename}_{datetime.utcnow().strftime("%Y-%m-%d")}.csv'
    )


# Helper data functions for Excel exports (duplicate logic from above, but return raw data)
def stock_report_data():
    vendor = request.args.get('vendor')
    product_id = request.args.get('product')
    if USE_MEMORY_DB:
        products = db.find('products', {})
        if vendor:
            products = [p for p in products if vendor.lower() in (p.get('supplier', '') or '').lower()]
        if product_id:
            products = [p for p in products if str(p.get('_id')) == str(product_id)]
        return products
    query = {}
    if vendor:
        query['supplier'] = {'$regex': vendor, '$options': 'i'}
    if product_id:
        query['_id'] = ObjectId(product_id)
    return list(db.products.find(query).sort('stock', 1))


def expiry_report_data():
    vendor = request.args.get('vendor')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    if USE_MEMORY_DB:
        products = db.find('products', {})
        results = []
        for p in products:
            exp = p.get('expiry_date', '')
            if exp:
                if vendor and vendor.lower() not in (p.get('supplier', '') or '').lower():
                    continue
                if date_from and exp < date_from:
                    continue
                if date_to and exp > date_to:
                    continue
                results.append(p)
        return results
    query = {'expiry_date': {'$exists': True, '$ne': ''}}
    if vendor:
        query['supplier'] = {'$regex': vendor, '$options': 'i'}
    if date_from and date_to:
        query['expiry_date'] = {'$gte': date_from, '$lte': date_to}
    elif date_from:
        query['expiry_date'] = {'$gte': date_from}
    elif date_to:
        query['expiry_date'] = {'$lte': date_to}
    return list(db.products.find(query))


def price_list_report_data():
    vendor = request.args.get('vendor')
    if USE_MEMORY_DB:
        products = db.find('products', {})
        if vendor:
            products = [p for p in products if vendor.lower() in (p.get('supplier', '') or '').lower()]
        result = []
        for p in products:
            result.append({
                'name': p['name'],
                'barcode': p.get('barcode', ''),
                'category': p.get('category', ''),
                'supplier': p.get('supplier', ''),
                'selling_price': p['price'],
                'cost_price': p.get('cost_price', 0),
                'mrp': p.get('mrp', 0),
                'discount_percent': p.get('discount_percent', 0)
            })
        return result
    query = {}
    if vendor:
        query['supplier'] = {'$regex': vendor, '$options': 'i'}
    products = list(db.products.find(query))
    result = []
    for p in products:
        result.append({
            'name': p['name'],
            'barcode': p.get('barcode', ''),
            'category': p.get('category', ''),
            'supplier': p.get('supplier', ''),
            'selling_price': p['price'],
            'cost_price': p.get('cost_price', 0),
            'mrp': p.get('mrp', 0),
            'discount_percent': p.get('discount_percent', 0)
        })
    return result


def slow_moving_report_data():
    days = int(request.args.get('days', 30))
    cutoff = datetime.utcnow() - timedelta(days=days)
    if USE_MEMORY_DB:
        products = db.find('products', {})
        recent_sales = getattr(db, 'sales', [])
        product_ids_sold = set()
        for s in recent_sales:
            s_date = s.get('timestamp')
            if isinstance(s_date, str):
                try:
                    s_date = datetime.fromisoformat(s_date)
                except:
                    s_date = datetime.min
            if s_date >= cutoff:
                for item in s.get('items', []):
                    product_ids_sold.add(item.get('product_id', ''))
        slow_items = [p for p in products if str(p.get('_id')) not in product_ids_sold]
        for p in slow_items:
            p['days_since'] = days
            # Find last sale ever
            last_sold = None
            for s in recent_sales:
                s_date = s.get('timestamp')
                if isinstance(s_date, str):
                    try:
                        s_date = datetime.fromisoformat(s_date)
                    except:
                        continue
                if s_date:
                    for item in s.get('items', []):
                        if item.get('product_id') == str(p.get('_id')):
                            if not last_sold or s_date > last_sold:
                                last_sold = s_date
            p['last_sold'] = last_sold.strftime('%Y-%m-%d') if last_sold else 'Never'
        return slow_items
    pipeline = [
        {'$match': {'timestamp': {'$gte': cutoff}}},
        {'$unwind': '$items'},
        {'$group': {'_id': '$items.product_id'}},
        {'$project': {'_id': 1}}
    ]
    sold_products = {str(r['_id']) for r in db.sales.aggregate(pipeline)}
    unsold = list(db.products.find({'_id': {'$nin': [ObjectId(pid) for pid in sold_products]}}))
    for p in unsold:
        p['days_since'] = days
        # Find last sale ever (if any)
        last_sale = db.sales.find({'items.product_id': p['_id']}).sort('timestamp', -1).limit(1)
        last_list = list(last_sale)
        if last_list:
            ts = last_list[0]['timestamp']
            if isinstance(ts, datetime):
                p['last_sold'] = ts.strftime('%Y-%m-%d')
            else:
                p['last_sold'] = str(ts)
        else:
            p['last_sold'] = 'Never'
    return unsold


def vendor_payment_report_data():
    vendor_id = request.args.get('vendor_id')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    if USE_MEMORY_DB:
        orders = getattr(db, 'purchase_orders', [])
        if vendor_id:
            orders = [o for o in orders if o.get('vendor_id') == vendor_id]
        return orders
    query = {}
    if vendor_id:
        query['vendor_id'] = vendor_id
    return list(db.purchase_orders.find(query).sort('order_date', -1))


def daily_products_report_data():
    date_filter = request.args.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
    vendor_filter = request.args.get('vendor')
    category_filter = request.args.get('category')
    if USE_MEMORY_DB:
        products = db.find('products', {})
        if vendor_filter:
            products = [p for p in products if vendor_filter.lower() in (p.get('supplier', '') or '').lower()]
        if category_filter:
            products = [p for p in products if p.get('category') == category_filter]
        return products
    query = {}
    if vendor_filter:
        query['supplier'] = {'$regex': vendor_filter, '$options': 'i'}
    if category_filter:
        query['category'] = category_filter
    return list(db.products.find(query))


# =============================================================================
# MAIN ENTRY
# =============================================================================

if __name__ == '__main__':
    print("Initializing POS System...")
    init_db()
    print(f"Database: {'MongoDB' if not USE_MEMORY_DB else 'In-Memory (demo mode)'}")
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting POS server on http://0.0.0.0:{port}")
    app.run(debug=False, port=port, host='0.0.0.0')