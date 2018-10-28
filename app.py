from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
import os
from data import Rules
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, IntegerField, PasswordField, SelectField, validators
from flask_bcrypt import Bcrypt
from functools import wraps
import requests
import json
import geocoder
import time
from datetime import datetime, timedelta
import math
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omoine_com.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#add Database Views
class Stock(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)

class Sales(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.Integer, nullable=False)
    sales_amount = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)

class Users(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)


#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unathorized! Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Index
@app.route('/')
def index():

    return render_template('home.html')

#Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    #get all sales
    sales = Sales.query.all()
    #get all stock
    all_stock = Stock.query.all()

    total_stock = 0
    total_sales = 0
    total_revenue = 0
    total_profit = 0
    shoes = 0
    clothes = 0
    phones = 0
    tablets = 0
    others = 0

    for stock in all_stock:
        total_stock += stock.quantity

        print(total_stock)
    for sale in sales:
        total_sales += sale.quantity
        total_revenue += sale.sales_amount
        total_profit += sale.profit
        if sale.category == 'Shoes':
            shoes += 1
        if sale.category == 'Phones':
            phones += 1
        if sale.category == 'Tablets':
            tablets += 1
        if sale.category == 'Clothes':
            clothes += 1
        if sale.category == 'Others':
            others += 1


    context = {
            'sales': sales,
            'total_stock': total_stock,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'total_stock': total_stock,
            'shoes': shoes,
            'clothes': clothes,
            'phones': phones,
            'tablets': tablets,
            'others': others,

            }

    return render_template('dashboard.html', context=context)


#user registration form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

#User registration
@app.route('/add_user', methods=['GET', 'POST'])
@is_logged_in
def add_user():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        #execute commands
        user = Users(name=name, email=email, username=username, password=hashed_password, create_date=datetime.now())
        db.session.add(user)
        db.session.commit()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))

    return render_template('add_user.html', form=form)

#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user.id > 0:
            #compare passwords
            if user and bcrypt.check_password_hash(user.password, password_candidate):
             #Passed
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Wrong Password. Please Try Again'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#Manage user
@app.route('/manage_users')
@is_logged_in
def manage_users():
    #get users
    users = Users.query.all()

    if len(users) > 0:
        return render_template('manage_users.html', users=users)
    else:
        msg = 'No Users Found'
        return render_template('manage_users.html', msg=msg)

#Add Sales
@app.route('/add_sales', methods=['POST', 'GET'])
@is_logged_in
def add_sales():
    #Get Stock
    stocks = Stock.query.all()
    if len(stocks) > 0:
            return render_template('add_sales.html', stocks=stocks)
    else:
        msg = 'You currently have NO stock!'
        return render_template('dashboard.html', msg=msg)

@app.route('/sales/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def sales(id):
        #Get Stock from DB
        stock = Stock.query.filter_by(id=id).one()

        #Collect name and category
        product_name = stock.name
        category = stock.category
        cost_price = int(stock.unit_price)

        #Add new sales form
        class SalesForm(Form):
            quantity = IntegerField('How Much Sold?', [validators.NumberRange(max=stock.quantity)])
            sales_amount = IntegerField('Total Sales Price?', [validators.NumberRange(min=50)])

        #get Sales form
        form = SalesForm(request.form)

        if request.method == 'POST' and form.validate():
            #reduce stock by sales quantity
            quantity_sold = int(request.form['quantity'])
            current_stock = stock.quantity
            stock_balance = current_stock - quantity_sold
            stock.quantity = stock_balance
            stock.total_price = stock.quantity * stock.unit_price

            #add change to DB
            db.session.commit()

            quantity = request.form['quantity']
            sales_amount = request.form['sales_amount']
            profit = int(sales_amount) - (cost_price * quantity_sold)
            #add sales to DB
            sales = Sales(name=product_name, category=category, quantity=quantity, profit=profit, sales_amount=sales_amount, create_date=datetime.now().date())
            db.session.add(sales)
            db.session.commit()

            flash('Sales Added and Stock Updated!', 'success')

            return redirect(url_for('sales_history'))

        return render_template('sales.html', form=form)

#View all sales and add stock
@app.route('/sales_history')
@is_logged_in
def sales_history():
    #get all stock
    sales = Sales.query.all()

    if len(sales) > 0:
        return render_template('sales_history.html', sales=sales)
    else:
        msg = 'You Currently have NO Sales!'
        return render_template('dashboard.html', msg=msg)

#Stock form
class StockForm(Form):
    product_name = TextAreaField('Product Name', [validators.Length(min=1)])
    category = SelectField('Select a Product Category', choices=[(' ', ' '), ('Shoes', 'Shoes'), ('Bags', 'Bags'), ('Clothes', 'Clothes'), ('Phones', 'Phones'), ('Tablets', 'Tablets'), ('Others', 'Others')], validators=[validators.DataRequired()] )
    quantity = IntegerField('How Many?', [validators.NumberRange(min=1)])
    unit_price = IntegerField('What is the Cost Per Product?', [validators.NumberRange(min=50)])

#Add stock
@app.route('/add_stock', methods=['POST', 'GET'])
@is_logged_in
def add_stock():
    form = StockForm(request.form)
    if request.method == 'POST' and form.validate():
        product_name = form.product_name.data
        category = form.category.data
        quantity = form.quantity.data
        unit_price = form.unit_price.data
        total_price = quantity * unit_price

        #add stock to DB
        stock = Stock(name=product_name, category=category, quantity=quantity, unit_price=unit_price, total_price=total_price, create_date=datetime.now())
        db.session.add(stock)
        db.session.commit()

        flash('New Stock Added', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_stock.html', form=form)

#View all stock and add stock
@app.route('/current_stock')
@is_logged_in
def current_stock():
    #get all stock
    stocks = Stock.query.all()

    if len(stocks) > 0:
        return render_template('current_stock.html', stocks=stocks)
    else:
        msg = 'You Currently have NO Stock!'
        return render_template('dashboard.html', msg=msg)

@app.route('/edit_stock/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_stock(id):

        stock = Stock.query.filter_by(id=id).one()

        #get form
        form = StockForm(request.form)

        if request.method == 'POST' and form.validate():
            stock.name = request.form['product_name']
            stock.category = request.form['category']
            stock.quantity = request.form['quantity']
            stock.unit_price = request.form['unit_price']
            stock.total_price = int(request.form['unit_price']) * int(request.form['quantity'])

            db.session.commit()

            flash('Stock Updated', 'success')

            return redirect(url_for('current_stock'))

        return render_template('edit_stock.html', form=form)



#LogOut
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('index'))




if __name__ == '__main__':
    	port = int(os.environ.get('PORT', 5000))
    	app.run(host='0.0.0.0', port=port)
