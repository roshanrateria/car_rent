from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,IntegerField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email

class CarForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Add Car')

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Add Customer')

class ReservationForm(FlaskForm):
    #car_id = IntegerField('Car ID', validators=[DataRequired()])
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Make Reservation')

class PaymentForm(FlaskForm):
    reservation_id = SelectField('Reservation ID', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    submit = SubmitField('Process Payment')
