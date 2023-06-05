from app import db
from app.models import User, Record


def test_new_user(init_db):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check user is added, name and id in instance
    """
    token, exp = User.get_token()
    user = User(
        id='3333',
        name='User3',
        token=token,
        token_expiration=exp)
    db.session.add(user)
    db.session.commit()

    assert db.session.query(User).count() == 3
    assert user.name == 'User3'
    assert user.id != '1111'
