"""Flask-WTF forms for the Wedding Management Dashboard."""

from wtforms import (
    StringField,
    PasswordField,
    DateField,
    TimeField,
    SelectField,
    TextAreaField,
    DecimalField,
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
    Email,
    EqualTo,
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


TEMPLATE_CHOICES = [
    ("classic", "Classic Elegance"),
]


# Organizer login form with username & password validation
class LoginForm(FlaskForm):
    """Login form for organizers."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


# New organizer registration with email & password confirmation
class RegisterForm(FlaskForm):
    """Registration form for new organizers."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=200)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )


# Organizer configures wedding details (bilingual: English & Khmer)
class WeddingSettingsForm(FlaskForm):
    """Form for configuring the wedding event details."""

    template = SelectField(
        "Invitation Template", choices=TEMPLATE_CHOICES, default="classic"
    )

    wedding_date = DateField("Wedding Date", validators=[Optional()])
    ceremony_time = TimeField("Ceremony Time", validators=[Optional()])
    reception_time = TimeField("Reception Time", validators=[Optional()])
    venue_map_url = StringField(
        "Google Maps URL", validators=[Optional(), Length(max=500)]
    )
    organizer_phone = StringField(
        "Organizer Phone", validators=[Optional(), Length(max=50)]
    )

    bride_name_en = StringField(
        "Bride Name (English)", validators=[Optional(), Length(max=200)]
    )
    bride_name_km = StringField(
        "Bride Name (Khmer)", validators=[Optional(), Length(max=200)]
    )
    groom_name_en = StringField(
        "Groom Name (English)", validators=[Optional(), Length(max=200)]
    )
    groom_name_km = StringField(
        "Groom Name (Khmer)", validators=[Optional(), Length(max=200)]
    )
    venue_name_en = StringField(
        "Venue Name (English)", validators=[Optional(), Length(max=200)]
    )
    venue_name_km = StringField(
        "Venue Name (Khmer)", validators=[Optional(), Length(max=200)]
    )
    venue_address_en = StringField(
        "Venue Address (English)", validators=[Optional(), Length(max=500)]
    )
    venue_address_km = StringField(
        "Venue Address (Khmer)", validators=[Optional(), Length(max=500)]
    )
    welcome_message_en = TextAreaField(
        "Welcome Message (English)", validators=[Optional(), Length(max=2000)]
    )
    welcome_message_km = TextAreaField(
        "Welcome Message (Khmer)", validators=[Optional(), Length(max=2000)]
    )


# Add or edit guest information (name, phone, side, language)
class GuestForm(FlaskForm):
    """Form for adding or editing a guest."""

    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=200)])
    nickname = StringField("Nickname", validators=[Optional(), Length(max=100)])
    phone = StringField("Phone", validators=[Optional(), Length(max=50)])
    email = StringField("Email", validators=[Optional(), Length(max=200)])
    side = SelectField("Side", choices=[("bride", "Bride"), ("groom", "Groom")])
    language = SelectField("Language", choices=[("en", "English"), ("km", "Khmer")])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])


# Record guest arrival & gift details (amount, currency, note)
class CheckInForm(FlaskForm):
    """Form for checking in a guest and recording their gift."""

    gift_amount = DecimalField(
        "Gift Amount", validators=[Optional(), NumberRange(min=0)], default=0
    )
    gift_currency = SelectField(
        "Currency", choices=[("USD", "USD"), ("KHR", "KHR")], default="USD"
    )
    gift_note = TextAreaField("Gift Note", validators=[Optional(), Length(max=500)])


# Bulk import guests from CSV or Excel file
class GuestImportForm(FlaskForm):
    """Form for importing guests from a CSV or Excel file."""

    file = FileField(
        "Guest File",
        validators=[
            FileRequired(),
            FileAllowed(["csv", "xlsx"], "Only .csv and .xlsx files are allowed."),
        ],
    )
