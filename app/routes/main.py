"""Main routes: dashboard and wedding settings."""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import WeddingEvent, Guest
from app.forms import WeddingSettingsForm

main_bp = Blueprint("main", __name__)


# Helper function to fetch current user's wedding
def get_wedding():
    """Get the current user's wedding (ensures data isolation)."""
    return WeddingEvent.query.filter_by(user_id=current_user.id).first()


# Helper function to fetch all guests for current wedding
def get_guests():
    """Get all guests for the current user's wedding."""
    wedding = get_wedding()
    if not wedding:
        return []
    return Guest.query.filter_by(wedding_id=wedding.wedding_id).all()


# Redirect to dashboard
@main_bp.route("/")
@login_required
def index():
    """Redirect root URL to dashboard."""
    return redirect(url_for("main.dashboard"))


# Main dashboard with real-time stats: guests, check-ins, gifts by side & currency
@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Display main dashboard with statistics, charts, and recent check-ins."""
    guests = get_guests()
    wedding = get_wedding()
    # Calculate basic statistics
    total = len(guests)
    shared = sum(1 for g in guests if g.invitation_shared)
    not_shared = total - shared
    checked_in = sum(1 for g in guests if g.checked_in)

    # Aggregate gifts by currency
    total_usd = sum(
        float(g.gift_amount or 0) for g in guests if g.gift_currency == "USD"
    )
    total_khr = sum(
        float(g.gift_amount or 0) for g in guests if g.gift_currency == "KHR"
    )

    recent_checkins = []
    if wedding:
        recent_checkins = (
            Guest.query.filter(
                Guest.wedding_id == wedding.wedding_id,
                Guest.checked_in == True,
            )
            .order_by(Guest.check_in_time.desc())
            .limit(10)
            .all()
        )

    bride_usd = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "bride" and g.gift_currency == "USD"
    )
    bride_khr = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "bride" and g.gift_currency == "KHR"
    )
    groom_usd = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "groom" and g.gift_currency == "USD"
    )
    groom_khr = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "groom" and g.gift_currency == "KHR"
    )

    chart_data = {
        "bride_usd": bride_usd,
        "bride_khr": bride_khr,
        "groom_usd": groom_usd,
        "groom_khr": groom_khr,
    }

    return render_template(
        "dashboard.html",
        total=total,
        shared=shared,
        not_shared=not_shared,
        checked_in=checked_in,
        total_usd=total_usd,
        total_khr=total_khr,
        recent_checkins=recent_checkins,
        chart_data=chart_data,
    )


# HTMX polling endpoint - returns updated stats every 30 seconds
@main_bp.route("/dashboard/stats")
@login_required
def dashboard_stats():
    """HTMX endpoint: return updated stats for real-time dashboard polling."""
    guests = get_guests()
    wedding = get_wedding()
    # Recalculate all statistics for fresh data
    total = len(guests)
    shared = sum(1 for g in guests if g.invitation_shared)
    not_shared = total - shared
    checked_in = sum(1 for g in guests if g.checked_in)
    total_usd = sum(
        float(g.gift_amount or 0) for g in guests if g.gift_currency == "USD"
    )
    total_khr = sum(
        float(g.gift_amount or 0) for g in guests if g.gift_currency == "KHR"
    )

    # Get 10 most recent check-ins
    recent_checkins = []
    if wedding:
        recent_checkins = (
            Guest.query.filter(
                Guest.wedding_id == wedding.wedding_id,
                Guest.checked_in == True,
            )
            .order_by(Guest.check_in_time.desc())
            .limit(10)
            .all()
        )

    bride_usd = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "bride" and g.gift_currency == "USD"
    )
    bride_khr = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "bride" and g.gift_currency == "KHR"
    )
    groom_usd = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "groom" and g.gift_currency == "USD"
    )
    groom_khr = sum(
        float(g.gift_amount or 0)
        for g in guests
        if g.side == "groom" and g.gift_currency == "KHR"
    )

    chart_data = {
        "bride_usd": bride_usd,
        "bride_khr": bride_khr,
        "groom_usd": groom_usd,
        "groom_khr": groom_khr,
    }

    return render_template(
        "dashboard_stats.html",
        total=total,
        shared=shared,
        not_shared=not_shared,
        checked_in=checked_in,
        total_usd=total_usd,
        total_khr=total_khr,
        recent_checkins=recent_checkins,
        chart_data=chart_data,
    )


@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Display and save the wedding configuration form."""
    wedding = get_wedding()
    form = WeddingSettingsForm()

    if form.validate_on_submit():
        try:
            if not wedding:
                wedding = WeddingEvent(user_id=current_user.id)
                db.session.add(wedding)

            wedding.template = form.template.data
            wedding.wedding_date = form.wedding_date.data
            wedding.ceremony_time = form.ceremony_time.data
            wedding.reception_time = form.reception_time.data
            wedding.venue_map_url = form.venue_map_url.data
            wedding.organizer_phone = form.organizer_phone.data

            wedding.bride_name = {
                "en": form.bride_name_en.data or "",
                "km": form.bride_name_km.data or "",
            }
            wedding.groom_name = {
                "en": form.groom_name_en.data or "",
                "km": form.groom_name_km.data or "",
            }
            wedding.venue_name = {
                "en": form.venue_name_en.data or "",
                "km": form.venue_name_km.data or "",
            }
            wedding.venue_address = {
                "en": form.venue_address_en.data or "",
                "km": form.venue_address_km.data or "",
            }
            wedding.welcome_message = {
                "en": form.welcome_message_en.data or "",
                "km": form.welcome_message_km.data or "",
            }

            db.session.commit()
            flash("Wedding settings saved successfully!", "success")
            return redirect(url_for("main.settings"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving settings: {str(e)}", "danger")
    elif not form.is_submitted() and wedding:
        form.template.data = wedding.template
        form.wedding_date.data = wedding.wedding_date
        form.ceremony_time.data = wedding.ceremony_time
        form.reception_time.data = wedding.reception_time
        form.venue_map_url.data = wedding.venue_map_url
        form.organizer_phone.data = wedding.organizer_phone
        form.bride_name_en.data = (wedding.bride_name or {}).get("en", "")
        form.bride_name_km.data = (wedding.bride_name or {}).get("km", "")
        form.groom_name_en.data = (wedding.groom_name or {}).get("en", "")
        form.groom_name_km.data = (wedding.groom_name or {}).get("km", "")
        form.venue_name_en.data = (wedding.venue_name or {}).get("en", "")
        form.venue_name_km.data = (wedding.venue_name or {}).get("km", "")
        form.venue_address_en.data = (wedding.venue_address or {}).get("en", "")
        form.venue_address_km.data = (wedding.venue_address or {}).get("km", "")
        form.welcome_message_en.data = (wedding.welcome_message or {}).get("en", "")
        form.welcome_message_km.data = (wedding.welcome_message or {}).get("km", "")

    return render_template("settings.html", form=form, wedding=wedding)
