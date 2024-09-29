import os
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from ..models.communication_model import Communication
from ..models.lost_items_model import LostItem
from ..models.lost_items_model import LostImage
from ..models.user_model import User
from ..forms.lost_item_form import LostItemForm
from ..exts import db

# Blueprint
lost_items_bp = Blueprint('lost_items', __name__, url_prefix='/lost_items')


# Utility function for unique filenames
def unique_filename(directory, filename):
    basename, extension = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{basename}_{counter}{extension}"
        counter += 1
    return unique_name


@lost_items_bp.route('/')
def lost_items_gallery_page():
    active_users = User.query.filter_by(is_active=True).subquery()
    query = LostItem.query.filter(LostItem.lost_by_id.in_(db.session.query(active_users.c.id)))

    search = request.args.get('search', '')
    filter_by = request.args.get('filter_by', '')
    state = request.args.get('state', 'unclaimed')
    sort_by = request.args.get('sort_by', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)

    if search:
        query = query.filter(or_(
            LostItem.name.ilike(f'%{search}%'),
            LostItem.description.ilike(f'%{search}%'),
            LostItem.colour.ilike(f'%{search}%'),
            LostItem.brand.ilike(f'%{search}%'),
            LostItem.additional_info.ilike(f'%{search}%'),
            LostItem.location_lost.ilike(f'%{search}%'),
            LostItem.category.ilike(f'%{search}%')
        ))

    if state == 'unclaimed':
        query = query.filter(LostItem.is_found==False)
    elif state == 'claimed':
        query = query.filter(LostItem.is_found==True)

    if filter_by:
        if filter_by == 'name':
            query = query.order_by(LostItem.name.asc())
        elif filter_by == 'location_lost':
            query = query.order_by(LostItem.location_lost.asc())
        elif filter_by == 'date_lost':
            query = query.order_by(LostItem.date_lost.desc())
        elif filter_by == 'brand':
            query = query.order_by(LostItem.brand.asc())
        elif filter_by == 'category':
            query = query.order_by(LostItem.category.asc())
        elif filter_by == 'colour':
            query = query.order_by(LostItem.colour.asc())

    if sort_by == 'newest':
        query = query.order_by(LostItem.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(LostItem.id.asc())

    pagination = query.paginate(page=page, per_page=per_page)
    items = pagination.items

    return render_template('lost_items_gallery.html', items=items, pagination=pagination, per_page=per_page, search=search, filter_by=filter_by, state=state, sort_by=sort_by)


@lost_items_bp.route('/report_lost_item', methods=['GET', 'POST'])
@login_required
def report_lost_item_page():
    form = LostItemForm()
    current_date = datetime.now().strftime('%Y-%m-%d')
    if form.validate_on_submit():
        images = request.files.getlist('images')
        image_urls = []
        upload_dir = 'App/static/uploads/lost_items'
        os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists

        for image in images:
            if image.filename:  # Ensure the file is not empty
                filename = secure_filename(image.filename)
                unique_name = unique_filename(upload_dir, filename)
                image_path = os.path.join(upload_dir, unique_name)
                image.save(image_path)
                image_urls.append(image_path)

        new_item = LostItem(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            brand=form.brand.data,
            colour=form.colour.data,
            additional_info=form.additional_info.data,
            location_lost=form.location_lost.data,
            date_lost=form.date_lost.data.strftime('%Y-%m-%d'),
            lost_by_id=current_user.id  # Ensure current_user is set correctly
        )
        db.session.add(new_item)
        db.session.commit()

        for image_url in image_urls:
            new_image = LostImage(url=image_url, lost_item_id=new_item.id)
            db.session.add(new_image)

        db.session.commit()
        flash('Lost item reported successfully!', 'success')
        return redirect(url_for('lost_items.lost_items_gallery_page'))

    return render_template('lost_item_report.html', form=form, current_date=current_date)


@lost_items_bp.route('/<int:item_id>', methods=['GET', 'POST'])
def lost_item_details_page(item_id):
    item = LostItem.query.get_or_404(item_id)

    return render_template('lost_item_details.html', item=item)


@lost_items_bp.route('/send_message/<int:item_id>', methods=['POST'])
@login_required
def send_message(item_id):
    item = LostItem.query.get_or_404(item_id)
    message = request.form['message']
    if message:
        receiver_id = item.lost_by_id if item.lost_by_id != current_user.id else (item.found_by_id or current_user.id)

        new_message = Communication(
            lost_item_id=item.id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
    else:
        flash('Message cannot be empty', 'danger')
    return redirect(url_for('lost_items.lost_item_details_page', item_id=item.id))


@lost_items_bp.route('/delete_communication/<int:communication_id>', methods=['POST'])
@login_required
def delete_communication(communication_id):
    communication = Communication.query.get_or_404(communication_id)
    if communication.sender_id == current_user.id or current_user.is_admin:
        db.session.delete(communication)
        db.session.commit()
        flash('Message deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this message.', 'danger')
    return redirect(url_for('lost_items.lost_item_details_page', item_id=communication.lost_item_id))


@lost_items_bp.route('/claim_item/<int:item_id>', methods=['POST'])
@login_required
def claim_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    if not item.is_found:
        message = request.form['message']
        if not message:
            flash('Message is required to claim the item.', 'danger')
            return redirect(url_for('lost_items.lost_item_details_page', item_id=item.id))

        item.is_found = True
        item.found_by_id = current_user.id
        item.date_found = datetime.utcnow()

        new_message = Communication(
            lost_item_id=item.id,
            sender_id=current_user.id,
            receiver_id=item.lost_by_id,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()

        flash('Item claimed and message sent successfully!', 'success')
    else:
        flash('Item is already claimed.', 'danger')
    return redirect(url_for('lost_items.lost_item_details_page', item_id=item.id))


@lost_items_bp.route('/reverse_claim_item/<int:item_id>', methods=['POST'])
@login_required
def reverse_claim_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    if item.is_found and item.found_by_id == current_user.id:
        item.is_found = False
        item.found_by_id = None
        item.date_found = None
        db.session.commit()
        flash('Claim reversed successfully!', 'success')
    else:
        flash('You cannot reverse the claim.', 'danger')
    return redirect(url_for('lost_items.lost_item_details_page', item_id=item.id))


@lost_items_bp.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    current_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.category = request.form['category']
        item.brand = request.form['brand']
        item.colour = request.form['colour']
        item.additional_info = request.form['additional_info']
        item.location_lost = request.form['location_lost']
        item.date_lost = request.form['date_lost']
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('lost_items.lost_item_details_page', item_id=item.id))
    return render_template('lost_item_edit.html', item=item, current_date=current_date)






@lost_items_bp.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    if item.lost_by_id == current_user.id or current_user.is_admin:
        # Delete related images from the folder
        for image in item.images:
            image_path = os.path.join('App/static/uploads/lost_items', os.path.basename(image.url))
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(item)
        db.session.commit()
        flash('Item and related images deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this item.', 'danger')
    return redirect(url_for('lost_items.lost_items_gallery_page'))


# @lost_items_bp.route('/inbox', methods=['GET'])
# @login_required
# def inbox():
#     received_messages = Communication.query.filter_by(receiver_id=current_user.id).order_by(Communication.timestamp.desc()).all()
#     sent_messages = Communication.query.filter_by(sender_id=current_user.id).order_by(Communication.timestamp.desc()).all()
#     return render_template('inbox.html', received_messages=received_messages, sent_messages=sent_messages)


# @lost_items_bp.route('/reply_message', methods=['POST'])
# @login_required
# def reply_message():
#     receiver_id = request.form['receiver_id']
#     original_message_id = request.form['original_message_id']
#     message_text = request.form['message']
#     if not message_text:
#         flash('Message text is required.', 'danger')
#         return redirect(url_for('lost_items.inbox'))
#
#     original_message = Communication.query.get_or_404(original_message_id)
#     new_message = Communication(
#         lost_item_id=original_message.lost_item_id,
#         sender_id=current_user.id,
#         receiver_id=receiver_id,
#         message=f"Re: {original_message.message}\n\n{message_text}",
#         timestamp=datetime.utcnow()
#     )
#     db.session.add(new_message)
#     db.session.commit()
#
#     flash('Reply sent successfully!', 'success')
#     return redirect(url_for('lost_items.inbox'))