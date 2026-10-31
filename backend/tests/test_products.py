from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_products_requires_auth():
    response = client.get("/api/v1/products/")
    assert response.status_code == 403


def test_list_plans_requires_auth():
    response = client.get("/api/v1/plans/")
    assert response.status_code == 403
