from http import HTTPStatus
import pytest
import requests

from app.models.User import User
from tests.conftest import AUTOTEST_PREFIX


class TestUsers:

    def test_get_users(self, app_url: str):
        """Проверка получения юзеров"""
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK

        for user in response.json()["items"]:
            User.model_validate(user)

    def test_users_no_duplicates(self, users: list[User]):
        """Проверка, что среди юзеров нет дублей"""
        users_ids = [user["id"] for user in users]
        assert len(users_ids) == len(set(users_ids))

    def test_get_user_by_id(self, app_url: str, generate_users: list[int]):
        """Проверка получения юзера с существующим user_id"""
        response = requests.get(f"{app_url}/api/users/{generate_users[0]}")
        assert response.status_code == HTTPStatus.OK

        user = response.json()
        User.model_validate(user)

    def test_get_user_by_unexisted_id(self, app_url: str, generate_users: list[int]):
        """Проверка получения юзера с несуществующим user_id"""
        unexisted_id = generate_users[-1] + 1
        response = requests.get(f"{app_url}/api/users/{unexisted_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "asd", [3], None])
    def test_get_user_with_invalid_id(self, app_url: str, user_id):
        """Проверка получения юзера с невалидным user_id"""
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

class TestUsers_CRUD:
    def test_create_user(self, app_url: str, generate_user_data: dict[str, str]):
        """Проверка создания юзера"""
        response = requests.post(f"{app_url}/api/users/", json=generate_user_data)
        assert response.status_code == HTTPStatus.CREATED

        user = response.json()
        User.model_validate(user)
        del user['id']
        assert generate_user_data == user

    def test_delete_user(self, app_url: str, create_user: dict):
        """Проверка удаления юзера"""
        response = requests.delete(f"{app_url}/api/users/{create_user['id']}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["message"] == "User deleted"
        assert requests.get(f'{app_url}/api/users/{create_user['id']}').status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_data", [
        {
            "email": f"test_email@{AUTOTEST_PREFIX}.com",
        },
        {
            "first_name": "test first name"
        },
        {
            "last_name": "last last name"
        },
        {
            "avatar": "https://reqres.in/img/faces/unique-avatar-1.jpg"
        },
        {
            "email": f"autotest_emailUpdate@{AUTOTEST_PREFIX}.com",
            "first_name": "firstnameUpdate",
            "last_name": "lastnameUpdate",
            "avatar": "https://reqres.in/img/faces/unique-avatar-0.jpg"
        }
    ])
    def test_update_user(self, app_url: str, user_data: dict, create_user: dict):
        """Проверка обновления данных юзера"""

        response = requests.patch(f"{app_url}/api/users/{create_user['id']}", json=user_data)
        assert response.status_code == HTTPStatus.OK
        updated_user = response.json()
        User.model_validate(updated_user)

        assert create_user['id'] == updated_user['id']
        for key in user_data.keys():
            assert create_user[key] != updated_user[key]

    def test_create_not_valid_user(self, app_url: str):
        """Создание пользователя с невалидными данными"""
        response = requests.post(f"{app_url}/api/users", json={'name': 'Alisa', 'job': 'ai-agent'})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('user_id', (0, -1))
    def test_delete_with_not_valid_user_id(self, app_url: str, user_id: int):
        """Удаление пользователя с невалидным id"""
        delete_response = requests.delete(f"{app_url}/api/users/{user_id}")
        assert delete_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY