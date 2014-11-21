# -*- encoding: utf-8 -*-
from flask import (Blueprint, render_template, current_app, redirect, url_for,
    flash, abort, jsonify, request)
from flask.ext.security import login_required, roles_required, current_user
from flask_mail import Message

from ..search.forms import SearchForm

from ..provider.models import Provider, Comment
from ..consumer.models import Consumer
from ..models import User, Photo

from ..forms import CommentForm
from ..core import db, mail

import datetime

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route('/favorite/<int:provider_id>')
def favorite(provider_id):
    if current_user.consumer:
        consumer = current_user.consumer
        provider = Provider.get(provider_id)
        consumer.favorites.append(provider)
        consumer.save()
        return redirect(url_for('.provider_url', provider_url=provider.business_url))

@frontend.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        if request.form['honeypot']:
            # if we've got a bot on our hands, just redirect to the contact page
            current_app.logger.info('it\'s a trap')
            current_app.logger.info(request.host)
            return redirect(url_for('.contact_us'))

        # otherwise, process the form
        current_app.logger.info(request.form)

        body = "{}\n{}\n{}\n".format(request.form['name'],
                request.form['message'],
                request.form['number'])

        msg = Message('FORM',
                body=body,
                sender="hss-app", recipients=["oneofy@gmail.com"])

        mail.send(msg)

    return render_template('frontend/contact-us.jade')

@frontend.route('/about-us')
def about_us():
    return render_template('frontend/about_us.jade')

@frontend.route('/<user_id>/gallery')
def gallery(user_id):
    title = 'Gallery'
    user = User.query.get(user_id)
    entity = user.provider or user.consumer
    gallery = entity.gallery
    return render_template('frontend/gallery.html', title=title, gallery=gallery)

@frontend.route('/')
def index():
    return render_template('frontend/index.html',
            index_search_form=SearchForm())

@login_required
@frontend.route('/photo/<int:photo_id>/favorite')
def add_to_favorites(photo_id):
    photo = Photo.query.get(photo_id) 
    current_user.favorite_photos.append(photo)
    db.session.add(current_user)
    db.session.commit()

    current_app.logger.info('{} favd by {}'.format(photo.url, current_user.email))
    
    if photo.gallery.provider_id:
        user = Provider.query.get(photo.gallery.provider_id).user
    else:
        user = Consumer.query.get(photo.gallery.consumer_id).user

    return redirect(url_for('frontend.gallery', user_id=user.id))

@frontend.route('/<provider_url>')
def provider_url(provider_url):
    p = Provider.query.filter(Provider._business_url==provider_url.lower()).first()

    # TODO wtf
    class d:
        def getDay(self):
            return datetime.date.today().isoweekday() 
    d = d() 

    if p:
        return render_template('frontend/provider.jade', provider=p, d=d)
    else:
        abort(404)

@frontend.route('/<provider_id>/comment', methods=['POST'])
def comment(provider_id):
    provider = Provider.get(provider_id)

    form = CommentForm()

    if not form.validate_on_submit():
        if form.errors:
            flash(form.errors)
            current_app.logger.info(errors)
    else:
        comment = Comment(body=form.body.data)

        current_user.consumer.comments.append(comment)
        current_user.consumer.save()

        if form.happy.data:
            provider.happy_customers.append(current_user.consumer)
        else:
            provider.unhappy_customers.append(current_user.consumer)

        provider.comments.append(comment)
        provider.save()

        return redirect(url_for('.provider_url', provider_url=provider.business_url))

@frontend.route('/consumer/<consumer_url>')
def consumer_url(consumer_url):
    c = Consumer.query.filter(Consumer.consumer_url==consumer_url.lower()).first()
    current_app.logger.info(c)
    if c:
        return render_template('frontend/consumer.jade', consumer=c)
    else:
        abort(404)

@login_required
@frontend.route('/<int:provider_id>/endorse')
def endorse(provider_id):
    if not current_user.provider:
        return abort()
    endorsee = Provider.query.filter(Provider.id == provider_id).first()
    current_user.provider.endorses.append(endorsee)
    db.session.add(current_user.provider)
    db.session.commit()
    return redirect(url_for('frontend.provider_url',
        provider_url=endorsee.business_url))


@frontend.route('/welcome')
@login_required
def welcome():
    return render_template('frontend/welcome.html')


@login_required
@roles_required(['consumer'])
@frontend.route('/<int:consumer_id>/follow')
def follow(consumer_id):
    first_person = current_user.consumer
    consumer = Consumer.query.get(consumer_id)

    first_person.follows.append(consumer)
    db.session.add(first_person)
    db.session.commit()

    return redirect(url_for('frontend.consumer_url',
        consumer_url=consumer.consumer_url))

@frontend.route('/provider_welcome')
def provider_welcome():
    return render_template('frontend/provider_marketing.jade')

@frontend.route('/consumer_welcome')
def consumer_welcome():
    return render_template('frontend/consumer_marketing.jade')

@frontend.route('/tos')
def tos():
    return render_template('frontend/tos.html')

@frontend.route('/privacy_policy')
def privacy_policy():
    return render_template('frontend/privacy_policy.html')
