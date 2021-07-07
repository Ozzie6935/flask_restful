from webapp.app import create_app
from webapp.extensions import db


if __name__ == '__main__':
    app = create_app()
    db.app = create_app()
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8080)
