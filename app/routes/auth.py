"""Authentication routes: register, login, and logout."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Display the registration form and create a new organizer account."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username is already taken.", "danger")
            return render_template("register.html", form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash("Email is already registered.", "danger")
            return render_template("register.html", form=form)

        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Account created! Configure your wedding in Settings.", "success")
            return redirect(url_for("main.settings"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "danger")

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Display the login form and authenticate an organizer."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current organizer."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
