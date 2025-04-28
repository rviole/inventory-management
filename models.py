from app import db
from datetime import datetime

class Product(db.Model):
    """Model for inventory products"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product {self.name}>"

class InventoryFillup(db.Model):
    """Model for tracking inventory additions"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_added = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship with Product
    product = db.relationship('Product', backref=db.backref('fillups', lazy=True))
    
    def __repr__(self):
        return f"<InventoryFillup {self.id} - Product {self.product_id}>"

class Sale(db.Model):
    """Model for sales transactions"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship with Product
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))
    
    def __repr__(self):
        return f"<Sale {self.id} - Product {self.product_id}>"
