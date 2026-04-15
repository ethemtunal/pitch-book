from adapters.document_stores.document_db.document_store import seed_db
from api.app import create_app

app = create_app()
seed_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
