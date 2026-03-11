from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def landing():
    return render_template('auth/landing.html')


@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.route('/signup')
def signup_step1():
    return render_template('auth/signup_step1.html')


@auth_bp.route('/signup/step2')
def signup_step2():
    return render_template('auth/signup_step2.html')


@auth_bp.route('/signup/step3')
def signup_step3():
    return render_template('auth/signup_step3.html')


@auth_bp.route('/signup/verify')
def signup_verify():
    return render_template('auth/signup_verify.html')


@auth_bp.route('/signup/profile')
def signup_profile():
    return render_template('auth/signup_profile.html')


@auth_bp.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')


@auth_bp.route('/forgot-password/sent')
def forgot_password_sent():
    return render_template('auth/forgot_password_sent.html')


@auth_bp.route('/reset-password')
def reset_password():
    return render_template('auth/reset_password.html')
