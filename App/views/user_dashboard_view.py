import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from datetime import datetime

from werkzeug.utils import secure_filename

from ..models.lost_items_model import LostItem
from ..forms.user_profile_form import UserProfileForm
from ..models.user_model import User
from ..models.found_items_model import FoundItem
from ..models.communication_model import Communication
from ..exts import db


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')



@dashboard_bp.route('/profile')
@login_required
def user_dashboard_profile():
    form = UserProfileForm(obj=current_user)
    return render_template('user_dashboard_profile.html', form=form)


@dashboard_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    form = UserProfileForm()
    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.phone = form.phone.data
        current_user.student_id = form.student_id.data

        if form.profile_pic.data:
            profile_pic = form.profile_pic.data
            filename = secure_filename(profile_pic.filename)
            filepath = os.path.join('App/static/uploads/profile_pics', filename)
            profile_pic.save(filepath)
            current_user.profile_pic = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.user_dashboard_profile'))
    return render_template('user_dashboard_profile.html', form=form)


@dashboard_bp.route('/inbox')
@login_required
def inbox():
    conversations = db.session.query(
        Communication.found_item_id,
        Communication.lost_item_id
    ).filter(
        (Communication.sender_id == current_user.id) | (Communication.receiver_id == current_user.id)
    ).distinct().all()

    conversation_details = []
    for found_item_id, lost_item_id in conversations:
        if found_item_id:
            latest_message = db.session.query(Communication).filter_by(found_item_id=found_item_id).order_by(
                Communication.timestamp.desc()).first()
            item_id = found_item_id
            item = db.session.query(FoundItem).get(found_item_id)
            item_type = 'found'
        else:
            latest_message = db.session.query(Communication).filter_by(lost_item_id=lost_item_id).order_by(
                Communication.timestamp.desc()).first()
            item_id = lost_item_id
            item = db.session.query(LostItem).get(lost_item_id)
            item_type = 'lost'

        conversation_details.append({
            'item_id': item_id,
            'item_type': item_type,
            'latest_message': latest_message,
            'item': item
        })
    conversation_details.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)

    return render_template('user_inbox.html', conversations=conversation_details)



@dashboard_bp.route('/view_message.html/<int:item_id>/<string:item_type>', methods=['GET', 'POST'])
@login_required
def view_message(item_id, item_type):
    new_messages_count = current_user.new_messages_count
    if item_type == 'found':
        related_item = FoundItem.query.get_or_404(item_id)
        all_messages = Communication.query.filter_by(found_item_id=item_id).order_by(Communication.timestamp.asc()).all()
    else:
        related_item = LostItem.query.get_or_404(item_id)
        all_messages = Communication.query.filter_by(lost_item_id=item_id).order_by(Communication.timestamp.asc()).all()

    for message in all_messages:
        if message.receiver_id == current_user.id:
            message.is_read = True
            db.session.commit()

    if request.method == 'POST':
        reply_text = request.form['message']
        receiver_id = request.form['receiver_id']
        new_message = Communication(
            found_item_id=item_id if item_type == 'found' else None,
            lost_item_id=item_id if item_type == 'lost' else None,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=reply_text,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()
        flash('Reply sent successfully!', 'success')
        return redirect(url_for('dashboard.view_message', item_id=item_id, item_type=item_type))

    return render_template('view_message.html', related_item=related_item, all_messages=all_messages, item_type=item_type, new_messages_count=new_messages_count)

@dashboard_bp.route('/claimed_items')
@login_required
def my_claimed_items():
    user_id = current_user.id
    claimed_items = FoundItem.query.filter_by(claimed_by_id=user_id).all()
    return render_template('user_dashboard_claimed_items.html', claimed_items=claimed_items)

@dashboard_bp.route('/found_items')
@login_required
def my_found_items():
    user_id = current_user.id
    found_items = FoundItem.query.filter_by(found_by_id=user_id).all()
    return render_template('user_dashboard_found_items.html', found_items=found_items)

@dashboard_bp.route('/lost_items')
@login_required
def my_lost_items():
    user_id = current_user.id
    lost_items = LostItem.query.filter_by(lost_by_id=user_id).all()
    return render_template('user_dashboard_lost_items.html', lost_items=lost_items)
#
#
#
# from flask_login import current_user, login_required
#
# @dashboard_bp.route('/user_dashboard/lost_items')
# @login_required
# def user_lost_items():
#     user_id = current_user.id  # Access the current user's ID
#     lost_items = LostItem.query.filter_by(lost_by_id=user_id).all()
#     return render_template('user_dashboard_lost_items.html', lost_items=lost_items)
#
#
#
# @dashboard_bp.route('/user_dashboard/found_items')
# @login_required
# def user_found_items():
#     user_id = current_user.id  # Access the current user's ID
#     found_items = FoundItem.query.filter_by(found_by_id=user_id).all()
#     return render_template('user_dashboard_found_items.html', found_items=found_items)
#
# @dashboard_bp.route('/user_dashboard/claimed_items')
# @login_required
# def user_claimed_items():
#     user_id = current_user.id  # Access the current user's ID
#     claimed_items = FoundItem.query.filter_by(claimed_by_id=user_id).all()
#     return render_template('user_dashboard_claimed_items.html', claimed_items=claimed_items)
#
# @dashboard_bp.route('/admin_dashboard/users')
# @login_required
# def admin_users():
#     # if session['role'] != 'admin':
#     #     return redirect(url_for('login'))
#     users = User.query.all()
#     return render_template('admin_user_management.html', users=users)
#
# @dashboard_bp.route('/admin_dashboard/lost_items')
# def admin_lost_items():
#     # if 'user_id' not in session or session['role'] != 'admin':
#     #     return redirect(url_for('login'))
#     lost_items = LostItem.query.all()
#     return render_template('admin_lost_items_management.html', lost_items=lost_items)
#
# @dashboard_bp.route('/admin_dashboard/found_items')
# def admin_found_items():
#     # if 'user_id' not in session or session['role'] != 'admin':
#     #     return redirect(url_for('login'))
#     found_items = FoundItem.query.all()
#     return render_template('admin_found_items_management.html', found_items=found_items)