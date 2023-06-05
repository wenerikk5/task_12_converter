import os
from config import BASE_DIR


def test_config(app):
    assert app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == \
           f"sqlite:///{os.path.join(BASE_DIR, 'db_test.sqlite3')}"