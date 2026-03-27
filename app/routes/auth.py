from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from wtforms import StringField, PasswordField, SelectField, validators
from flask_wtf import FlaskForm

auth_bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    username = StringField('用户名', [validators.DataRequired(), validators.Length(min=3, max=64)])
    password = PasswordField('密码', [validators.DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('用户名', [validators.DataRequired(), validators.Length(min=3, max=64)])
    name = StringField('姓名', [validators.DataRequired(), validators.Length(min=1, max=64)])
    student_id = StringField('学号', [validators.DataRequired(), validators.Length(min=1, max=32)])
    email = StringField('邮箱', [validators.Optional(), validators.Email()])
    password = PasswordField('密码', [validators.DataRequired(), validators.Length(min=6)])


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误。', 'error')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在。', 'error')
            return render_template('auth/register.html', form=form)
        if User.query.filter_by(student_id=form.student_id.data).first():
            flash('该学号已被注册。', 'error')
            return render_template('auth/register.html', form=form)

        user = User(
            username=form.username.data,
            name=form.name.data,
            student_id=form.student_id.data,
            email=form.email.data or None,
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('注册成功！请登录。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录。', 'info')
    return redirect(url_for('main.index'))
