from flask_wtf import Form
from wtforms import TextField, TextAreaField, FileField, SelectField, SubmitField, SelectMultipleField, DecimalField, BooleanField
from wtforms.validators import Required

from markupsafe import Markup

class TestForm(Form):
    name        = TextField()
    last        = TextField()
    submit      = SubmitField()


class CommentForm(Form):
    body        = TextAreaField('Comment')
    happy       = BooleanField()


class FileUploadForm(Form):
    up_file     = FileField(u'Upload a File')
    submit      = SubmitField(u'Save Photo')


def multi_checkboxes(field, ul_class=u'', **kwargs):
    html = []
    html.append(Markup('<ul>'))
    for value, label, checked in field.iter_choices():
        html.append(Markup('<li>'))

        if checked:
            html.append(Markup('<input id="{}-{}" type="checkbox" name="{}" \
                    value="{}" checked="checked">{}</input>'.format(
                        field.id,
                        value,
                        field.name,
                        value,
                        label)))
        else:
            html.append(Markup('<input id="{}-{}" type="checkbox" name="{}" \
                    value="{}">{}</input>'.format(
                        field.id,
                        value,
                        field.name,
                        value,
                        label)))

        html.append(Markup('</li>'))
    html.append(Markup('</ul>'))
    return Markup('\n').join(html)

class ConsumerDashForm(Form):
    first_name      = TextField('First Name', [Required()])
    last_name       = TextField('Last Name', [Required()])
    email           = TextField('Email', [Required()])
    birth_day       = TextField('Birthday')
    submit          = SubmitField('Save Changes')


payment_methods = [
        ('cash', 'Cash'),
        ('discover', 'Discover'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'Amex'),
        ('paypal', 'Paypal')
        ]


times = [('closed', 'Closed'),
        ('5:00am', '5:00am'), ('5:15am', '5:15am'), ('5:30am', '5:30am'),
        ('5:45am', '5:45am'), ('6:00am', '6:00am'), ('6:15am', '6:15am'),
        ('6:30am', '6:30am'), ('6:45am', '6:45am'), ('7:00am', '7:00am'),
        ('7:15am', '7:15am'), ('7:30am', '7:30am'), ('7:45am', '7:45am'),
        ('8:00am', '8:00am'), ('8:15am', '8:15am'), ('8:30am', '8:30am'),
        ('8:45am', '8:45am'), ('9:00am', '9:00am'), ('9:15am', '9:15am'),
        ('9:30am', '9:30am'), ('9:45am', '9:45am'), ('10:00am', '10:00am'),
        ('10:15am', '10:15am'), ('10:30am', '10:30am'), ('10:45am', '10:45am'),
        ('11:00am', '11:00am'), ('11:15am', '11:15am'), ('11:30am', '11:30am'),
        ('11:45am', '11:45am'), ('12:00pm', '12:00pm'), ('12:15pm', '12:15pm'),
        ('12:30pm', '12:30pm'), ('12:45pm', '12:45pm'), ('1:00pm', '1:00pm'),
        ('1:15pm', '1:15pm'), ('1:30pm', '1:30pm'), ('1:45pm', '1:45pm'),
        ('2:00pm', '2:00pm'), ('2:15pm', '2:15pm'), ('2:30pm', '2:30pm'),
        ('2:45pm', '2:45pm'), ('3:00pm', '3:00pm'), ('3:15pm', '3:15pm'),
        ('3:30pm', '3:30pm'), ('3:45pm', '3:45pm'), ('4:00pm', '4:00pm'),
        ('4:15pm', '4:15pm'), ('4:30pm', '4:30pm'), ('4:45pm', '4:45pm'),
        ('5:00pm', '5:00pm'), ('5:15pm', '5:15pm'), ('5:30pm', '5:30pm'),
        ('5:45pm', '5:45pm'), ('6:00pm', '6:00pm'), ('6:15pm', '6:15pm'),
        ('6:30pm', '6:30pm'), ('6:45pm', '6:45pm'), ('7:00pm', '7:00pm'),
        ('7:15pm', '7:15pm'), ('7:30pm', '7:30pm'), ('7:45pm', '7:45pm'),
        ('8:00pm', '8:00pm'), ('8:15pm', '8:15pm'), ('8:30pm', '8:30pm'),
        ('8:45pm', '8:45pm'), ('9:00pm', '9:00pm'), ('9:15pm', '9:15pm'),
        ('9:30pm', '9:30pm'), ('9:45pm', '9:45pm'), ('10:00pm', '10:00pm'),
        ('10:15pm', '10:15pm'), ('10:30pm', '10:30pm'), ('10:45pm', '10:45pm'),
        ('11:00pm', '11:00pm'), ('11:15pm', '11:15pm'), ('11:30pm', '11:30pm'),
        ('11:45pm', '11:45pm'), ('12:00am', '12:00am')]


menu_types = [
        ('barber', 'Barber'),
        ('salon', 'Salon'),
        ('product', 'Product')
        ]

class MenuItemForm(Form):
    name            = TextField(u'Name')
    price           = DecimalField(u'Price', places=2, rounding=None)
    description     = TextAreaField('Description')
    menu_type       = SelectField(u'Menu Type', choices=menu_types)
    submit          = SubmitField('Save Item')


class AddressForm(Form):
    street_1        = TextField('Street')
    street_2        = TextField('Street 2')
    apartment       = TextField('Number')
    city            = TextField('City', [Required('Please enter your city')])
    state           = TextField('State', [Required('Please provide your state')])
    zip_code        = TextField('Zip', [Required('Please tell us your zip code')])

    submit          = SubmitField('Save Changes')


class HoursForm(Form):
    monday_open     = SelectField(u'Monday open', choices=times)
    monday_close    = SelectField(u'Monday close', choices=times)
    tuesday_open    = SelectField(u'Tuesday open',choices=times)
    tuesday_close   = SelectField(u'Tuesday close',choices=times)
    wednesday_open  = SelectField(u'Wednesday open', choices=times)
    wednesday_close = SelectField(u'Wednesday close', choices=times)
    thursday_open   = SelectField(u'Thursday open', choices=times)
    thursday_close  = SelectField(u'Thursday close', choices=times)
    friday_open     = SelectField(u'Friday open', choices=times)
    friday_close    = SelectField(u'Friday close', choices=times)
    saturday_open   = SelectField(u'Saturday open', choices=times)
    saturday_close  = SelectField(u'Saturday close', choices=times)
    sunday_open     = SelectField(u'Sunday open', choices=times)
    sunday_close    = SelectField(u'Sunday close', choices=times)

    submit          = SubmitField('Save Changes')


class ProviderDashForm(Form):
    avatar          = TextField('Avatar')
    business_name   = TextField('Business Name')
    external_site   = TextField('External Site')
    phone           = TextField('Phone Number')
    email           = TextField('Business Email')

    payment_methods     = SelectMultipleField(u'Payment Methods',
                            widget=multi_checkboxes,
                            choices=payment_methods)

    bio             = TextAreaField('About Us')
    fb_url          = TextField('Facebook Page')
    twitter_url     = TextField('Twitter')

    submit          = SubmitField('Save Changes')
