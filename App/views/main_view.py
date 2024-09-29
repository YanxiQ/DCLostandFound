from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import current_user, login_required

from ..models.announce_model import Announcement
from ..forms.faq_form import *
from ..models.faq_model import *

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home_page():
    announcements = Announcement.query.order_by(Announcement.date_posted.desc()).limit(3).all()
    return render_template('index.html', announcements=announcements)

@main_bp.route('/about')
def about_page():
    return render_template('about.html')

@main_bp.route('/faqs')
def faqs_page():
    form=FaqForm()
    faqs = FAQ.query.filter(FAQ.is_answered == True).all()
    return render_template('faq.html', form=form, faqs=faqs)

@main_bp.route('/ask_question', methods=['POST'])
@login_required
def ask_question():
    form = FaqForm()
    if form.validate_on_submit():
        question = FAQ(
            user_id=current_user.id,
            question=form.question.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Your question has been submitted!', 'success')
        return redirect(url_for('main.faqs_page'))
    else:
        flash('There was an error with your submission.', 'danger')
        return render_template('faq.html', form=form)


