# Wedding Management Dashboard

A beautiful, full-featured wedding management dashboard for organizing guests, sharing invitations, and managing check-ins on the big day.


## Features

- **Dashboard** — Real-time overview of guest counts, invitation status, check-in progress, and gift totals with live Chart.js charts
- **Guest Management** — Full CRUD for guests with live HTMX search, filtering, and one-click invitation link sharing
- **Check-In System** — Tablet-optimized interface for checking in guests and recording gifts on event day
- **Public Invitation Cards** — Beautiful, responsive invitation pages for each guest with bilingual support (English + Khmer)
- **Wedding Settings** — Configure all wedding details including bilingual couple names, venue info, and welcome messages
- **Live Updates** — Dashboard auto-refreshes every 30 seconds via HTMX polling
- **Bilingual Support** — Full English and Khmer language support for invitation cards

## Tech Stack

- **Backend:** Python 3.11+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate
- **Database:** SQLite (single file)
- **Frontend:** Server-rendered Jinja2 templates, HTMX, Tailwind CSS (CDN), Chart.js (CDN)
- **Fonts:** Cormorant Garamond (headings), Inter (UI), Noto Sans Khmer (Khmer text)

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

### 1. Clone the repository

```bash
git clone <https://github.com/suningun/wedding-invitation.gitl>
cd wedding-invitation
```

### 2. Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` in your editor and update the values (see Environment Variables section below).

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `FLASK_APP` | Entry point for Flask | `run.py` |
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Secret key for session encryption. **Change this to a random string!** | `my-super-secret-key-123` |
| `DATABASE_URL` | SQLite database path | `sqlite:///wedding.db` |
| `ORGANIZER_USERNAME` | Login username for the organizer | `admin` |
| `ORGANIZER_PASSWORD` | Login password for the organizer. **Change this!** | `my-secure-password` |
| `BASE_URL` | Base URL for generating invitation links | `http://localhost:5000` |

## Database Setup

Initialize and create the database:

```bash
# Initialize the migrations directory
flask db init

# Generate the initial migration
flask db migrate -m "initial"

# Apply the migration to create tables
flask db upgrade
```

If you change the models later, run `flask db migrate` and `flask db upgrade` again to update the schema.

## First-Time Setup

1. Start the app (see Running section below)
2. Open `http://localhost:5000` in your browser
3. Log in with the username and password from your `.env` file
4. Go to **Settings** and fill in your wedding details (date, couple names, venue, etc.)
5. You're ready to start adding guests!

## Running the App

```bash
python run.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

The app will run on `0.0.0.0:5000` and be accessible via localhost, 127.0.0.1, or any other IP address on your machine.

## Usage Guide

### Step 1: Configure Your Wedding
Go to **Settings** and fill in all the wedding details. Enter both English and Khmer text for bilingual invitations.

### Step 2: Add Guests
Go to **Guests** and click "Add Guest" to add each guest. Set their preferred language (English or Khmer) — this determines which version of the invitation they see.

### Step 3: Share Invitations
For each guest, click the clipboard icon to copy their unique invitation link. Share it via messaging app, email, or however you prefer. Click "Not Shared" to mark it as shared once you've sent it.

### Step 4: Event Day Check-In
On the wedding day, open the **Check-In** page on a tablet. Search for arriving guests, tap their name, enter their gift amount, and check them in. The dashboard updates in real-time.

### Step 5: Monitor the Dashboard
Keep the **Dashboard** open on a screen to see live stats — total check-ins, gift totals, and recent arrivals.

## Project Structure

```
wedding-mvp/
├── app/
│   ├── __init__.py              # Flask app factory, extensions
│   ├── models.py                # SQLAlchemy models (WeddingEvent, Guest)
│   ├── forms.py                 # Flask-WTF form classes
│   ├── utils.py                 # Helper functions (get_lang_value)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Login / logout
│   │   ├── main.py              # Dashboard, settings
│   │   ├── guests.py            # Guest CRUD + HTMX endpoints
│   │   ├── checkin.py           # Check-in page + actions
│   │   └── invitation.py        # Public /invite/<token> page
│   ├── templates/
│   │   ├── base.html            # Main layout with navigation
│   │   ├── login.html           # Login page
│   │   ├── dashboard.html       # Dashboard page
│   │   ├── dashboard_stats.html # HTMX partial for live stats
│   │   ├── settings.html        # Wedding settings form
│   │   ├── guests/
│   │   │   ├── list.html        # Guest list page
│   │   │   ├── _row.html        # Single guest table row (HTMX)
│   │   │   ├── _rows.html       # Multiple guest rows (search)
│   │   │   └── _form.html       # Edit guest form (modal)
│   │   ├── checkin/
│   │   │   ├── index.html       # Check-in page
│   │   │   ├── _results.html    # Search results (HTMX)
│   │   │   └── _modal.html      # Check-in modal (HTMX)
│   │   └── invitation.html      # Public invitation card
│   └── static/
│       └── css/
│           └── custom.css       # Custom styles
├── migrations/                  # Flask-Migrate auto-generated
├── instance/                    # SQLite database (gitignored)
├── .env.example                 # Environment variable template
├── .gitignore
├── requirements.txt
├── run.py                       # Entry point
└── README.md
```

## Deployment

### Railway

1. Push your code to a GitHub repository
2. Connect the repo to [Railway](https://railway.app)
3. Set the environment variables in Railway's dashboard
4. Set the start command to: `gunicorn run:app`
5. Add `gunicorn` to your `requirements.txt`

### Render

1. Push your code to a GitHub repository
2. Create a new Web Service on [Render](https://render.com)
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `gunicorn run:app`
5. Add environment variables in the Render dashboard

For production, change `DATABASE_URL` to a PostgreSQL connection string and update SQLAlchemy accordingly.

## Troubleshooting

### Khmer font not rendering
Make sure you have an internet connection — Noto Sans Khmer is loaded from Google Fonts CDN. If deploying offline, download the font files and serve them locally.

### Database locked
SQLite can lock if multiple processes write simultaneously. Ensure only one Flask process is running. For production with concurrent users, consider switching to PostgreSQL.

### Port already in use
If port 5000 is occupied, run on a different port:
```bash
flask run --port 5001
```

### Migration errors
If you get migration errors, you can reset the database:
```bash
rm -rf migrations/ instance/wedding.db
flask db init
flask db migrate -m "initial"
flask db upgrade
```

## License

MIT
