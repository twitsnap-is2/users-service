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
    yield
    db.clear_table()
    #db.drop_table()

def test_create_user(setup):
    response = client.post("/users", json={"username":"Sofia", "password": "hola1234", "mail":"sofia@hotmail.com"})
    assert response.status_code == 201
    assert response.json() == "User created successfully"

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

