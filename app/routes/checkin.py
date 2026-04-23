"""Check-in routes: search guests and record check-in with gift details."""

from datetime import datetime, timezone
from decimal import Decimal

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import WeddingEvent, Guest
from app.forms import CheckInForm

checkin_bp = Blueprint("checkin", __name__)


def get_wedding():
    """Get the current user's wedding, or None."""
    return WeddingEvent.query.filter_by(user_id=current_user.id).first()


# Display check-in interface with search box
@checkin_bp.route("/check-in")
@login_required
def checkin_index():
    """Display the check-in page with search box for finding guests."""
    return render_template("checkin/index.html")


# Real-time search for check-in (HTMX endpoint)
@checkin_bp.route("/check-in/search")
@login_required
def checkin_search():
    """HTMX endpoint: search guests and return matching guest cards."""
    wedding = get_wedding()
    q = request.args.get("q", "").strip().lower()

    if not q or not wedding:
        return render_template("checkin/_results.html", guests=[])

    guests = (
        Guest.query.filter_by(wedding_id=wedding.wedding_id)
        .order_by(Guest.full_name)
        .all()
    )
    matches = [
        g
        for g in guests
        if q in (g.full_name or "").lower()
        or q in (g.nickname or "").lower()
        or q in (g.phone or "").lower()
    ]
    return render_template("checkin/_results.html", guests=matches)


# Load check-in modal form (HTMX endpoint)
@checkin_bp.route("/check-in/<guest_id>/modal")
@login_required
def checkin_modal(guest_id: str):
    """HTMX endpoint: return check-in form modal pre-populated with guest & gift data."""
    wedding = get_wedding()
    if not wedding:
        return "", 404
    guest = Guest.query.filter_by(
        guest_id=guest_id, wedding_id=wedding.wedding_id
    ).first_or_404()

    form = CheckInForm()
    if guest.gift_amount:
        form.gift_amount.data = guest.gift_amount
    if guest.gift_currency:
        form.gift_currency.data = guest.gift_currency
    if guest.gift_note:
        form.gift_note.data = guest.gift_note
    return render_template("checkin/_modal.html", guest=guest, form=form)


# Record guest arrival & gift details
@checkin_bp.route("/check-in/<guest_id>", methods=["POST"])
@login_required
def checkin_submit(guest_id: str):
    """Mark guest as checked-in with timestamp and record gift details."""
    wedding = get_wedding()
    if not wedding:
        return "", 404
    guest = Guest.query.filter_by(
        guest_id=guest_id, wedding_id=wedding.wedding_id
    ).first_or_404()

    form = CheckInForm()
    if form.validate_on_submit():
        try:
            # Mark guest as checked in with current timestamp (only first time)
            if not guest.checked_in:
                guest.checked_in = True
                guest.check_in_time = datetime.now(timezone.utc)

            # Record gift amount, currency, and note
            guest.gift_amount = form.gift_amount.data or Decimal("0.00")
            guest.gift_currency = form.gift_currency.data
            guest.gift_note = form.gift_note.data
            db.session.commit()
            flash(f"{guest.full_name} checked in successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error checking in guest: {str(e)}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")

    return redirect(url_for("checkin.checkin_index"))
