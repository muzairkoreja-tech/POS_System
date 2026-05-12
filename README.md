# POS Supermarket System - Setup Guide

A complete Point of Sale system for small supermarkets built with Flask (Python) and MongoDB. Features a clean Odoo-like interface.

## Features

- **Product Catalog**: Grid view with product images, prices, and stock levels
- **Shopping Cart**: Add/remove items, adjust quantities with stock validation
- **Checkout**: Multiple payment methods (Cash, Card, Mobile) with change calculation
- **Receipt Generation**: Print-ready receipts with transaction details
- **Dashboard**: Sales statistics, charts, low stock alerts
- **Product Management**: Search, filter by category
- **Real-time Stock Updates**: Automatic inventory deduction on sale

## Quick Start

### 1. Install Dependencies

```bash
cd pos_system
pip install -r requirements.txt
```

### 2. Install & Start MongoDB

**Windows (using Chocolatey):**
```bash
choco install mongodb-community
net start MongoDB
```

**Or download from:** https://www.mongodb.com/try/download/community

**Alternative (Docker):**
```bash
docker run -d -p 27017:27017 --name pos-mongo mongo:latest
```

### 3. Configure Environment (Optional)

Copy `.env.example` to `.env` and modify if needed:
```bash
cp .env.example .env
```

```env
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
```

### 4. Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

## Project Structure

```
pos_system/
├── app.py                 # Flask backend with MongoDB models and API
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
│
├── templates/
│   ├── index.html         # Main POS interface
│   └── dashboard.html     # Sales dashboard/reports
│
└── static/
    ├── css/
    │   └── style.css      # Clean Odoo-inspired styling
    ├── js/
    │   └── main.js        # POS functionality (cart, checkout, etc.)
    └── images/            # (optional) product images
```

## API Endpoints

### Products
- `GET /api/products` - Get all products (filterable by category/search)
- `POST /api/products` - Add new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Add new category

### Sales/Transactions
- `POST /api/sales` - Create new sale
- `GET /api/sales` - Get sales history
- `GET /api/sales/summary` - Sales summary
- `GET /api/sales/by-category` - Sales grouped by product

### Dashboard
- `GET /api/stats/today` - Today's statistics

## Using the POS

### Basic Operations

1. **Add to Cart**: Double-click any product card
2. **Adjust Quantity**: Use +/- buttons in cart
3. **Checkout**: Click "Checkout" button
4. **Payment**: Select cash/card/mobile, enter amount received
5. **Print Receipt**: Receipt modal opens automatically after sale

### Keyboard Shortcuts

- `F12` - Open Dashboard
- `ESC` - Close modals

### Cart Actions

- **Hold Order**: Temporarily save cart (persists in browser)
- **Recall Order**: Retrieve held order

### Stock Management

- Products show stock count on card (red if below 10)
- Cart prevents exceeding available stock
- Stock automatically reduced after sale

## Sample Data

The system initializes with sample products across categories:
- Fruits (Apple, Banana, Orange)
- Dairy (Milk, Cheese, Yogurt)
- Bakery (Bread, Croissant, Cookies)
- Grains (Rice, Pasta)
- Meat (Chicken, Beef, Fish)
- Beverages (Coke, Juice, Water)

Customize by:
- Updating products via API
- Adding new categories via API
- Modifying initial data in `init_db()` function in `app.py`

## Customization

### Change Tax Rate

In `app.py`, update the tax calculation in `create_sale()`:

```python
tax = subtotal * 0.10  # Change 0.10 to desired rate
```

### Add New Product Categories

Add icons in `getCategoryIcon()` in `main.js`:

```javascript
icons['YourCategory'] = 'icon-name';  // FontAwesome icon name
```

Then add category through API:

```bash
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"YourCategory"}'
```

### Add Custom Branding

Modify `static/css/style.css` variables:

```css
:root {
    --primary: #your-color;
    --accent: #your-accent-color;
}
```

## Troubleshooting

### MongoDB Connection Failed

- Ensure MongoDB is running: `sudo systemctl status mongod` (Linux/Mac) or check Services (Windows)
- Verify URI: default is `mongodb://localhost:27017/`
- Check using `mongo` shell

```bash
# Test connection
mongo
> show dbs
```

### Port Already in Use

Change port in `app.py`:

```python
app.run(debug=True, port=5001)  # Change 5000 to another
```

### Static Files Not Loading

Check paths in templates:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

### Products Not Showing

1. Check MongoDB: `db.products.find()` in mongo shell
2. Restart Flask: Ctrl+C then re-run
3. Check console for errors

## Production Deployment

For production use:

1. Disable debug mode: `app.run(debug=False)`
2. Use a WSGI server (Gunicorn/uWSGI):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
3. Use nginx as reverse proxy
4. Set proper SECRET_KEY in .env
5. Enable MongoDB authentication

## License

This project is provided as-is for personal/small business use.

## Support

For issues or questions, refer to the project documentation or open an issue.
