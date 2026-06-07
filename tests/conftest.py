import os
import sys
import pytest
from fastapi.testclient import TestClient
from app import oauth2, models
from app.database import get_db, Base
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:aldrich1028@localhost:5432/fastapi_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# scope define how long the fixture will be used
@pytest.fixture
def session():
    # drop before each test run, keep table if test fails.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    # yield allows us to run some code before and after the test function runs.
    yield TestClient(app)
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    user_data = {"email": "qianzhiyuan@gmail.com",
                 "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "test2@gmail.com",
                 "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return oauth2.create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    post_data = [
        {"title": "first title", "content": "first content", "owner_id": test_user["id"]},
        {"title": "second title", "content": "second content", "owner_id": test_user["id"]},
        {"title": "third title", "content": "third content", "owner_id": test_user["id"]},
        {"title": "fourth title", "content": "fourth content", "owner_id": test_user2["id"]}, 
    ]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, post_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()

    # session.add_all([
    #     models.Post(title="first title", content="first content", owner_id=test_user["id"]),
    #     models.Post(title="second title", content="second content", owner_id=test_user["id"]),
    #     models.Post(title="third title", content="third content", owner_id=test_user["id"]),
    # ])
    # session.commit()

    posts = session.query(models.Post).all()
    return posts