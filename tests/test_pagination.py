import pytest
from app.models.User import User
import requests
from http import HTTPStatus

@pytest.mark.pagination
class TestPagination:
    @pytest.mark.parametrize("page,size", [
        (1, 5),
        (2, 5),
        (3, 5),
        (1, 1)
    ])
    def test_pagination_data(self, app_url: str, page: int, size: int):
        """Проверка наличие элементов: total, pages, size"""
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        assert response.status_code == HTTPStatus.OK

        data = response.json()
        items = data["items"]

        expected_count = len(items)

        assert len(items) == expected_count
        assert data["page"] == page
        assert data["size"] == size
        assert "total" in data
        assert "pages" in data
        assert "size" in data

        for item in items:
            User.model_validate(item)

    @pytest.mark.parametrize("size", [2, 5, 10])
    def test_total_pages(self, app_url: str, size: int):
        """Проверка общее количество страниц """
        response = requests.get(f"{app_url}/api/users/?size={size}")
        assert response.status_code == HTTPStatus.OK

        data = response.json()
        total_items = data["total"]
        expected_pages = (total_items + size - 1) // size

        assert data["pages"] == expected_pages

    def test_unique_ids(self, app_url: str):
        """Проверка уникальности по id """
        response1 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        assert response1.status_code == HTTPStatus.OK
        page1 = response1.json()["items"]

        response2 = requests.get(f"{app_url}/api/users/?page=2&size=5")
        assert response2.status_code == HTTPStatus.OK
        page2 = response2.json()["items"]

        ids_page1 = {user["id"] for user in page1}
        ids_page2 = {user["id"] for user in page2}

        assert ids_page1.isdisjoint(ids_page2)