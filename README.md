# Twitsnap's User Service

## Table of Content

1. [Introduction](#introduction)
2. [Run the Project](#run-the-project)
3. [Technologies](#technologies)
4. [Testing](#testing)

## Introduction

This repository contains the **User Service** for the Twitsnap application. This service is responsible for all the users data. All requests that interact and are related to users are in this service such as creation, modification or deletion as needed and many more.

## Run the Project

To run the project using **Docker** follow this steps:

1. Create a `.env` file in the root directory of the project with the following content:

   (`.env.example` is provided as a template)

   ```env
    SERVICES_API_PORT = "5000"
    POSTGRES_USER = "user"
    POSTGRES_PASSWORD = "password"
    POSTGRES_DB = "dbname"
    POSTGRES_PORT = "5432"
    POSTGRES_HOST = "container-name"
   ```
    Replace the variables with the right information for connection of the service.
   
2. Build the Image:

   ```
   docker-compose -f docker-compose.yml up --build
   ```
   
3. Run the service: 

   ```
   docker-compose up
   ```

   This should run both services included such as the API and the DB (Postgres).

## OpenAPI Documentation

The User Service is fully documented using the OpenAPI standard. You can explore the API's functionality and available endpoints via Swagger UI at the following URL:

`http://localhost:<port>/docs`

_Make sure to replace `<port>` with the port number specified in your .env configuration file._

## Technologies


This service is developed in Python, the requirements and technologies used for correct functionality are:

* FastAPI: Framework to build the API (Python)
* Uvicorn: Requirement for FastAPI, async server ASGI
* Pydantic: Data validation for different models and schemas created in service
* Loguru: Logs for following the service functionality
* SQLAlchemy: ORM (Object-Realtional Mapping) for Python. Helps with the interaction between the program and the Database (in this case Postgres is being used)
* Psycopg2-binary: Makes the connection between the service and the database of PostgreSQL


## Testing


This service is in continuos development and for that it is being testes everytime a new feature is added. This services is provided with automated tests which can also be run with **Docker**:

There are some requirements that are being used for making the tests:

* Httpx: For making HTTP Requests
* Pytest: Tool for running the tests

  For running the tests:

  ```
  docker-compose -f docker-compose-tests.yml up --build
   ```

