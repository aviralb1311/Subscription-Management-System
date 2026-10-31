from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_customers_requires_auth():
    response = client.get("/api/v1/customers/")
    assert response.status_code == 403


def test_list_quotations_requires_auth():
    response = client.get("/api/v1/quotations/")
    assert response.status_code == 403


def test_quote_requires_plan_version():
    # This would need auth setup in full test
    pass
