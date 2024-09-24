from fastapi.testclient import TestClient
import pytest
from src.main import app 
#from src.routers.routers import router
from database.db import Database
from utils.engine import get_engine

client = TestClient(app)

@pytest.fixture(scope="function")
def setup():
    db = Database(get_engine())
    db.create_table()
    db.clear_table()
    yield db
    db.clear_table()
    db.drop_table()

def test_create_user(setup):
    response = client.post("/users", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234", "birthdate":"2001-01-01", "location":"Argentina"})
    assert response.status_code == 201
    response_expected = {
        "username": "sofisofi",
        "name": "Sofia",
        "email": "sofia@gmail.com",
    }
    #assert 
    #assert response.json() == "User created successfully"

# def test_create_user_no_username(setup):
#     response = client.post("/users", json={"username":"", "password":"hola1234", "mail":"hola@gmail.com"})
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Error inserting user"}

#     response_expected = {
#         "type": "about:blank",
#         "title": "Bad Request",
#         "status": 400,
#         "detail": "Error inserting user",
#         "instance": "/users",
#     }

#     assert response.json() == response_expected

