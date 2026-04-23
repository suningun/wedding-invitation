"""Public invitation route — no login required."""

from flask import Blueprint, render_template, abort
from app.models import Guest, WeddingEvent
from app.utils import get_lang_value

invitation_bp = Blueprint("invitation", __name__)

VALID_TEMPLATES = {"classic"}


# Public invitation page (no login required) - accessed via unique token per guest
@invitation_bp.route("/invite/<token>")
def invitation(token: str):
    """Render personalized invitation card for guest using unique token (no login needed)."""
    # Fetch guest by unique invitation token
    guest = Guest.query.filter_by(invitation_token=token).first()
    if not guest:
        abort(404)

    # Fetch wedding details
    wedding = WeddingEvent.query.filter_by(wedding_id=guest.wedding_id).first()
    if not wedding:
        abort(404)

    # Use guest's preferred language (English or Khmer)
    lang = guest.language or "en"
    template_name = wedding.template or "classic"
    if template_name not in VALID_TEMPLATES:
        template_name = "classic"

    # Prepare invitation context with multilingual data
    context = {
        "guest": guest,
        "lang": lang,
        "bride_name": get_lang_value(wedding.bride_name, lang),
        "groom_name": get_lang_value(wedding.groom_name, lang),
        "venue_name": get_lang_value(wedding.venue_name, lang),
        "venue_address": get_lang_value(wedding.venue_address, lang),
        "welcome_message": get_lang_value(wedding.welcome_message, lang),
        "wedding_date": wedding.wedding_date,
        "ceremony_time": wedding.ceremony_time,
        "reception_time": wedding.reception_time,
        "venue_map_url": wedding.venue_map_url,
        "organizer_phone": wedding.organizer_phone,
    }

    return render_template(f"invitations/{template_name}.html", **context)
