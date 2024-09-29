import os
from datetime import datetime

from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from ..forms.found_item_report_form import FoundItemForm
from ..models.found_items_model import FoundItem, FoundImage
from ..models.user_model import User
from ..exts import db
from ..models.communication_model import Communication

found_items_bp = Blueprint('found_items', __name__, url_prefix='/found_items')

@found_items_bp.route('/', methods=['GET'])
def found_items_gallery_page():
    active_users = User.query.filter_by(is_active=True).subquery()
    query = FoundItem.query.filter(FoundItem.found_by_id.in_(db.session.query(active_users.c.id)))

    search = request.args.get('search','')
    filter_by = request.args.get('filter_by','')
    state = request.args.get('state','unclaimed')
    sort_by = request.args.get('sort_by','newest')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)

    if state == 'unclaimed':
        query = query.filter(FoundItem.is_claimed==False)
    elif state == 'claimed':
        query = query.filter(FoundItem.is_claimed==True)

    if search:
        query = query.filter(or_(
                FoundItem.name.ilike(f'%{search}%'),
                FoundItem.description.ilike(f'%{search}%'),
                FoundItem.colour.ilike(f'%{search}%'),
                FoundItem.brand.ilike(f'%{search}%'),
                FoundItem.additional_info.ilike(f'%{search}%'),
                FoundItem.location_found.ilike(f'%{search}%'),
                FoundItem.category.ilike(f'%{search}%')
            ))

    if filter_by:
        if filter_by == 'name':
            query = query.order_by(FoundItem.name.asc())
        elif filter_by == 'location_found':
            query = query.order_by(FoundItem.location_found.asc())
        elif filter_by == 'date_found':
            query = query.order_by(FoundItem.date_found.asc())
        elif filter_by == 'brand':
            query = query.order_by(FoundItem.brand.asc())
        elif filter_by == 'category':
            query = query.order_by(FoundItem.category.asc())
        elif filter_by == 'colour':
            query = query.order_by(FoundItem.colour.asc())

    if sort_by == 'newest':
        query = query.order_by(FoundItem.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(FoundItem.id.asc())

    pagination = query.paginate(page=page, per_page=per_page)
    items = pagination.items

    return render_template('found_items_gallery.html', items=items, pagination=pagination, per_page=per_page, search=search, filter_by=filter_by, state=state, sort_by=sort_by)

# Function to make unique filename
def unique_filename(directory, filename):
    counter = 1
    unique_name = filename
    basename, extension = os.path.splitext(filename)
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f'{basename}_{counter}{extension}'
        counter += 1
    return unique_name


@found_items_bp.route('/found_item_report', methods=['GET', 'POST'])
@login_required
def found_item_report():
    form = FoundItemForm()
    current_date = datetime.now().strftime('%Y-%m-%d')
    if form.validate_on_submit():
        # save image
        images = request.files.getlist('images')
        image_urls = []
        upload_dir = 'App/static/uploads/found_items'
        os.makedirs(upload_dir, exist_ok=True)

        for image in images:
            if image.filename:
                filename = secure_filename(image.filename)
                unique_name = unique_filename(upload_dir, filename)
                image_path = os.path.join(upload_dir, unique_name)
                image.save(image_path)
                image_urls.append(image_path)

        new_item = FoundItem(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            brand=form.brand.data,
            colour=form.colour.data,
            additional_info=form.additional_info.data,
            location_found=form.location_found.data,
            date_found=form.date_found.data.strftime('%Y-%m-%d'),
            found_by_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()

        for image_url in image_urls:
            image = FoundImage(url=image_url, found_item_id=new_item.id)
            db.session.add(image)

        db.session.commit()
        flash('Found Item has been reported successfully.', 'success')
        return redirect(url_for('found_items.found_items_gallery_page'))

    else:
        for field_name, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field_name}: {error}")
                flash(f"Error in {getattr(form, field_name).label.text}: {error}", 'danger')

    return render_template('found_item_report.html', form=form, current_date=current_date)

@found_items_bp.route('/<int:item_id>', methods=['GET', 'POST'])
def found_item_details_page(item_id):
    item = FoundItem.query.get_or_404(item_id)

    return render_template('found_item_details.html', item=item)

@found_items_bp.route('/claim_found_item/<int:item_id>', methods=['POST'])
@login_required
def claim_item(item_id):
    item = FoundItem.query.get_or_404(item_id)
    if not item.is_claimed:
        message = request.form['message']
        if not message:
            flash('A message is required to claim the item.', 'danger')
            return redirect(url_for('found_items.found_item_details_page', item_id=item.id))

        item.is_claimed = True
        item.claimed_by_id = current_user.id
        item.date_claimed = datetime.utcnow()

        new_message = Communication(
            found_item_id=item_id,
            sender_id=current_user.id,
            receiver_id=item.found_by_id,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()

        flash('Item claimed and your message sent successfully.', 'success')
    else:
        flash('Item is already claimed.', 'danger')

    return redirect(url_for('found_items.found_item_details_page', item_id=item.id))

@found_items_bp.route('/send_message/<int:item_id>', methods=['POST'])
@login_required
def send_message(item_id):
    item = FoundItem.query.get_or_404(item_id)
    message = request.form['message']

    if message:
        if item.found_by_id != current_user.id:
            receiver_id = item.found_by_id
        elif item.claimed_by_id != None:
            receiver_id = item.claimed_by_id
        else:
            receiver_id=current_user.id
        new_message = Communication(
            found_item_id=item.id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        try:
            db.session.commit()
            flash('Message sent successfully!', 'success')
        except Exception as e:
            print(f"Error saving message: {e}")  # Debug output
            flash('Failed to send message', 'danger')
    return redirect(url_for('found_items.found_item_details_page', item_id=item.id))

@found_items_bp.route('/delete_communication/<int:communication_id>', methods=['POST'])
@login_required
def delete_communication(communication_id):
    communication = Communication.query.get_or_404(communication_id)
    if communication.sender_id == current_user.id or current_user.is_admin:
        db.session.delete(communication)
        db.session.commit()
        flash('Message deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this message.', 'danger')
    return redirect(url_for('found_items.found_item_details_page', item_id=communication.found_item_id))

@found_items_bp.route('/reverse_claim_item/<int:item_id>', methods=['POST'])
@login_required
def reverse_claim_item(item_id):
    item = FoundItem.query.get_or_404(item_id)
    if item.is_claimed and item.claimed_by_id == current_user.id:
        item.is_claimed = False
        item.claimed_by_id = None
        item.date_claimed = None
        db.session.commit()
        flash('Reversed your claim successfully.','success')
    else:
        flash('You cannot reverse the claim.','danger')

    return redirect(url_for('found_items.found_item_details_page', item_id=item.id))

@found_items_bp.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = FoundItem.query.get_or_404(item_id)
    form = FoundItemForm(obj=item)
    current_date = datetime.now().strftime('%Y-%m-%d')

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
        return redirect(url_for('found_items.found_item_details_page', item_id=item.id))
    return render_template('found_item_edit.html', form=form, item=item, current_date=current_date)

@found_items_bp.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = FoundItem.query.get_or_404(item_id)
    if item.found_by_id == current_user.id or current_user.is_admin:
        for image in item.images:
            image_path = os.path.join('App/static/uploads/found_items', os.path.basename(image.url))
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(item)
        db.session.commit()
        flash('Item post and related images deleted successfully.','success')
    else:
        flash('You do not have permission to delete this item.','danger')
    return redirect(url_for('found_items.found_items_gallery_page'))