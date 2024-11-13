from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    car = db.relationship('Car', backref='reservations')
    customer = db.relationship('Customer', backref='reservations')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    reservation = db.relationship('Reservation', backref='payments')

from forms import CarForm, CustomerForm, ReservationForm, PaymentForm
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db.init_app(app)
with app.app_context():
    db.create_all()
# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Route to list all cars
@app.route('/cars')
def list_cars():
    cars = Car.query.all()
    return render_template('list_cars.html', cars=cars)

# Route to add a new car
@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    form = CarForm()
    if form.validate_on_submit():
        car = Car(make=form.make.data, model=form.model.data, year=form.year.data)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('list_cars'))
    return render_template('add_car.html', form=form)


# Route to view car details along with reservations and payments
@app.route('/car/<int:car_id>', methods=['GET', 'POST'])
def car_details(car_id):
    car = Car.query.get_or_404(car_id)
    reservation_form = ReservationForm()
    payment_form = PaymentForm()

    # Populate the customer dropdown with all customers from the database
    reservation_form.customer_id.choices = [(customer.id, customer.name) for customer in Customer.query.all()]

    # Handle Reservation form submission
    if reservation_form.validate_on_submit():
        reservation = Reservation(
            car_id=car.id,
            customer_id=reservation_form.customer_id.data,
            start_date=reservation_form.start_date.data,
            end_date=reservation_form.end_date.data
        )
        print(reservation)
        db.session.add(reservation)
        db.session.commit()
        return redirect(url_for('car_details', car_id=car.id))
    else:
        print("Form not valid. Validation errors:")
        for field, errors in reservation_form.errors.items():
            print(f"{field}: {errors}")
    # Populate the reservation dropdown with all reservations for this car
    payment_form.reservation_id.choices = [(reservation.id, f"Reservation from {reservation.start_date} to {reservation.end_date}") for reservation in Reservation.query.filter_by(car_id=car.id).all()]

    # Handle Payment form submission
    if payment_form.validate_on_submit():
        print(f"Reservation ID: {payment_form.reservation_id.data}")
        print(f"Amount: {payment_form.amount.data}")
        payment = Payment(
            reservation_id=payment_form.reservation_id.data,
            amount=payment_form.amount.data,
            payment_date=datetime.now()
        )
        db.session.add(payment)
        db.session.commit()
        print(f"Payment created: {payment}")
        return redirect(url_for('car_details', car_id=car.id))


    # Fetch car reservations and payments
    reservations = Reservation.query.filter_by(car_id=car.id).all()
    payments = Payment.query.filter(Payment.reservation_id.in_([r.id for r in reservations])).all()

    return render_template('car.html', car=car, reservations=reservations, payments=payments, 
                           reservation_form=reservation_form, payment_form=payment_form)

# Route to update car details
@app.route('/update_car/<int:car_id>', methods=['GET', 'POST'])
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    form = CarForm(obj=car)
    if form.validate_on_submit():
        car.make = form.make.data
        car.model = form.model.data
        car.year = form.year.data
        db.session.commit()
        return redirect(url_for('car_details', car_id=car.id))
    return render_template('update_car.html', form=form, car=car)

# Route to add a new customer


# Route to add a new customer
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data, email=form.email.data, phone=form.phone.data)
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('list_customers'))
    return render_template('add_customer.html', form=form)

# Route to list all customers
@app.route('/customers')
def list_customers():
    customers = Customer.query.all()
    return render_template('list_customers.html', customers=customers)

# Route to view a specific customer
@app.route('/customer/<int:customer_id>')
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    reservations = Reservation.query.filter_by(customer_id=customer.id).all()
    payments = Payment.query.filter(Payment.reservation_id.in_([r.id for r in reservations])).all()
    return render_template('view_customer.html', customer=customer, reservations=reservations, payments=payments)


# Route to list all cars (for easy access to car list)
@app.route('/list_cars')
def list_all_cars():
    cars = Car.query.all()
    return render_template('list_cars.html', cars=cars)


@app.route('/abc')
def test():
    c=Car.query.get_or_404(1)
    print(c)
    print(Reservation.query.filter_by(car_id=1).all())
    
if __name__ == '__main__':
    app.run(debug=True)
