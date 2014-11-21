from flask import current_app
from flask_wtf import Form
from wtforms import TextField, SubmitField, SelectField
from wtforms.validators import Required, ValidationError

menu_types = [
        ('none', 'I\'m looking for:'),
        ('salon', 'Salons'),
        ('barbershop', 'Barbershops'),
        ('product', 'Products')]

zip_message = 'Please enter a zip code so we can find a HairShop for you'

class SearchForm(Form):
    menu_type       = SelectField('Type', choices=menu_types)
    service         = TextField('Service', default="services")
    zip_code        = TextField('Zip', default='zip code')
    submit          = SubmitField('Search')

    def validate_zip_code(form, field):
        if field.data == 'in ZIP code':
            raise ValidationError(zip_message)

    def validate_menu_type(form, field):
        if field.data == 'none':
            raise ValidationError('Please select a HairShop type from the dropdown')

