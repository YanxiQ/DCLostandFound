from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import current_user, login_user, logout_user, login_required

from ..exts import bcrypt, db

from App import User
from App.forms.student_register_form import StudentRegisterForm
from App.forms.parent_register_form import ParentRegisterForm
from App.forms.login_form import LoginForm

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@user_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    form = StudentRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists, please login instead.','warning')
            return redirect(url_for('user.login'))
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            firstname = form.first_name.data,
            lastname = form.last_name.data,
            email = form.email.data,
            password = hashed_pass,
            phone = form.phone.data,
            role = 'Student',
            student_id = form.student_id.data
        )
        db.session.add(user)
        db.session.commit()
        flash('You have been registered successfully.', 'success')
        return redirect(url_for('user.login'))
    return render_template('register_student.html', form=form)

@user_bp.route('/register/parent', methods=['GET', 'POST'])
def register_parent():
    form = ParentRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists, please login instead.','warning')
            return redirect(url_for('user.login'))
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            firstname = form.first_name.data,
            lastname = form.last_name.data,
            email = form.email.data,
            password = hashed_pass,
            phone = form.phone.data,
            role = 'Parent'
        )
        db.session.add(user)
        db.session.commit()
        flash('You have been registered successfully.', 'success')
        return redirect(url_for('user.login'))
    return render_template('register_parent.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and user.is_active:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home_page'))
            else:
                flash('Login Unsuccessful. Please try again.','danger')
        else:
            flash('This account has been deactivated.', 'warning')
    return render_template('login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home_page'))




