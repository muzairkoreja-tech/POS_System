import os

base = r"C:\Users\hp\Pictures\VSCode-win32-x64-1.119.0\My WEB Projects\pos_system\templates"

procurement = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Procurement Dashboard - POS System</title>
<link rel="stylesheet" href="../static/css/style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f5f6fa;min-height:100vh;overflow-y:auto}
.dashboard-nav{background:linear-gradient(135deg,#2c3e50,#34495e);color:#fff;padding:0 24px;display:flex;justify-content:space-between;align-items:center;height:60px;box-shadow:0 2px 8px rgba(0,0,0,.2);position:sticky;top:0;z-index:100}
.nav-brand{display:flex;align-items:center;gap:12px;font-size:18px;font-weight:600}
.nav-brand i{font-size:24px;color:#27ae60}
.nav-right{display:flex;align-items:center;gap:20px}
.nav-user{display:flex;align-items:center;gap:8px;font-size:14px}
.nav-user i{font-size:20px}
.nav-user .role-badge{background:rgba(255,255,255,.2);padding:4px 10px;border-radius:12px;font-size:11px;text-transform:uppercase}
.btn-logout{background:rgba(231,76,60,.8);color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px;transition:background .3s}
.btn-logout:hover{background:#e74c3c}
.dashboard-container{max-width:1200px;margin:0 auto;padding:24px}
.page-title{font-size:24px;font-weight:700;color:#2c3e50;margin-bottom:8px}
.page-subtitle{color:#7f8c8d;font-size:14px;margin-bottom:24px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:20px;margin-bottom:32px}
.kpi-card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center;cursor:pointer;transition:all .3s;border-left:4px solid #3498db;text-decoration:none;color:inherit;display:block}
.kpi-card:hover{transform:translateY(-3px);box-shadow:0 6px 20px rgba(0,0,0,.12)}
.kpi-card:nth-child(1){border-left-color:#3498db}
.kpi-card:nth-child(2){border-left-color:#9b59b6}
.kpi-card:nth-child(3){border-left-color:#27ae60}
.kpi-card:nth-child(4){border-left-color:#e67e22}
.kpi-card:nth-child(5){border-left-color:#e74c3c}
.kpi-card:nth-child(6){border-left-color:#1abc9c}
.kpi-icon{font-size:32px;margin-bottom:8px;color:#fff}
.kpi-card h3{font-size:24px;color:#2c3e50;margin-bottom:2px}
.kpi-card p{color:#7f8c8d;font-size:12px;text-transform:uppercase;letter-spacing:1px}
.section-panel{background:#fff;border-radius:10px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:24px;display:none}
.section-panel.active{display:block}
.section-panel h3{font-size:18px;color:#2c3e50;margin-bottom:16px}
.section-panel h3 i{color:#3498db;margin-right:8px}
table{width:100%;border-collapse:collapse;margin-top:12px}
th{background:#f8f9fa;padding:12px 16px;text-align:left;font-size:12px;color:#7f8c8d;text-transform:uppercase;border-bottom:2px solid #eee}
td{padding:12px 16px;border-bottom:1px solid #eee;font-size:14px}
tr:hover{background:#f8f9fa}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:13px;font-weight:600;color:#555;margin-bottom:6px}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px 12px;border:2px solid #eee;border-radius:6px;font-size:14px;transition:border-color .3s}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{outline:none;border-color:#3498db}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.form-row-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.form-row-4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px}
.btn-action{display:inline-flex;align-items:center;gap:6px;padding:10px 20px;border:none;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;transition:all .3s;margin-right:8px;margin-bottom:8px}
.btn-primary{background:#3498db;color:#fff}
.btn-success{background:#27ae60;color:#fff}
.btn-danger{background:#e74c3c;color:#fff}
.btn-warning{background:#e67e22;color:#fff}
.btn-secondary{background:#ecf0f1;color:#2c3e50}
.btn-action:hover{opacity:.9}
.role-tag{padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;text-transform:uppercase}
.toast{position:fixed;bottom:20px;right:20px;background:#2c3e50;color:#fff;padding:12px 24px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);display:none;animation:slideUp .3s ease;z-index:2000}
.toast.success{background:#27ae60}.toast.error{background:#e74c3c}
.toast.show{display:block}
@keyframes slideUp{from{transform:translateY(30px);opacity:0}to{transform:translateY(0);opacity:1}}
.file-upload{border:2px dashed #ccc;padding:40px;text-align:center;border-radius:8px;margin:16px 0;cursor:pointer;transition:border-color .3s}
.file-upload:hover{border-color:#3498db}
.file-upload input{display:none}
</style>
</head>
<body>
<nav class="dashboard-nav">
<div class="nav-brand"><i class="fas fa-truck-loading"></i><span>POS System - Procurement</span></div>
<div class="nav-right">
<div class="nav-user"><i class="fas fa-user-circle"></i><span id="navUserName">Procurement</span><span class="role-badge" id="navRoleBadge">Procurement</span></div>
<button class="btn-logout" onclick="handleLogout()"><i class="fas fa-sign-out-alt"></i> Logout</button>
</div>
</nav>
<div class="dashboard-container">
<h1 class="page-title"><i class="fas fa-truck-loading"></i> Procurement Dashboard</h1>
<p class="page-subtitle">Manage vendors, stock, products, and procurement operations</p>
<div class="kpi-grid">
<a class="kpi-card" onclick="showSection('vendors')" style="cursor:pointer">
<div class="kpi-icon"><i class="fas fa-building"></i></div><h3 id="kpiVendors">-</h3><p>Vendors</p>
</a>
<a class="kpi-card" onclick="showSection('products')" style="cursor:pointer">
<div class="kpi-icon"><i class="fas fa-boxes"></i></div><h3 id="kpiProducts">-</h3><p>Products</p>
</a>
<a class="kpi-card" onclick="showSection('stock')" style="cursor:pointer">
<div class="kpi-icon"><i class="fas fa-cubes"></i></div><h3 id="kpiLowStock">-</h3><p>Low Stock</p>
</a>
<a class="kpi-card" onclick="showSection('orders')" style="cursor:pointer">
<div class="kpi-icon"><i class="fas fa-file-invoice-dollar"></i></div><h3 id="kpiOrders">-</h3><p>Orders</p>
</a>
<a class="kpi-card" onclick="showSection('reports')" style="cursor:pointer">
<div class="kpi-icon"><i class="fas fa-chart-bar"></i></div><h3>Reports</h3><p>Analytics</p>
</a>
<a class="kpi-card" onclick="showSection('qr')" style="cursor:pointer">
<div class="kpi-icon"><i class="fas fa-qrcode"></i></div><h3>QR Code</h3><p>Generate</p>
</a>
</div>
<div id="sectionContent"></div>
</div>
<div id="toastContainer"></div>

<script>
document.addEventListener("DOMContentLoaded",function(){
document.getElementById("navUserName").textContent=sessionStorage.getItem("full_name")||"Procurement Manager";
document.getElementById("navRoleBadge").textContent=(sessionStorage.getItem("role")||"procurement_manager").replace(/_/g," ");
loadStats();
});

async function loadStats(){
try{
const [prods,vendors,orders,stats]=await Promise.all([
fetch("/api/products").then(r=>r.json()),
fetch("/api/vendors").then(r=>r.json()),
fetch("/api/purchase-orders").then(r=>r.json()),
fetch("/api/stats/today").then(r=>r.json())
]);
document.getElementById("kpiProducts").textContent=prods.length;
document.getElementById("kpiVendors").textContent=vendors.length;
document.getElementById("kpiOrders").textContent=orders.length;
document.getElementById("kpiLowStock").textContent=stats.low_stock_products||0;
}catch(e){console.error(e)}
}

function showSection(n){
const el=document.getElementById("sectionContent");
const m={vendors:rVendors,products:rProducts,stock:rStock,orders:rOrders,reports:rReports,qr:rQR};
if(m[n])m[n](el);
}

function rVendors(el){
el.innerHTML='<div class="section-panel active"><h3><i class="fas fa-building"></i> Vendor Management</h3><div class="action-bar"><button class="btn-action btn-primary" onclick="showVF()">+ Add Vendor</button><button class="btn-action btn-secondary" onclick="loadVs()"><i class="fas fa-sync"></i> Refresh</button></div><div id="vF" style="display:none;margin:16px 0;padding:16px;background:#f8f9fa;border-radius:8px"><h4 style="margin-bottom:12px">Add New Vendor</h4><div class="form-row"><div class="form-group"><label>Vendor Name *</label><input id="vn" placeholder="Enter vendor name"></div><div class="form-group"><label>Contact Person</label><input id="vc" placeholder="Contact person name"></div></div><div class="form-row"><div class="form-group"><label>Phone</label><input id="vp" placeholder="Phone number"></div><div class="form-group"><label>Email</label><input type="email" id="ve" placeholder="Email address"></div></div><div class="form-group"><label>Address</label><input id="va" placeholder="Full address"></div><div class="form-row-3"><div class="form-group"><label>Payment Terms</label><select id="vt"><option value="Net 15">Net 15</option><option value="Net 30">Net 30</option><option value="Net 45">Net 45</option><option value="COD">COD</option></select></div><div class="form-group"><label>Status</label><select id="vs"><option value="active">Active</option><option value="inactive">Inactive</option></select></div><div class="form-group"><label>Credit Limit (PKR)</label><input type="number" id="vcl" placeholder="0"></div></div><button class="btn-action btn-success" onclick="saveV()"><i class="fas fa-save"></i> Save Vendor</button><button class="btn-action btn-secondary" onclick="document.getElementById(\'vF\').style.display=\'none\'">Cancel</button></div><table><thead><tr><th>#</th><th>Name</th><th>Contact</th><th>Phone</th><th>Email</th><th>Status</th><th>Terms</th><th>Actions</th></tr></thead><tbody id="vT"><tr><td colspan="8" style="text-align:center;padding:30px"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr></tbody></table></div>';
loadVs();
}

async function loadVs(){
try{
var v=await fetch("/api/vendors").then(r=>r.json());
var tb=document.getElementById("vT");
if(!v.length){tb.innerHTML='<tr><td colspan="8" style="text-align:center;padding:20px;color:#999">No vendors found</td></tr>';return}
var h="";
v.forEach(function(x,i){
var c=x.status==="active"?"#1e8449":"#b9770e";var bg=x.status==="active"?"#d5f5e3":"#fdebd0";
h+="<tr><td>"+(i+1)+"</td><td><strong>"+x.name+"</strong></td><td>"+(x.contact_person||"-")+"</td><td>"+(x.phone||"-")+"</td><td>"+(x.email||"-")+"</td><td><span class=\'role-tag\' style=\'background:"+bg+";color:"+c+"\'>"+x.status+"</span></td><td>"+(x.payment_terms||"-")+"</td><td><button class=\'btn-action btn-danger\' style=\'padding:4px 8px;font-size:11px\' onclick=\"delV(\'"+x._id+"\')\">Delete</button></td></tr>"
});
tb.innerHTML=h;
}catch(e){console.error(e);tb.innerHTML=\'<tr><td colspan="8" style="text-align:center;padding:20px;color:#e74c3c">Failed to load vendors</td></tr>\';}
}

function showVF(){document.getElementById("vF").style.display="block"}

async function saveV(){
var v={name:document.getElementById("vn").value.trim(),contact_person:document.getElementById("vc").value.trim(),phone:document.getElementById("vp").value.trim(),email:document.getElementById("ve").value.trim(),address:document.getElementById("va").value.trim(),payment_terms:document.getElementById("vt").value,status:document.getElementById("vs").value,credit_limit:parseFloat(document.getElementById("vcl").value)||0};
if(!v.name){showT("Vendor name is required","error");return}
try{
var r=await fetch("/api/vendors",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(v)});
if(r.ok){showT("Vendor saved successfully!","success");document.getElementById("vF").style.display="none";loadVs()}
else{var d=await r.json();showT(d.message||"Error saving vendor","error")}
}catch(e){showT("Failed to save vendor","error")}
}

async function delV(id){
if(!confirm("Are you sure you want to delete this vendor?"))return;
try{
var r=await fetch("/api/vendors/"+id,{method:"DELETE"});var d=await r.json();
if(d.success){showT("Vendor deleted successfully","success");loadVs()}else showT(d.message||"Failed to delete vendor","error")
}catch(e){showT("Failed to delete vendor","error")}
}

function rProducts(el){
el.innerHTML=\'<div class="section-panel active"><h3><i class="fas fa-boxes"></i> Product Management</h3><table><thead><tr><th>#</th><th>Name</th><th>Category</th><th>Supplier</th><th>Price(PKR)</th><th>Stock</th><th>Status</th><th>Expiry</th><th>Batch</th></tr></thead><tbody id="pT"><tr><td colspan="9" style="text-align:center;padding:30px"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr></tbody></table></div>\';
loadPs();
}

async function loadPs(){
try{
var p=await fetch("/api/products").then(r=>r.json());
var tb=document.getElementById("pT");
if(!p.length){tb.innerHTML=\'<tr><td colspan="9" style="text-align:center;padding:20px;color:#999">No products found</td></tr>\';return}
var h="";
p.forEach(function(x){
var sc=x.stock<10?"#fdebd0":"#d5f5e3";var sc2=x.stock<10?"#b9770e":"#1e8449";
h+="<tr><td>"+x._id+"</td><td><strong>"+x.name+"</strong></td><td>"+(x.category||"-")+"</td><td>"+(x.supplier||"-")+"</td><td>PKR "+parseFloat(x.price).toFixed(2)+"</td><td>"+(x.stock||0)+" "+(x.unit||"")+"</td><td><span class=\'role-tag\' style=\'background:"+sc+";color:"+sc2+"\'>"+(x.status||"active")+"</span></td><td>"+(x.expiry_date||"-")+"</td><td>"+(x.batch_no||"-")+"</td></tr>"
});
tb.innerHTML=h;
}catch(e){console.error(e);tb.innerHTML=\'<tr><td colspan="9" style="text-align:center;padding:20px;color:#e74c3c">Failed to load products</td></tr>\';}
}

function rStock(el){
el.innerHTML=\'<div class="section-panel active"><h3><i class="fas fa-cubes"></i> Low Stock Alert</h3><table><thead><tr><th>#</th><th>Product</th><th>Category</th><th>Supplier</th><th>Stock</th><th>Reorder Lvl</th><th>Unit</th><th>Price(PKR)</th></tr></thead><tbody id="sT"><tr><td colspan="8" style="text-align:center;padding:30px"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr></tbody></table></div>\';
loadStk();
}

async function loadStk(){
try{
var p=await fetch("/api/products").then(r=>r.json());
var low=p.filter(function(x){return(x.stock||0)<(x.reorder_level||10)});
var tb=document.getElementById("sT");
if(!low.length){tb.innerHTML=\'<tr><td colspan="8" style="text-align:center;padding:20px;color:#27ae60"><i class="fas fa-check-circle"></i> All well stocked!</td></tr>\';return}
var h="";
low.forEach(function(x){
var bg=x.stock<5?"#fef3e2":"transparent";var c=x.stock<5?"#e74c3c":"#e67e22";
h+="<tr style=\'background:"+bg+"\'><td>"+x._id+"</td><td><strong>"+x.name+"</strong></td><td>"+(x.category||"-")+"</td><td>"+(x.supplier||"-")+"</td><td style=\'color:"+c+";font-weight:700\'>"+(x.stock||0)+"</td><td>"+(x.reorder_level||"-")+"</td><td>"+(x.unit||"-")+"</td><td>PKR "+parseFloat(x.price).toFixed(2)+"</td></tr>"
});
tb.innerHTML=h;
}catch(e){console.error(e)}
}

function rOrders(el){
el.innerHTML=\'<div class="section-panel active"><h3><i class="fas fa-file-invoice-dollar"></i> Purchase Orders</h3><div class="action-bar"><button class="btn-action btn-primary" onclick="showPOForm()">+ New Order</button></div><div id="poForm" style="display:none;margin:16px 0;padding:16px;background:#f8f9fa;border-radius:8px"><h4 style="margin-bottom:12px">Create Purchase Order</h4><div class="form-row"><div class="form-group"><label>Vendor *</label><select id="poVendor"></select></div><div class="form-group"><label>Order Date</label><input type="date" id="poDate"></div></div><div class="form-group"><label>Items (JSON)</label><textarea id="poItems" rows="4" placeholder=\'[{"name":"Product","qty":10,"unit_price":100}]\'></textarea></div><div class="form-row"><div class="form-group"><label>Paid Amount (PKR)</label><input type="number" id="poPaid" value="0"></div><div class="form-group"><label>Payment Status</label><select id="poStatus"><option value="pending">Pending</option><option value="paid">Paid</option><option value="partial">Partial</option></select></div></div><div style="display:flex;gap:8px"><button class="btn-action btn-success" onclick="savePO()"><i class="fas fa-save"></i> Save Order</button><button class="btn-action btn-secondary" onclick="document.getElementById(\'poForm\').style.display=\'none\'">Cancel</button></div></div><table><thead><tr><th>#</th><th>Vendor</th><th>Items</th><th>Total(PKR)</th><th>Paid</th><th>Pending</th><th>Status</th><th>Date</th></tr></thead><tbody id="poT"><tr><td colspan="8" style="text-align:center;padding:30px"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr></tbody></table></div>\';
loadPOs();
loadVendorsForPO();
}

async function loadVendorsForPO(){
try{
var v=await fetch("/api/vendors").then(r=>r.json());
var sel=document.getElementById("poVendor");
if(sel){sel.innerHTML=\'<option value="">Select Vendor</option>\'+v.map(function(x){return\'<option value="\'+x._id+\'">\'+x.name+\'</option>\'}).join("");}
}catch(e){console.error(e)}
}

async function loadPOs(){
try{
var orders=await fetch("/api/purchase-orders").then(r=>r.json());
var tb=document.getElementById("poT");
if(!orders.length){tb.innerHTML=\'<tr><td colspan="8" style="text-align:center;padding:20px;color:#999">No purchase orders</td></tr>\';return}
var h="";
orders.forEach(function(x){
var pending=(x.total_amount||0)-(x.paid_amount||0);
h+="<tr><td>"+x._id+"</td><td>"+(x.vendor_name||"-")+"</td><td>"+(x.items?x.items.length:0)+" items</td><td>PKR "+parseFloat(x.total_amount||0).toFixed(2)+"</td><td>PKR "+parseFloat(x.paid_amount||0).toFixed(2)+"</td><td>PKR "+pending.toFixed(2)+"</td><td><span class=\'role-tag\' style=\'background:"+(x.payment_status==="paid"?"#d5f5e3":"#fdebd0")+";color:"+(x.payment_status==="paid"?"#1e8449":"#b9770e")+"\'>"+(x.payment_status||"pending")+"</span></td><td>"+(x.order_date?new Date(x.order_date).toLocaleDateString():"-")+"</td></tr>"
});
tb.innerHTML=h;
}catch(e){console.error(e);tb.innerHTML=\'<tr><td colspan="8" style="text-align:center;padding:20px;color:#e74c3c">Failed to load orders</td></tr>\';}
}

function showPOForm(){document.getElementById("poForm").style.display="block"}

async function savePO(){
var vendorId=document.getElementById("poVendor").value;
var vendorName=document.getElementById("poVendor").selectedOptions[0]?.text||"";
var itemsStr=document.getElementById("poItems").value;
var paid=parseFloat(document.getElementById("poPaid").value)||0;
var status=document.getElementById("poStatus").value;
var orderDate=document.getElementById("poDate").value;
if(!vendorId){showT("Select a vendor","error");return}
var items;
try{items=JSON.parse(itemsStr)}catch(e){showT("Invalid items JSON format","error");return}
if(!items||!items.length){showT("Add at least one item","error");return}
var order={vendor_id:vendorId,vendor_name:vendorName,items:items,paid_amount:paid,payment_status:status,order_date:orderDate||new Date().toISOString().split("T")[0]};
try{
var r=await fetch("/api/purchase-orders",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(order)});
if(r.ok){showT("Purchase order created!","success");document.getElementById("poForm").style.display="none";loadPOs()}
else{var d=await r.json();showT(d.message||"Error creating order","error")}
}catch(e){showT("Failed to create order","error")}
}

function rQR(el){
el.innerHTML=\'<div class="section-panel active"><h3><i class="fas fa-qrcode"></i> QR Code Generator</h3><p style="color:#7f8c8d;margin-bottom:16px">Generate QR codes for products with discount offers or special pricing.</p><div style="max-width:500px"><div class="form-group"><label>Select Product</label><select id="qrProduct"><option value="">Loading...</option></select></div><div class="form-group"><label>Discount Percentage (%)</label><input type="number" id="qrDiscount" min="0" max="100" value="0" onchange="calcQRPrice()"></div><div class="form-row"><div class="form-group"><label>Original Price (PKR)</label><input type="number" id="qrOrigPrice" readonly></div><div class="form-group"><label>Discounted Price (PKR)</label><input type="number" id="qrDiscPrice" readonly></div></div><div id="qrCodeDisplay" style="text-align:center;margin:20px 0;padding:20px;border:2px dashed #ccc;border-radius:8px;background:#fafafa"><p style="color:#999"><i class="fas fa-qrcode" style="font-size:48px"></i><br>QR Code will appear here</p></div><button class="btn-action btn-primary" onclick="genQR()"><i class="fas fa-qrcode"></i> Generate QR Code</button></div></div>\';
loadQRProducts();
}

async function loadQRProducts(){
try{
var p=await fetch("/api/products").then(r=>r.json());
var sel=document.getElementById("qrProduct");
if(sel){sel.innerHTML=\'<option value="">Select Product</option>\'+p.map(function(x){return\'<option value="\'+x._id+\'" data-price="\'+x.price+\'" data-name="\'+x.name+\'">\'+x.name+\' - PKR \'+parseFloat(x.price).toFixed(2)+\'</option>\'}).join("");}
}catch(e){console.error(e)}
}

function calcQRPrice(){
var sel=document.getElementById("qrProduct");
var opt=sel.options[sel.selectedIndex];
var price=opt?.dataset?.price||0;
var disc=parseFloat(document.getElementById("qrDiscount").value)||0;
var discPrice=price*(1-disc/100);
document.getElementById("qrOrigPrice").value=price;
document.getElementById("qrDiscPrice").value=discPrice.toFixed(2);
}

function genQR(){
var sel=document.getElementById("qrProduct");
var opt=sel.options[sel.selectedIndex];
if(!opt?.value){showT("Select a product","error");return}
var discount=parseFloat(document.getElementById("qrDiscount").value)||0;
var price=opt.dataset.price;
var discPrice=(price*(1-discount/100)).toFixed(2);
var qrData={product_id:opt.value,name:opt.dataset.name,original_price:price,discount_percent:discount,discounted_price:discPrice,qr_code:"QR-"+opt.value+"-"+Date.now()};
var display=document.getElementById("qrCodeDisplay");
display.innerHTML=\'<div style="padding:16px"><p style="font-weight:600;margin-bottom:8px">QR Code: \'+qrData.name+\'</p><div style="font-size:11px;color:#666;margin-bottom:8px">Product ID: \'+qrData.product_id+\' | Discount: \'+qrData.discount_percent+\'% | Price: PKR \'+qrData.discounted_price+\'</div><div style="background:#fff;border:1px solid #ddd;padding:20px;display:inline-block;border-radius:8px;font-family:monospace;font-size:14px;letter-spacing:2px">\'QR-\'+qrData.product_id+\'-\'+qrData.discount_percent+\'%\nPKR \'+qrData.discounted_price+\'</div><p style="margin-top:12px;font-size:12px;color:#999">Scan this code at POS for discounted price</p></div>\';
showT("QR Code generated successfully!","success");
}

function rReports(el){
el.innerHTML=\'<div class="section-panel active"><h3><i class="fas fa-chart-bar"></i> Reports Center</h3><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px"><div style="background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)"><h4 style="margin-bottom:12px"><i class="fas fa-cubes" style="color:#3498db;margin-right:8px"></i>Stock Report</h4><p style="font-size:13px;color:#7f8c8d;margin-bottom:12px">View remaining stock by vendor, product, or date</p><a href="/api/reports/stock-report" target="_blank" class="btn-action btn-primary" style="display:inline-flex"><i class="fas fa-download"></i> Download</a></div><div style="background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)"><h4 style="margin-bottom:12px"><i class="fas fa-calendar-times" style="color:#e67e22;margin-right:8px"></i>Expiry Report</h4><p style="font-size:13px;color:#7f8c8d;margin-bottom:12px">Track products by expiry date</p><a href="/api/reports/expiry-report" target="_blank" class="btn-action btn-warning" style="display:inline-flex"><i class="fas fa-download"></i> Download</a></div><div style="background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)"><h4 style="margin-bottom:12px"><i class="fas fa-tag" style="color:#27ae60;margin-right:8px"></i>Price List (PKR)</h4><p style="font-size:13px;color:#7f8c8d;margin-bottom:12px">Current product prices with cost & selling price</p><a href="/api/reports/price-list" target="_blank" class="btn-action btn-success" style="display:inline-flex"><i class="fas fa-download"></i> Download</a></div><div style="background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)"><h4 style="margin-bottom:12px"><i class="fas fa-tachometer-alt" style="color:#e74c3c;margin-right:8px"></i>Slow Moving Items</h4><p style="font-size:13px;color:#7f8c8d;margin-bottom:12px">Products not selling in the last 30 days</p><a href="/api/reports/slow-moving" target="_blank" class="btn-action btn-danger" style="display:inline-flex"><i class="fas fa-download"></i> Download</a></div><div style="background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)"><h4 style="margin-bottom:12px"><i class="fas fa-file-invoice-dollar" style="color:#9b59b6;margin-right:8px"></i>Vendor Payments</h4><p style="font-size:13px;color:#7f8c8d;margin-bottom:12px">Paid & pending amounts by vendor</p><a href="/api/reports/vendor-payment" target="_blank" class="btn-action" style="display:inline-flex;background:#9b59b6;color:#fff"><i class="fas fa-download"></i> Download</a></div><div style="background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)"><h4 style="margin-bottom:12px"><i class="fas fa-calendar-day" style="color:#1abc9c;margin-right:8px"></i>Daily Products Added</h4><p style="font-size:13px;color:#7f8c8d;margin-bottom:12px">Products registered on a specific date</p><a href="/api/reports/daily-products" target="_blank" class="btn-action" style="display:inline-flex;background:#1abc9c;color:#fff"><i class="fas fa-download"></i> Download</a></div></div></div>\';
}

function showT(m,t){
var ex=document.querySelector(".toast");if(ex)ex.remove();
var e=document.createElement("div");e.className="toast "+t;e.textContent=m;
document.getElementById("toastContainer").appendChild(e);
setTimeout(function(){e.classList.add("show");setTimeout(function(){e.classList.remove("show");setTimeout(function(){e.remove()},300)},3000)},100);
}

function handleLogout(){
    fetch("/api/auth/logout",{
        method:"POST",
        credentials:"same-origin",
        headers:{"Content-Type":"application/json"}
    }).then(function(res){
        sessionStorage.clear();
        window.location.href="/login";
    }).catch(function(){
        sessionStorage.clear();
        window.location.href="/login";
    });
}
</script>
</body>
</html>"""

with open(os.path.join(base, 'procurement_dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(procurement)
print('Procurement dashboard written!')