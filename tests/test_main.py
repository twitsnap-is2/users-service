from fastapi.testclient import TestClient
import pytest
from src.main import app 
from loguru import logger
#from src.routers.routers import router
from database.db import Database
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase, FollowerAccountBase, FollowResponse
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

def test_get_email_existence(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    email = response_post.json()["email"]
    response_get = client.get(f"/users/{email}/email/exists")
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data["exists"] == True

def test_get_email_existence_incorrect(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    email = "s@hotmail.com"
    response_get = client.get(f"/users/{email}/email/exists")
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data["exists"] == False

def test_get_users_authors_info(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    response_post3 = client.post("/users/temp", json={"username":"sofisofi1", "name":"Sofiia", "email":"sofiiaa@gmail.com", "password": "hola123456"})

    user_id = response_post.json()["id"]
    authors = [response_post2.json()["username"], response_post3.json()["username"]]

    response_get = client.get(f"/users/{user_id}/authorsUsernames/", params={"authors": authors})
    
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data[0]["username"] == "sofisofia"
    assert response_data[1]["username"] == "sofisofi1"

def test_get_users_authors_info_not_found(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})

    user_id = response_post.json()["id"]
    authors = ["sofisofia"]

    response_get = client.get(f"/users/{user_id}/authorsUsernames/", params={"authors": authors})
    assert response_get.status_code == 404
    response_expected = {
        "type": "https://httpstatuses.com/404",
        "title": "Users not found",
        "status": 404,
        "detail": "None of the users were found",
        "instance": "/users/{user_id}/authors_id/{authors_id}",
        "errors": None
    }

def test_get_authors_info_with_only_one_valid_author(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})

    user_id = response_post.json()["id"]
    authors = [response_post2.json()["username"], "sofisofi1"]

    response_get = client.get(f"/users/{user_id}/authorsUsernames/", params={"authors": authors})

    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data[0]["username"] == "sofisofia"    

def test_search_users(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    response_post3 = client.post("/users/temp", json={"username":"sofisofi1", "name":"Sofiia", "email":"sofiiaa@gmail.com", "password": "hola123456"})

    response_get = client.get("/users/search/", params={"username": "sofisofi"})
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data[0]["username"] == "sofisofi"

def test_search_users_not_found(setup):
    response_get = client.get("/users/search/", params={"username": "sofisofi"})
    print(f"RESPONSE: {response_get.json()}")
    assert response_get.status_code == 404
    response_expected = {
        "type": "https://httpstatuses.com/404",
        "title": "Users not found",
        "status": 404,
        "detail": "None of the users were found",
        "instance": "/users/search/",
        "errors": None
    }

    assert response_get.json() == response_expected

def test_search_user_with_starting_name(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    response_post3 = client.post("/users/temp", json={"username":"sofisofi1", "name":"Sofiia", "email":"sofiiaa@gmail.com", "password": "hola123456"})

    response_get = client.get("/users/search/", params={"username": "sofisof"})
    
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data[0]["username"] == "sofisofi"
    assert response_data[1]["username"] == "sofisofia"
    assert response_data[2]["username"] == "sofisofi1"

def test_follow_user(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    
    user_id = response_post.json()["id"]
    followed_user_name = response_post2.json()["username"]
    followed_user_id = response_post2.json()["id"]
    follower_data = FollowerAccountBase(user_id=user_id)

    response_post = client.post(f"/users/follow/{followed_user_id}/", json=follower_data.model_dump())
    assert response_post.status_code == 201
    response_data = response_post.json()
    assert response_data["follower_id"] == user_id
    assert response_data["followed_id"] == followed_user_id

def test_follow_user_already_followed(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    
    user_id = response_post.json()["id"]
    followed_user_name = response_post2.json()["username"]
    followed_user_id = response_post2.json()["id"]
    followed_username = response_post2.json()["username"]
    follower_data = FollowerAccountBase(user_id=user_id)

    response = client.post(f"/users/follow/{followed_user_id}/", json=follower_data.model_dump())
    assert response.status_code == 201
    response2 = client.post(f"/users/follow/{followed_user_id}/", json=follower_data.model_dump())
    assert response2.status_code == 404
    response_expected = {
        "type": "https://httpstatuses.com/404",
        "title": "User not found or you are already following",
        "status": 404,
        "detail": "User not found or already following",
        "instance": f"/users/follow/{followed_user_id}/",
        "errors": None
    }
    assert response2.json() == response_expected

def test_unfollow_user(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    
    user_id = response_post.json()["id"]
    followed_user_name = response_post2.json()["username"]
    followed_user_id = response_post2.json()["id"]
    follower_data = FollowerAccountBase(user_id=user_id)

    response = client.post(f"/users/follow/{followed_user_id}/", json=follower_data.model_dump())
    assert response.status_code == 201

    response2 = client.request(
            method="DELETE",
            url=f"/users/unfollow/{followed_user_id}/",
            json=follower_data.model_dump()  
        )

    assert response2.status_code == 204

def test_unfollow_user_not_followed(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    
    user_id = response_post.json()["id"]
    followed_user_name = response_post2.json()["username"]
    followed_user_id = response_post2.json()["id"]
    follower_data = FollowerAccountBase(user_id=user_id)

    response2 = client.request(
            method="DELETE",
            url=f"/users/unfollow/{followed_user_id}/",
            json=follower_data.model_dump() 
        )

    assert response2.status_code == 404
    
    response_expected = {
        "type": "https://httpstatuses.com/404",
        "title": "User not found or you are not following",
        "status": 404,
        "detail": "User not found or not following",
        "instance": f"/users/unfollow/{followed_user_id}/",
        "errors": None
    }

    assert response2.json() == response_expected

def test_get_followers(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})

    user_id = response_post.json()["id"]
    followed_user_name = response_post2.json()["username"]
    followed_user_id = response_post2.json()["id"]
    follower_data = FollowerAccountBase(user_id=user_id)

    response = client.post(f"/users/follow/{followed_user_id}/", json=follower_data.model_dump())
    assert response.status_code == 201

    response_get = client.get(f"/users/followers/{followed_user_id}/")
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data[0]["username"] == "sofisofi"

def test_get_followers_not_found(setup):

    response_get = client.get("/users/followers/non-existent-id/")
    assert response_get.status_code == 404

    assert response_get.json()['status'] == 404
    assert response_get.json()['title'] == "User not found"
    assert response_get.json()['type'] == "https://httpstatuses.com/404"
    assert response_get.json()['errors'] == None

def test_get_following(setup):
    response_post = client.post("/users/temp", json={"username":"sofisofi", "name":"Sofia", "email":"sofia@gmail.com", "password": "hola1234"})
    response_post2 = client.post("/users/temp", json={"username":"sofisofia", "name":"Sofii", "email":"sofiia@gmail.com", "password": "hola12345"})
    
    user_id = response_post.json()["id"]
    followed_user_name = response_post2.json()["username"]
    followed_user_id = response_post2.json()["id"]
    follower_data = FollowerAccountBase(user_id=user_id)

    response = client.post(f"/users/follow/{followed_user_id}/", json=follower_data.model_dump())

    response_get = client.get(f"/users/following/{follower_data.user_id}/")
    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data[0]["username"] == "sofisofia"

def test_get_following_not_found(setup):
    response_get = client.get("/users/following/non-existent-id/")
    assert response_get.status_code == 404
    response_expected = {
        "type": "https://httpstatuses.com/404",
        "title": "User not found",
        "status": 404,
        "detail": "User not found",
        "instance": "/users/following/non-existent-id/",
        "errors": None
    }

    assert response_get.json() == response_expected

def test_get_near_users(setup):
    response_post1 = client.post("/users/temp", json={"username":"user1", "name":"User One", "email":"user1@gmail.com", "password":"password1"})
    response_post2 = client.post("/users/temp", json={"username":"user2", "name":"User Two", "email":"user2@gmail.com", "password":"password2"})
    response_post3 = client.post("/users/temp", json={"username":"user3", "name":"User Three", "email":"user3@gmail.com", "password":"password3"})

    user_id1 = response_post1.json()["id"]
    user_id2 = response_post2.json()["id"]
    user_id3 = response_post3.json()["id"] 

    client.put(f"/users/{user_id1}", json={"supabase_id": user_id1, "birthdate": "", "locationLat": -34.6274, "locationLong": -58.4431, "profilePic": ""}) 
    client.put(f"/users/{user_id2}", json={"supabase_id": user_id2, "birthdate": "", "locationLat": -34.6274, "locationLong": -58.4424, "profilePic": ""})  
    client.put(f"/users/{user_id3}", json={"supabase_id": user_id3, "birthdate": "", "locationLat": 34.0522, "locationLong": -118.2437, "profilePic": ""})  


    response_get = client.get(f"/users/near/{user_id1}/")

    assert response_get.status_code == 200
    response_data = response_get.json()
    assert len(response_data) == 1
    assert response_data[0]["username"] == "user2"

def test_get_users_with_common_interests(setup):
    response_post1 = client.post("/users/temp", json={"username":"user1", "name":"User One", "email":"user1@gmail.com", "password":"password1"})
    response_post2 = client.post("/users/temp", json={"username":"user2", "name":"User Two", "email":"user2@gmail.com", "password":"password2"})
    response_post3 = client.post("/users/temp", json={"username":"user3", "name":"User Three", "email":"user3@gmail.com", "password":"password3"})

    user_id1 = response_post1.json()["id"]
    user_id2 = response_post2.json()["id"]
    user_id3 = response_post3.json()["id"]

    client.put(f"/users/{user_id1}", json={"supabase_id": user_id1, "birthdate": "", "locationLat": -34.6274, "locationLong": -58.4431, "profilePic": ""}) 
    client.put(f"/users/{user_id2}", json={"supabase_id": user_id2, "birthdate": "", "locationLat": -34.6274, "locationLong": -58.4424, "profilePic": ""})  
    client.put(f"/users/{user_id3}", json={"supabase_id": user_id3, "birthdate": "", "locationLat": 34.0522, "locationLong": -118.2437, "profilePic": ""})  

    client.put(f"/users/edit/{user_id1}", json={"interests": ",music,reading,"})
    client.put(f"/users/edit/{user_id2}", json={"interests": ",music,sports,"})
    client.put(f"/users/edit/{user_id3}", json={"interests": ",travel,reading,"})

    response_get = client.get(f"/users/common-interests/{user_id1}/")

    logger.info(f"Response status: {response_get.status_code}")
    logger.info(f"Response data: {response_get.json()}")

    assert response_get.status_code == 200
    response_data = response_get.json()
    assert len(response_data) == 2
    assert response_data[0]["username"] in ["user2", "user3"]
    assert response_data[1]["username"] in ["user2", "user3"]