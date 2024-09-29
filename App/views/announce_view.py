from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user
from ..exts import db

from ..models.announce_model import Announcement
from ..forms.announce_form import AnnounceForm

announce_bp = Blueprint('announcements', __name__)

@announce_bp.route('/', methods=['GET'])
def announcement_list():
    announcements = Announcement.query.order_by(Announcement.date_posted.desc()).all()
    return render_template('announcements.html', announcements=announcements)

@announce_bp.route('/<int:announcement_id>', methods=['GET'])
def announcement_detail(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    return render_template('announcement_detail.html', announcement=announcement)

@announce_bp.route('/create', methods=['GET','POST'])
def create_announcement():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    form = AnnounceForm()
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement created successfully!','success')
        return redirect(url_for('announcements.announcement_list'))
    return render_template('create_announcement.html', form=form)

@announce_bp.route('/<int:announcement_id>/edit', methods=['GET','POST'])
def edit_announcement(announcement_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    announcement = Announcement.query.get_or_404(announcement_id)

    form = AnnounceForm(obj=announcement)
    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.content = form.content.data
        db.session.commit()
        flash('Announcement updated successfully.', 'success')
        return redirect(url_for('announcements.announcement_detail', announcement_id=announcement.id))

    return render_template('edit_announcement.html', form=form, announcement=announcement)

@announce_bp.route('/<int:announcement_id>/delete', methods=['POST'])
def delete_announcement(announcement_id):
    if not current_user.is_authenticated or current_user.role != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.login'))
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted successfully.', 'success')
    return redirect(url_for('announcements.announcement_list'))




