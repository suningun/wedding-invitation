"""Guest management routes: CRUD, search, import, and HTMX partials."""
import csv
import io

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, send_file
from flask_login import login_required, current_user
from app import db
from app.models import WeddingEvent, Guest
from app.forms import GuestForm, GuestImportForm

guests_bp = Blueprint("guests", __name__)


# Helper function to fetch current user's wedding for authorization
def get_wedding():
    """Get the current user's wedding, or None (ensures data isolation)."""
    return WeddingEvent.query.filter_by(user_id=current_user.id).first()


# Security check: only return guest if they belong to current user's wedding
def get_guest_or_404(guest_id: str) -> Guest:
    """Get a guest that belongs to the current user's wedding, or return 404 (security)."""
    wedding = get_wedding()
    if not wedding:
        abort(404)
    guest = Guest.query.filter_by(
        guest_id=guest_id, wedding_id=wedding.wedding_id
    ).first_or_404()
    return guest


# Display all guests with filtering (shared/checked-in status)
@guests_bp.route("/guests")
@login_required
def guest_list():
    """Display the guest list with status filtering (shared/checked-in)."""
    wedding = get_wedding()
    filter_by = request.args.get("filter", "all")

    if not wedding:
        guests = []
    else:
        query = Guest.query.filter_by(wedding_id=wedding.wedding_id)

        if filter_by == "shared":
            query = query.filter(Guest.invitation_shared == True)
        elif filter_by == "not_shared":
            query = query.filter(Guest.invitation_shared == False)
        elif filter_by == "checked_in":
            query = query.filter(Guest.checked_in == True)
        elif filter_by == "not_checked_in":
            query = query.filter(Guest.checked_in == False)

        guests = query.order_by(Guest.created_at.desc()).all()

    form = GuestForm()
    import_form = GuestImportForm()
    base_url = current_app.config["BASE_URL"]
    return render_template(
        "guests/list.html",
        guests=guests,
        form=form,
        import_form=import_form,
        filter_by=filter_by,
        base_url=base_url,
    )


# Real-time search endpoint for HTMX (searches by name/nickname/phone)
@guests_bp.route("/guests/search")
@login_required
def guest_search():
    """HTMX endpoint: real-time search across name, nickname, and phone fields."""
    wedding = get_wedding()
    q = request.args.get("q", "").strip().lower()
    filter_by = request.args.get("filter", "all")

    if not wedding:
        return render_template("guests/_rows.html", guests=[], base_url="")

    query = Guest.query.filter_by(wedding_id=wedding.wedding_id)

    if filter_by == "shared":
        query = query.filter(Guest.invitation_shared == True)
    elif filter_by == "not_shared":
        query = query.filter(Guest.invitation_shared == False)
    elif filter_by == "checked_in":
        query = query.filter(Guest.checked_in == True)
    elif filter_by == "not_checked_in":
        query = query.filter(Guest.checked_in == False)

    guests = query.order_by(Guest.created_at.desc()).all()

    if q:
        guests = [
            g
            for g in guests
            if q in (g.full_name or "").lower()
            or q in (g.nickname or "").lower()
            or q in (g.phone or "").lower()
        ]

    base_url = current_app.config["BASE_URL"]
    return render_template(
        "guests/_rows.html", guests=guests, base_url=base_url
    )


# Create new guest with auto-generated UUID & invitation token
@guests_bp.route("/guests/add", methods=["POST"])
@login_required
def guest_add():
    """Add a new guest to the current user's wedding (auto-generates unique token)."""
    wedding = get_wedding()
    if not wedding:
        flash("Please configure your wedding in Settings first.", "danger")
        return redirect(url_for("main.settings"))

    form = GuestForm()
    if form.validate_on_submit():
        try:
            guest = Guest(
                wedding_id=wedding.wedding_id,
                full_name=form.full_name.data,
                nickname=form.nickname.data,
                phone=form.phone.data,
                email=form.email.data,
                side=form.side.data,
                language=form.language.data,
                notes=form.notes.data,
            )
            db.session.add(guest)
            db.session.commit()
            flash("Guest added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding guest: {str(e)}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for("guests.guest_list"))


# Edit guest details (GET shows form, POST saves changes)
@guests_bp.route("/guests/<guest_id>/edit", methods=["GET", "POST"])
@login_required
def guest_edit(guest_id: str):
    """Edit an existing guest (GET returns form, POST saves updates)."""
    guest = get_guest_or_404(guest_id)
    form = GuestForm(obj=guest)

    # GET: Return form for editing guest
    if request.method == "GET":
        return render_template("guests/_form.html", form=form, guest=guest)

    # POST: Save guest updates to database
    if form.validate_on_submit():
        try:
            guest.full_name = form.full_name.data
            guest.nickname = form.nickname.data
            guest.phone = form.phone.data
            guest.email = form.email.data
            guest.side = form.side.data
            guest.language = form.language.data
            guest.notes = form.notes.data
            db.session.commit()
            flash("Guest updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating guest: {str(e)}", "danger")
    return redirect(url_for("guests.guest_list"))


@guests_bp.route("/guests/<guest_id>/delete", methods=["POST"])
@login_required
def guest_delete(guest_id: str):
    """Delete a guest from the current user's wedding."""
    guest = get_guest_or_404(guest_id)
    try:
        db.session.delete(guest)
        db.session.commit()
        flash("Guest deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting guest: {str(e)}", "danger")
    return redirect(url_for("guests.guest_list"))


@guests_bp.route("/guests/<guest_id>/toggle-shared", methods=["POST"])
@login_required
def guest_toggle_shared(guest_id: str):
    """Toggle the invitation_shared status of a guest via HTMX."""
    guest = get_guest_or_404(guest_id)
    try:
        guest.invitation_shared = not guest.invitation_shared
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    base_url = current_app.config["BASE_URL"]
    return render_template("guests/_row.html", guest=guest, base_url=base_url)


IMPORT_COLUMNS = ["full_name", "nickname", "phone", "email", "side", "language", "notes"]
VALID_SIDES = {"bride", "groom"}
VALID_LANGUAGES = {"en", "km"}


@guests_bp.route("/guests/import-template")
@login_required
def guest_import_template():
    """Download a CSV template for guest import."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(IMPORT_COLUMNS)
    writer.writerow(["John Doe", "Johnny", "+855 12 345 678", "john@example.com", "bride", "en", "Family friend"])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="guest_import_template.csv",
    )


def _parse_csv(stream) -> list[dict]:
    """Parse a CSV file stream into a list of guest dicts."""
    text = stream.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        rows.append({col: (row.get(col) or "").strip() for col in IMPORT_COLUMNS})
    return rows


def _parse_xlsx(stream) -> list[dict]:
    """Parse an XLSX file stream into a list of guest dicts."""
    from openpyxl import load_workbook

    buf = io.BytesIO(stream.read())
    wb = load_workbook(buf, read_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)

    # Read header row
    header = [str(c or "").strip().lower() for c in next(rows_iter, [])]
    col_map = {}
    for col in IMPORT_COLUMNS:
        if col in header:
            col_map[col] = header.index(col)

    rows = []
    for row in rows_iter:
        guest = {}
        for col in IMPORT_COLUMNS:
            idx = col_map.get(col)
            guest[col] = str(row[idx] or "").strip() if idx is not None and idx < len(row) else ""
        rows.append(guest)
    wb.close()
    return rows


@guests_bp.route("/guests/import", methods=["POST"])
@login_required
def guest_import():
    """Import guests from an uploaded CSV or XLSX file."""
    wedding = get_wedding()
    if not wedding:
        flash("Please configure your wedding in Settings first.", "danger")
        return redirect(url_for("main.settings"))

    import_form = GuestImportForm()
    if not import_form.validate_on_submit():
        for field, errors in import_form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
        return redirect(url_for("guests.guest_list"))

    file = import_form.file.data
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            rows = _parse_csv(file.stream)
        elif filename.endswith(".xlsx"):
            rows = _parse_xlsx(file.stream)
        else:
            flash("Unsupported file type. Use .csv or .xlsx.", "danger")
            return redirect(url_for("guests.guest_list"))
    except Exception as e:
        flash(f"Error reading file: {str(e)}", "danger")
        return redirect(url_for("guests.guest_list"))

    if not rows:
        flash("The file is empty or has no data rows.", "danger")
        return redirect(url_for("guests.guest_list"))

    imported = 0
    skipped = 0
    for i, row in enumerate(rows, start=2):
        name = row.get("full_name", "").strip()
        if not name:
            skipped += 1
            continue

        side = row.get("side", "bride").lower()
        if side not in VALID_SIDES:
            side = "bride"

        lang = row.get("language", "en").lower()
        if lang not in VALID_LANGUAGES:
            lang = "en"

        guest = Guest(
            wedding_id=wedding.wedding_id,
            full_name=name,
            nickname=row.get("nickname", "") or None,
            phone=row.get("phone", "") or None,
            email=row.get("email", "") or None,
            side=side,
            language=lang,
            notes=row.get("notes", "") or None,
        )
        db.session.add(guest)
        imported += 1

    try:
        db.session.commit()
        flash(f"Imported {imported} guest(s) successfully! ({skipped} skipped — missing name.)", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving imported guests: {str(e)}", "danger")

    return redirect(url_for("guests.guest_list"))
