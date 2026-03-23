"""Entry point for the Wedding Management Dashboard."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
