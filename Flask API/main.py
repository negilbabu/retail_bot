import os
from dotenv import load_dotenv
from app import create_app, db
from flask_migrate import Migrate


# Load .env from root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")
