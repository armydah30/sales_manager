from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omoine_com.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

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


if __name__ == '__main__':
    manager.run()
