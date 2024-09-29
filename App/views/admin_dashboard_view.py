import os

from flask import Blueprint, flash, redirect, url_for, render_template, request, session
from flask_login import current_user, login_user, logout_user, login_required

from .. import FAQ
from ..forms.faq_form import AnswerFaqForm
from ..models.user_model import *
from ..models.found_items_model import *
from ..forms.found_item_report_form import *
from ..models.lost_items_model import *
from ..forms.lost_item_form import *

admin_bp = Blueprint('admin', __name__)

def is_admin():
    return current_user.is_authenticated and current_user.role == 'Admin'

@admin_bp.route('/user_management')
def user_management():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    users = User.query.all()
    return render_template('admin_user_management.html', users=users)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.firstname = request.form['firstname']
        user.lastname = request.form['lastname']
        user.phone = request.form['phone']
        user.student_id = request.form['student_id']
        db.session.commit()
        return redirect(url_for('admin.user_management'))
    return render_template('admin_user_edit.html', user=user)

@admin_bp.route('/deactivate_user/<int:user_id>', methods=['GET','POST'])
def deactivate_user(user_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    user = User.query.get_or_404(user_id)
    if user:
        user.is_active = False
        db.session.commit()
        flash(f'User {user.firstname} {user.lastname} has been deactivated.', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/activate_user/<int:user_id>', methods=['GET','POST'])
def reactivate_user(user_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    user = User.query.get_or_404(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        flash(f'User {user.firstname} {user.lastname} has been activated.', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/found_items_management')
def found_items_management():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    items = FoundItem.query.all()
    return render_template('admin_found_items_management.html',items=items)

@admin_bp.route('/edit_found_item/<int:item_id>', methods=['GET','POST'])
def edit_found_item(item_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    item = FoundItem.query.get_or_404(item_id)
    form = FoundItemForm(obj=item)

    if request.method == 'POST':
        item.name = form.name.data
        item.description = form.description.data
        item.category = form.category.data
        item.brand = form.brand.data
        item.colour = form.colour.data
        item.additional_info = form.additional_info.data
        item.location_found = form.location_found.data
        item.date_found = form.date_found.data
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('admin.found_items_management', item_id=item.id))
    return render_template('admin_found_item_edit.html', form=form, item=item)

@admin_bp.route('/delete_found_item/<int:item_id>', methods=['POST'])
def delete_found_item(item_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    item = FoundItem.query.get_or_404(item_id)
    for image in item.images:
        image_path = os.path.join('App/static/uploads/found_items', os.path.basename(image.url))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(item)
    db.session.commit()
    flash('Item post and related images deleted successfully.','success')
    return redirect(url_for('admin.found_items_management'))

@admin_bp.route('/lost_items_management')
def lost_items_management():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    items = LostItem.query.all()
    return render_template('admin_lost_items_management.html',items=items)

@admin_bp.route('/edit_lost_item/<int:item_id>', methods=['GET','POST'])
def edit_lost_item(item_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    item = LostItem.query.get_or_404(item_id)
    form = LostItemForm(obj=item)

    if request.method == 'POST':
        item.name = form.name.data
        item.description = form.description.data
        item.category = form.category.data
        item.brand = form.brand.data
        item.colour = form.colour.data
        item.additional_info = form.additional_info.data
        item.location_lost = form.location_lost.data
        item.date_lost = form.date_lost.data
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('admin.lost_items_management', item_id=item.id))
    return render_template('admin_lost_item_edit.html', form=form, item=item)

@admin_bp.route('/delete_lost_item/<int:item_id>', methods=['POST'])
def delete_lost_item(item_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    item = LostItem.query.get_or_404(item_id)
    for image in item.images:
        image_path = os.path.join('App/static/uploads/found_items', os.path.basename(image.url))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(item)
    db.session.commit()
    flash('Item post and related images deleted successfully.','success')
    return redirect(url_for('admin.lost_items_management'))

@admin_bp.route('/message_log')
def message_log():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    conversations = db.session.query(
        Communication.found_item_id,
        Communication.lost_item_id
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

    return render_template('admin_user_message_log.html', conversations=conversation_details)

@admin_bp.route('/view_message.html/<int:item_id>/<string:item_type>', methods=['GET', 'POST'])
@login_required
def admin_view_message(item_id, item_type):
    new_messages_count = current_user.new_messages_count
    if item_type == 'found':
        related_item = FoundItem.query.get_or_404(item_id)
        all_messages = Communication.query.filter_by(found_item_id=item_id).order_by(Communication.timestamp.asc()).all()
    else:
        related_item = LostItem.query.get_or_404(item_id)
        all_messages = Communication.query.filter_by(lost_item_id=item_id).order_by(Communication.timestamp.asc()).all()

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
        return redirect(url_for('admin.admin_view_message', item_id=item_id, item_type=item_type))

    return render_template('admin_view_message.html', related_item=related_item, all_messages=all_messages, item_type=item_type, new_messages_count=new_messages_count)

@admin_bp.route('/faq_management', methods=['GET', 'POST'])
def faq_management():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    faqs = FAQ.query.all()
    form = AnswerFaqForm()
    return render_template('admin_faq_management.html', faqs=faqs, form=form)

@admin_bp.route('/faq_answer/<int:faq_id>', methods=['GET', 'POST'])
def faq_answer(faq_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    faq = FAQ.query.get_or_404(faq_id)
    form = AnswerFaqForm()

    if form.validate_on_submit():
        faq.answer = form.answer.data
        faq.is_answered = True
        db.session.commit()
        flash('Answer submitted successfully!', 'success')
    return redirect(url_for('admin.faq_management'))

@admin_bp.route('/faq_delete/<int:faq_id>', methods=['GET', 'POST'])
def faq_delete(faq_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully!', 'success')
    return redirect(url_for('admin.faq_management'))

@admin_bp.route('/faq_publish', methods=['GET', 'POST'])
def faq_publish(faq_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
        faq = FAQ.query.get_or_404(faq_id)
        faq.is_public = True
        db.session.commit()
        flash('FAQ published successfully!', 'success')
    return redirect(url_for('admin.faq_management'))