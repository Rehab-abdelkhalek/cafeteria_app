from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'  # لتأمين النماذج
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:013555@localhost/cafeteria_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# نموذج المستخدم
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

# نموذج المنتج
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=True)

# نموذج الطلب
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    user = db.relationship('User', backref='orders')

# نموذج عنصر الطلب
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product')

# نموذج التسجيل
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

# نموذج تسجيل الدخول
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# نموذج المنتج
class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category', choices=[('Food', 'Food'), ('Drink', 'Drink')], validators=[DataRequired()])
    submit = SubmitField('Add Product')

# نموذج الطلب
class OrderForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Order')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# إنشاء قاعدة البيانات وإضافة منتجات افتراضية
with app.app_context():
    db.create_all()
    
    # التحقق إذا كان فيه منتجات، لو مفيش نضيف افتراضيين
    if Product.query.count() == 0:
        products_data = [
            Product(name='American Breakfast', price=150, category='Food', image='https://images.unsplash.com/photo-1528137878665-60b3f4f5ce4b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Crispy Chicken', price=100, category='Food', image='https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='French Fries', price=50, category='Food', image='https://images.unsplash.com/photo-1532136647-8ec7e5d8d5d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Kung Pao Chicken', price=120, category='Food', image='https://images.unsplash.com/photo-1603360946369-dc9bb6258143?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Smoky Snack', price=80, category='Food', image='https://images.unsplash.com/photo-1555939594-58056f625634?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Bhutanese Veg', price=90, category='Food', image='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Chicken Nuggets', price=70, category='Food', image='https://images.unsplash.com/photo-1571091718767-18b5b1457add?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Chalupas', price=110, category='Food', image='https://images.unsplash.com/photo-1579586141497-7f2568aa3e0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='French Fries Supreme', price=60, category='Food', image='https://images.unsplash.com/photo-1532136647-8ec7e5d8d5d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Chalupa Supreme', price=130, category='Food', image='https://images.unsplash.com/photo-1571091718767-18b5b1457add?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Wisconsin Cheese', price=95, category='Food', image='https://images.unsplash.com/photo-1542994980-2e8fc9a1c5b9?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Sandwich', price=75, category='Food', image='https://images.unsplash.com/photo-1559056199-641a0ac8b55a?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Baconator', price=140, category='Food', image='https://images.unsplash.com/photo-1579586141497-7f2568aa3e0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Pepperoni Pizza', price=150, category='Food', image='https://images.unsplash.com/photo-1513104890138-7c749659a591?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Hot Coffee', price=30, category='Drink', image='https://images.unsplash.com/photo-1494314671902-399b181aab93?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Iced Tea', price=25, category='Drink', image='https://images.unsplash.com/photo-1512568400610-3f3f73bfed6b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Green Tea', price=20, category='Drink', image='https://images.unsplash.com/photo-1576092768241-dec231879fc3?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Product(name='Espresso', price=40, category='Drink', image='https://images.unsplash.com/photo-1494314671902-399b181aab93?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')
        ]
        for product in products_data:
            db.session.add(product)
        db.session.commit()
        flash('Default products added!')

# الصفحة الرئيسية
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

# تسجيل الخروج
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# لوحة التحكم
@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', orders=orders)

# إضافة منتج (للأدمن)
@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(name=form.name.data, price=form.price.data, category=form.category.data)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('index'))
    return render_template('add_product.html', form=form)

# عرض الطلبات (للأدمن)
@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

# تحديث حالة الطلب
@app.route('/admin/update_order/<int:order_id>', methods=['POST'])
@login_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Completed'
    db.session.commit()
    flash('Order updated!')
    return redirect(url_for('admin_orders'))

# تقديم طلب
@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()
    form.product_id.choices = [(p.id, p.name) for p in Product.query.all()]
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        total_price = product.price * form.quantity.data
        new_order = Order(user_id=current_user.id, total_price=total_price)
        db.session.add(new_order)
        db.session.commit()
        order_item = OrderItem(order_id=new_order.id, product_id=product.id, quantity=form.quantity.data)
        db.session.add(order_item)
        db.session.commit()
        flash('Order placed successfully!')
        return redirect(url_for('dashboard'))
    return render_template('order.html', form=form)

# البحث عن المنتجات
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query') if request.method == 'POST' else ''
    category = request.form.get('category') if request.method == 'POST' else ''
    products = Product.query
    if query:
        products = products.filter(Product.name.ilike(f'%{query}%'))
    if category:
        products = products.filter_by(category=category)
    products = products.all()
    categories = ['Food', 'Drink']
    return render_template('search.html', products=products, query=query, category=category, categories=categories)

if __name__ == '__main__':
    app.run(debug=True)