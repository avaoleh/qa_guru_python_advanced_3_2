import pytest
import dotenv
import os
import requests
import json
import random
from http import HTTPStatus
from faker import Faker


faker = Faker()
AUTOTEST_PREFIX = "qaguru.autotest"

@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(scope="session", autouse=True)
def generate_users(app_url: str) -> list[int]:
    """Генерация пользователей для сессии с тестами и удаление"""

    with open("../users.json", "r", encoding="utf-8") as f:
        test_users = json.load(f)
    api_users = []
    for user in test_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    clear_users_in_db(app_url)

@pytest.fixture(scope="function")
def create_user(app_url: str, generate_user_data: dict[str, str]) -> dict:
    """Создание пользователя для теста"""

    response = requests.post(f"{app_url}/api/users/", json=generate_user_data)
    assert response.status_code == HTTPStatus.CREATED

    yield response.json()


@pytest.fixture
def users(app_url: str):
    """Получение пользователей"""
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]


def clear_users_in_db(app_url: str) -> None:
    """Удаление всех сгенерированных пользователей из БД после прогона"""
    response = requests.get(f"{app_url}/api/users/", params={"page": 1, "size": 100})
    users = response.json()["items"]

    generated_users = [user for user in users if AUTOTEST_PREFIX in user["email"]]

    for user in generated_users:
        requests.delete(f"{app_url}/api/users/{user['id']}")


@pytest.fixture
def generate_user_data() -> dict[str, str]:
    """Генерация данных для тестового юзера"""
    email = faker.email(domain=f"{AUTOTEST_PREFIX}")
    first_name = faker.first_name()
    last_name = faker.last_name()
    avatar = f"https://reqres.in/img/faces/{AUTOTEST_PREFIX}{random.randint(0, 100)}-image.jpg"


    user_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "avatar": avatar
    }
    return user_data