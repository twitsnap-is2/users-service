from fastapi.testclient import TestClient
import pytest
from src.main import app 
from loguru import logger
#from src.routers.routers import router
from database.db import Database
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase
import os

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
    response = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["username"] == "sofisofi"
    assert response_data["name"] == "Sofia"
    assert response_data["email"] == "sofia@gmail.com"

def test_collect_users(setup):
    response_post1 = client.post("/users/temp", json={"username":"sofisofi1", "name":"Sofia", "email":"sofia1@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofi2", "name":"Sofia", "email":"sofia2@gmail.com", "password": "hola1234"})

    response_get = client.get("/users")
    response_data = response_get.json()
    first_user = response_data[0]
    second_user = response_data[1]
    assert response_get.status_code == 200
    assert first_user["username"] == "sofisofi1"
    assert first_user["email"] == "sofia1@gmail.com"
    assert first_user["name"] == "Sofia"
    assert second_user["username"] == "sofisofi2"
    assert second_user["email"] == "sofia2@gmail.com"
    assert second_user["name"] == "Sofia"


def test_get_user(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    user_id = response_post.json()["id"]
    response_get = client.get(f"/users/{user_id}")
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data["username"] == "sofisofi"
    assert response_data["name"] == "Sofia"
    assert response_data["email"] == "sofia@gmail.com"

def test_create_user_no_username(setup):
    response = client.post("/users/temp", json={"username":"", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    assert response.status_code == 400
    response_expected = {
        "type": "about:blank",
        "title": "Bad Request",
        "status": 400,
        "detail": "Error inserting user",
        "instance": "/users/temp",
        "errors": None
    }
    
    assert response.json() == response_expected


def test_create_more_than_one_user_with_same_username(setup):
    response_post1 = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia1", "email":"sofia1@gmail.com", "password": "hola12341"})
    assert response_post1.status_code == 201
    assert response_post2.status_code == 400
    response_expected = {
        "type": "https://httpstatuses.com/400",
        "title": "Bad Request",
        "status": 400,
        "detail": "User already exists",
        "instance": "/users/temp",
        "errors": {"username": "User already exists"}
    }

    assert response_post2.json() == response_expected


def test_create_more_than_one_user_with_same_email(setup):
    response_post1 = client.post("/users/temp", json={"username":"sofisofi1", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234", "birthdate":"2001-01-01", "location":"Argentina"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofi2", "name":"Sofia1", "email":"sofia@gmail.com", "password": "hola12341", "birthdate":"2002-01-01", "location":"Australia"})
    assert response_post1.status_code == 201
    assert response_post2.status_code == 400
    response_expected = {
        "type": "https://httpstatuses.com/400",
        "title": "Bad Request",
        "status": 400,
        "detail": "Email already exists",
        "instance": "/users/temp",
        "errors": {"email": "Email already exists"}
    }

    assert response_post2.json() == response_expected

def test_create_user_with_invalid_schema(setup):
    response1 = client.post("/users/temp", json={"name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response2 = client.post("/users/temp", json={"username":"sofisofi1", "email":"sofia@gmail.com", "password": "hola1234"})
    response3 = client.post("/users/temp", json={"username":"sofisofi2", "name":"Sofia1", "password": "hola12341"})

    assert response1.status_code == 422
    assert response2.status_code == 422
    assert response3.status_code == 422


    response_expected = {
        "type": "about:blank",
        "title": "Validation Error",
        "status": 422,
        "detail": "JSON decode error",
        "instance": "/users/temp",
        "errors": None
    }
    assert response1.json() == response_expected
    assert response2.json() == response_expected
    assert response3.json() == response_expected

def test_get_user_not_found(setup):
    response = client.get("/users/hola/email")
    assert response.status_code == 404
    response_expected = {
        "type": "https://httpstatuses.com/404",
        "title": "User not found",
        "status": 404,
        "detail": "User not found",
        "instance": "/users/hola/email",
        "errors": {"email": "email not found"}
    }

    assert response.json() == response_expected