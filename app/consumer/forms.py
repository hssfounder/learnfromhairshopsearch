from flask_wtf import Form
from wtforms import TextField, SubmitField, SelectMultipleField, SelectField, TextAreaField

from markupsafe import Markup

class HairJourneyForm(Form):
    journey = TextAreaField("What's the story of your hair?")
    submit  = SubmitField("Tell It")

class HairStatusForm(Form):
    status = TextField("Tell us about your hair. What is your current hair status?")
    submit = SubmitField("Update Your Status")

class ConsumerInfoForm(Form):
    first_name      = TextField('First Name')
    last_name       = TextField('Last Name')
    email           = TextField('Email')
    submit          = SubmitField('Save Changes')

hair_condition = [
    ('none', 'No answer'),
    ('exceptionally_curly', 'Exceptionally Curly (4a, 4b, 4c)'),
    ('curly', 'Curly (3a, 3b, 3c)'),
    ('wavy', 'Wavy (2a, 2b, 2c)'),
    ('straight', 'Straight (1a, 1b, 1c)')
]

scalp_condition = [
    ('none', 'No answer'),
    ('oily', 'Oily'),
    ('dry', 'Dry'),
    ('flaky', 'Flaky'),
    ('itchy', 'Itchy'),
    ('normal', 'Normal')
]

trim_last = treat_last = [
    ('none', 'No answer'),
    ('0 - 4 weeks ago', '0 - 4 weeks ago'),
    ('1 - 3 months ago', '1 - 3 months ago'),
    ('3 - 6 months ago', '3 - 6 months ago'),
    ('6 - 12 months ago', '6 - 12 months ago'),
    ('1 year or longer', '1 year or longer')
]

maintenance_freq = [
    ('none', 'No answer'),
    ('Daily', 'Daily'),
    ('Twice a week', 'Twice a week'),
    ('Once a week', 'Once a week'),
    ('Twice a month', 'Twice a month'),
    ('Once a month', 'Once a month'),
    ('Every other month', 'Every other month')
]

genders = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('rather_not', 'Rather Not Say')
]

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

class HairRoutineForm(Form):
    hair_condition      = SelectMultipleField('What is your hair condition?',
                            widget=multi_checkboxes,
                            choices=hair_condition)

    scalp_condition     = SelectMultipleField('What is your scalp condition?',
                            widget=multi_checkboxes,
                            choices=scalp_condition)

    chemical_treat      = SelectField('Do you relax or chemically treat your hair?',
                            choices=[
                                ('none', 'No answer'),
                                ('yes', 'Yes'),
                                ('no', 'No')
                                ])

    last_treatment      = SelectField('When was your last treatment?',
                            choices=treat_last)

    fav_style           = TextField('What is your favorite cut or style?')

    shampoo_type        = TextField('What shampoo do you use?')
    shampoo_frequency   = SelectField('How often do you shampoo your hair?',
                        choices=maintenance_freq)

    conditioner_type    = TextField('What conditioner do you use?')
    condition_frequency = SelectField('How often do you condition your hair?',
                            choices=maintenance_freq)

    last_trim           = SelectField('When was your hair last trimmed?',
                            choices=trim_last)

    submit              = SubmitField('Save Changes')
