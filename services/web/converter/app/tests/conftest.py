import pytest
from app import create_app, db
from app.models import User, Record


@pytest.fixture()
def app():
    app = create_app('config.TestingConfig')

    with app.app_context():
        db.create_all()

        yield app

        db.drop_all()


@pytest.fixture()
def client(app):
    with app.app_context():
        yield app.test_client()


@pytest.fixture()
def init_db(client):
    db.create_all()

    _, exp = User.get_token()
    user1 = User(id='1111', name='User1', token='token1', token_expiration=exp)
    user2 = User(id='2222', name='User2', token='token2', token_expiration=exp)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    yield

    db.drop_all()
