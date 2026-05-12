// Global state
let products = [];
let categories = [];
let cart = [];
let selectedCategory = null;

// API Base URL (adjust if needed)
const API_BASE = '';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadProducts();
    loadStats();
    updateDateTime();
    setInterval(updateDateTime, 60000);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);

    // Search functionality
    document.getElementById('searchInput').addEventListener('input', debounce(handleSearch, 300));
});

// ---------------------
// Data Loading
// ---------------------

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/api/categories`);
        categories = await response.json();
        renderCategories();
    } catch (error) {
        console.error('Failed to load categories:', error);
        showToast('Failed to load categories', 'error');
    }
}

async function loadProducts(category = null, search = '') {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    if (search) params.set('search', search);

    try {
        const response = await fetch(`${API_BASE}/api/products?${params}`);
        products = await response.json();
        renderProducts();
    } catch (error) {
        console.error('Failed to load products:', error);
        showToast('Failed to load products', 'error');
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats/today`);
        const stats = await response.json();
        document.getElementById('totalProducts').textContent = stats.total_products || 0;
        document.getElementById('lowStock').textContent = stats.low_stock_products || 0;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ---------------------
// Rendering
// ---------------------

function renderCategories() {
    const container = document.getElementById('categoryList');
    container.innerHTML = `
        <div class="category-item ${selectedCategory === null ? 'active' : ''}" onclick="selectCategory(null)">
            <i class="fas fa-th"></i>
            <span>All Products</span>
        </div>
    `;

    categories.forEach(cat => {
        const count = products.filter(p => p.category === cat).length;
        container.innerHTML += `
            <div class="category-item ${selectedCategory === cat ? 'active' : ''}" onclick="selectCategory('${cat}')">
                <i class="fas fa-tag"></i>
                <span>${cat}</span>
                <span class="count">${count}</span>
            </div>
        `;
    });
}

function renderProducts() {
    const container = document.getElementById('productsGrid');
    const filteredProducts = selectedCategory
        ? products.filter(p => p.category === selectedCategory)
        : products;

    if (filteredProducts.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-light);">
                <i class="fas fa-box-open" style="font-size: 48px; margin-bottom: 16px;"></i>
                <p>No products found</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filteredProducts.map(product => {
        const inCart = cart.find(item => item.product_id === product._id);
        const stockClass = product.stock < 10 ? 'low' : '';
        const addedClass = inCart ? 'added' : '';

        return `
            <div class="product-card ${addedClass}"
                 ondblclick="addToCart('${product._id}')"
                 data-id="${product._id}">
                <div class="product-image">
                    <i class="fas fa-${getCategoryIcon(product.category)}"></i>
                </div>
                <div class="product-name" title="${product.name}">${product.name}</div>
                <div class="product-category">${product.category}</div>
                <div class="product-price">$${parseFloat(product.price).toFixed(2)}</div>
                <div class="product-stock ${stockClass}">${product.stock} ${product.unit}</div>
            </div>
        `;
    }).join('');

    renderCategories(); // Update counts
}

function renderCart() {
    const container = document.getElementById('cartItems');

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="cart-empty">
                <i class="fas fa-shopping-cart"></i>
                <p>Your cart is empty</p>
                <small>Double-click products to add them</p>
            </div>
        `;
        updateCartTotals();
        return;
    }

    container.innerHTML = cart.map(item => {
        const product = products.find(p => p._id === item.product_id);
        if (!product) return '';

        return `
            <div class="cart-item" data-id="${item.product_id}">
                <div class="cart-item-image">
                    <i class="fas fa-${getCategoryIcon(product.category)}"></i>
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-name">${product.name}</div>
                    <div class="cart-item-price">$${parseFloat(product.price).toFixed(2)} / ${product.unit}</div>
                    <div class="cart-item-controls">
                        <button class="qty-btn" onclick="updateQuantity('${item.product_id}', -1)">-</button>
                        <span class="qty-display">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity('${item.product_id}', 1)">+</button>
                    </div>
                </div>
                <div class="cart-item-subtotal">
                    $${(product.price * item.quantity).toFixed(2)}
                </div>
                <div class="cart-item-remove" onclick="removeFromCart('${item.product_id}')">
                    <i class="fas fa-times"></i>
                </div>
            </div>
        `;
    }).join('');

    updateCartTotals();
}

function updateCartTotals() {
    const subtotal = cart.reduce((sum, item) => {
        const product = products.find(p => p._id === item.product_id);
        return sum + (product ? product.price * item.quantity : 0);
    }, 0);

    const tax = subtotal * 0.10;
    const total = subtotal + tax;

    document.getElementById('cartSubtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('cartTax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('cartTotal').textContent = `$${total.toFixed(2)}`;
}

// ---------------------
// Cart Actions
// ---------------------

function addToCart(productId) {
    const product = products.find(p => p._id === productId);
    if (!product) return;

    if (product.stock === 0) {
        showToast('Product out of stock!', 'error');
        return;
    }

    const existingItem = cart.find(item => item.product_id === productId);

    if (existingItem) {
        if (existingItem.quantity >= product.stock) {
            showToast('Maximum stock reached!', 'error');
            return;
        }
        existingItem.quantity += 1;
    } else {
        cart.push({ product_id: productId, quantity: 1 });
    }

    // Visual feedback
    const card = document.querySelector(`.product-card[data-id="${productId}"]`);
    if (card) {
        card.classList.add('added');
        setTimeout(() => card.classList.remove('added'), 500);
    }

    renderCart();
    renderProducts(); // Update counts
}

function updateQuantity(productId, delta) {
    const item = cart.find(i => i.product_id === productId);
    const product = products.find(p => p._id === productId);

    if (!item || !product) return;

    const newQty = item.quantity + delta;

    if (newQty <= 0) {
        removeFromCart(productId);
    } else if (newQty > product.stock) {
        showToast('Cannot exceed available stock', 'error');
    } else {
        item.quantity = newQty;
        renderCart();
        renderProducts();
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.product_id !== productId);
    renderCart();
    renderProducts();
}

function clearCart() {
    if (cart.length === 0) return;
    if (confirm('Clear all items from cart?')) {
        cart = [];
        renderCart();
        renderProducts();
    }
}

function holdOrder() {
    if (cart.length === 0) return;
    localStorage.setItem('heldOrder', JSON.stringify(cart));
    showToast('Order held', 'success');
    cart = [];
    renderCart();
    renderProducts();
}

function recallOrder() {
    const held = localStorage.getItem('heldOrder');
    if (held) {
        cart = JSON.parse(held);
        localStorage.removeItem('heldOrder');
        renderCart();
        renderProducts();
        showToast('Order recalled', 'success');
    } else {
        showToast('No held order found', 'error');
    }
}

// ---------------------
// Category & Search
// ---------------------

function selectCategory(category) {
    selectedCategory = category;
    document.getElementById('categoryTitle').textContent = category || 'All Products';
    const search = document.getElementById('searchInput').value;
    loadProducts(category, search);
}

function handleSearch(e) {
    const search = e.target.value;
    loadProducts(selectedCategory, search);
}

// ---------------------
// Checkout
// ---------------------

function openCheckoutModal() {
    if (cart.length === 0) {
        showToast('Cart is empty!', 'error');
        return;
    }

    // Populate checkout summary
    const checkoutItems = document.getElementById('checkoutItems');
    const subtotal = cart.reduce((sum, item) => {
        const product = products.find(p => p._id === item.product_id);
        return sum + (product ? product.price * item.quantity : 0);
    }, 0);
    const tax = subtotal * 0.10;
    const total = subtotal + tax;

    checkoutItems.innerHTML = cart.map(item => {
        const product = products.find(p => p._id === item.product_id);
        if (!product) return '';
        return `
            <div class="checkout-item">
                <span>${product.name} x ${item.quantity}</span>
                <span>$${(product.price * item.quantity).toFixed(2)}</span>
            </div>
        `;
    }).join('');

    document.getElementById('checkoutTotal').textContent = `$${total.toFixed(2)}`;
    document.getElementById('amountReceived').value = total.toFixed(2);
    document.getElementById('changeAmount').textContent = '$0.00';
    document.getElementById('customerName').value = '';

    document.getElementById('checkoutModal').classList.add('active');
    updateChangeDisplay();
}

function closeCheckoutModal() {
    document.getElementById('checkoutModal').classList.remove('active');
}

function updateChangeDisplay() {
    const amountReceived = parseFloat(document.getElementById('amountReceived').value) || 0;
    const subtotal = cart.reduce((sum, item) => {
        const product = products.find(p => p._id === item.product_id);
        return sum + (product ? product.price * item.quantity : 0);
    }, 0);
    const total = subtotal * 1.10;

    const change = amountReceived - total;
    document.getElementById('changeAmount').textContent = change >= 0 ? `$${change.toFixed(2)}` : 'Insufficient';
}

function setExactAmount() {
    const subtotal = cart.reduce((sum, item) => {
        const product = products.find(p => p._id === item.product_id);
        return sum + (product ? product.price * item.quantity : 0);
    }, 0);
    const total = subtotal * 1.10;
    document.getElementById('amountReceived').value = total.toFixed(2);
    updateChangeDisplay();
}

async function completeSale() {
    const paymentMethod = document.querySelector('input[name="payment"]:checked').value;
    const customerName = document.getElementById('customerName').value;
    const amountReceived = parseFloat(document.getElementById('amountReceived').value) || 0;

    const subtotal = cart.reduce((sum, item) => {
        const product = products.find(p => p._id === item.product_id);
        return sum + (product ? product.price * item.quantity : 0);
    }, 0);
    const total = subtotal * 1.10;

    if (amountReceived < total) {
        showToast('Amount received is insufficient!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/sales`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                items: cart.map(item => ({ product_id: item.product_id, quantity: item.quantity })),
                payment_method: paymentMethod,
                customer_name: customerName
            })
        });

        if (!response.ok) {
            throw new Error('Sale failed');
        }

        const result = await response.json();

        closeCheckoutModal();
        showReceipt(result);
        cart = [];
        renderCart();
        renderProducts();
        loadStats();

    } catch (error) {
        console.error('Sale error:', error);
        showToast('Failed to complete sale', 'error');
    }
}

// ---------------------
// Receipt
// ---------------------

function showReceipt(result) {
    const receiptContent = document.getElementById('receiptContent');
    const change = parseFloat(document.getElementById('amountReceived').value) - result.sale.total;

    receiptContent.innerHTML = `
        <div class="receipt-header">
            <h2>SUPERMARKET POS</h2>
            <p>123 Main Street, City</p>
            <p>Tel: +1-234-567-8900</p>
        </div>
        <div class="receipt-info">
            <div><strong>Receipt #:</strong> ${result.receipt_number}</div>
            <div><strong>Date:</strong> ${new Date().toLocaleString()}</div>
            <div><strong>Payment:</strong> ${result.sale.payment_method.toUpperCase()}</div>
            ${result.sale.customer_name ? `<div><strong>Customer:</strong> ${result.sale.customer_name}</div>` : ''}
        </div>
        <div class="receipt-items">
            ${result.sale.items.map(item => `
                <div class="receipt-item">
                    <span>${item.product_name} x ${item.quantity}</span>
                    <span>$${item.subtotal.toFixed(2)}</span>
                </div>
            `).join('')}
        </div>
        <div class="receipt-totals">
            <div class="checkout-item"><span>Subtotal:</span><span>$${(result.sale.total / 1.1).toFixed(2)}</span></div>
            <div class="checkout-item"><span>Tax (10%):</span><span>$${(result.sale.total * 0.1).toFixed(2)}</span></div>
            <div class="receipt-total"><span>TOTAL:</span><span>$${result.sale.total.toFixed(2)}</span></div>
            <div class="receipt-item"><span>Amount Received:</span><span>$${document.getElementById('amountReceived').value}</span></div>
            <div class="receipt-item"><span>Change:</span><span>$${change.toFixed(2)}</span></div>
        </div>
        <div class="receipt-footer">
            <p>Thank you for your purchase!</p>
            <p>Please come again.</p>
        </div>
    `;

    // Store for printing
    document.getElementById('printableReceipt').innerHTML = receiptContent.innerHTML;

    document.getElementById('receiptModal').classList.add('active');
}

function closeReceiptModal() {
    document.getElementById('receiptModal').classList.remove('active');
}

function printReceipt() {
    const printContent = document.getElementById('printableReceipt').innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Receipt Print</title>
            <style>
                body { font-family: 'Courier New', monospace; font-size: 12px; max-width: 320px; margin: 0 auto; padding: 20px; }
                .receipt-header { text-align: center; border-bottom: 1px dashed #000; padding-bottom: 10px; margin-bottom: 10px; }
                .receipt-info, .receipt-items, .receipt-totals { margin-bottom: 10px; }
                .checkout-item { display: flex; justify-content: space-between; }
                .receipt-item { border-bottom: 1px dotted #ccc; margin-bottom: 4px; }
                .receipt-total { font-weight: bold; font-size: 14px; border-top: 2px solid #000; padding-top: 5px; }
                .receipt-footer { text-align: center; margin-top: 15px; border-top: 1px dashed #000; padding-top: 10px; }
                @media print { body { margin: 0; } }
            </style>
        </head>
        <body>${printContent}</body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 250);
}

// ---------------------
// Dashboard
// ---------------------

function showDashboard() {
    window.location.href = '/dashboard';
}

// ---------------------
// Utilities
// ---------------------

function getCategoryIcon(category) {
    const icons = {
        'Fruits': 'apple-alt',
        'Dairy': 'cheese',
        'Bakery': 'bread-slice',
        'Grains': 'wheat-awn',
        'Meat': 'drumstick-bite',
        'Beverages': 'wine-bottle',
        'Vegetables': 'carrot',
        'Snacks': 'cookie'
    };
    return icons[category] || 'box';
}

function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.querySelector('.date-time').textContent = now.toLocaleDateString('en-US', options);
}

function handleKeyboard(e) {
    // ESC to close modals
    if (e.key === 'Escape') {
        closeCheckoutModal();
        closeReceiptModal();
    }
    // F12 for dashboard
    if (e.key === 'F12') {
        showDashboard();
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showToast(message, type = 'success') {
    // Remove existing toast
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type} show`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Load initial time format
document.addEventListener('DOMContentLoaded', () => {
    const now = new Date();
    const options = {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.querySelector('.date-time').textContent = now.toLocaleDateString('en-US', options);
});
