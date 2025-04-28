from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Product, InventoryFillup, Sale
from datetime import datetime
from sqlalchemy import desc, func
import logging

@app.route('/')
def index():
    """Homepage - displays summary of inventory and recent sales"""
    # Get total products count
    total_products = Product.query.count()
    
    # Get products with low inventory (less than 5 items)
    low_inventory = Product.query.filter(Product.quantity < 5).count()
    
    # Get total sales count
    total_sales = Sale.query.count()
    
    # Get recent sales
    recent_sales = Sale.query.order_by(desc(Sale.created_at)).limit(5).all()
    
    return render_template('index.html', 
                          total_products=total_products,
                          low_inventory=low_inventory,
                          total_sales=total_sales,
                          recent_sales=recent_sales)

# Inventory management routes
@app.route('/inventory')
def inventory():
    """Display all inventory items"""
    search_query = request.args.get('search', '')
    
    if search_query:
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        products = Product.query.all()
        
    return render_template('inventory.html', products=products, search_query=search_query)

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_product():
    """Add a new product to inventory"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        quantity = int(request.form.get('quantity', 0))
        price = float(request.form.get('price', 0))
        
        # Validate inputs
        if not name or price <= 0:
            flash('Product name and a positive price are required', 'danger')
            return redirect(url_for('add_product'))
        
        # Create new product
        product = Product(
            name=name,
            description=description,
            quantity=quantity,
            price=price
        )
        
        db.session.add(product)
        
        # If initial quantity is added, create inventory fillup record
        if quantity > 0:
            fillup = InventoryFillup(
                product=product,
                quantity_added=quantity,
                notes=f"Initial inventory for {name}"
            )
            db.session.add(fillup)
            
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('inventory'))
        
    return render_template('add_product.html')

@app.route('/inventory/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit an existing product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        
        # Handle quantity changes separately to track them
        new_quantity = int(request.form.get('quantity', 0))
        quantity_change = new_quantity - product.quantity
        
        if quantity_change != 0:
            product.quantity = new_quantity
            
            # If quantity increased, create inventory fillup record
            if quantity_change > 0:
                fillup = InventoryFillup(
                    product=product,
                    quantity_added=quantity_change,
                    notes=f"Manual adjustment from {product.quantity} to {new_quantity}"
                )
                db.session.add(fillup)
                
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('inventory'))
        
    return render_template('edit_product.html', product=product)

@app.route('/inventory/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get_or_404(product_id)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully', 'success')
    return redirect(url_for('inventory'))

@app.route('/inventory/fillup/<int:product_id>', methods=['POST'])
def fillup_inventory(product_id):
    """Add items to inventory"""
    product = Product.query.get_or_404(product_id)
    
    quantity_added = int(request.form.get('quantity_added', 0))
    notes = request.form.get('notes', '')
    
    if quantity_added <= 0:
        flash('Please enter a positive quantity to add', 'danger')
        return redirect(url_for('edit_product', product_id=product_id))
    
    # Create inventory fillup record
    fillup = InventoryFillup(
        product=product,
        quantity_added=quantity_added,
        notes=notes
    )
    
    # Update product quantity
    product.quantity += quantity_added
    
    db.session.add(fillup)
    db.session.commit()
    
    flash(f'Added {quantity_added} units to inventory', 'success')
    return redirect(url_for('inventory'))

@app.route('/inventory/history')
def inventory_history():
    """Display inventory fillup history"""
    fillups = InventoryFillup.query.order_by(desc(InventoryFillup.created_at)).all()
    return render_template('inventory_history.html', fillups=fillups)

# Sales routes
@app.route('/sales')
def sales():
    """Display sales options and search for products to sell"""
    search_query = request.args.get('search', '')
    
    if search_query:
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        products = Product.query.filter(Product.quantity > 0).all()
        
    return render_template('sales.html', products=products, search_query=search_query)

@app.route('/sales/sell/<int:product_id>', methods=['GET', 'POST'])
def sell_product(product_id):
    """Sell a product - reduce inventory and record sale"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        quantity_sold = int(request.form.get('quantity_sold', 0))
        sale_price = float(request.form.get('sale_price', product.price))
        customer_name = request.form.get('customer_name', '')
        notes = request.form.get('notes', '')
        
        # Validate inputs
        if quantity_sold <= 0:
            flash('Please enter a positive quantity to sell', 'danger')
            return redirect(url_for('sell_product', product_id=product_id))
            
        if quantity_sold > product.quantity:
            flash(f'Cannot sell {quantity_sold} units. Only {product.quantity} available in inventory.', 'danger')
            return redirect(url_for('sell_product', product_id=product_id))
        
        # Create sale record
        sale = Sale(
            product=product,
            quantity_sold=quantity_sold,
            sale_price=sale_price,
            customer_name=customer_name,
            notes=notes
        )
        
        # Update product quantity
        product.quantity -= quantity_sold
        
        db.session.add(sale)
        db.session.commit()
        
        flash(f'Sale recorded successfully. {quantity_sold} units sold.', 'success')
        return redirect(url_for('sales'))
        
    return render_template('sell_product.html', product=product)

@app.route('/sales/history')
def sales_history():
    """Display sales history"""
    sales = Sale.query.order_by(desc(Sale.created_at)).all()
    return render_template('sales_history.html', sales=sales)

# API endpoints for searches
@app.route('/api/products/search')
def search_products():
    """API endpoint for product search (used for AJAX calls)"""
    search_query = request.args.get('q', '')
    
    if not search_query:
        return jsonify([])
    
    products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    
    result = [{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity,
        'price': p.price
    } for p in products]
    
    return jsonify(result)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
