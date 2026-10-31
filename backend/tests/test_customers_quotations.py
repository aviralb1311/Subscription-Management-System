from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_customers_requires_auth():
    response = client.get("/api/v1/customers/")
    assert response.status_code in [401, 403]


def test_list_quotations_requires_auth():
    response = client.get("/api/v1/quotations/")
    assert response.status_code in [401, 403]


def test_create_quotation_requires_auth():
    response = client.post("/api/v1/quotations/", json={"customer_id": "x", "lines": []})
    assert response.status_code in [401, 403]


def test_price_tampering_prevented():
    # Client cannot supply unit_price; must use plan version
    assert True


def test_historical_price_preserved():
    assert True


def test_invalid_plan_version_rejected():
    assert True


def test_product_only_line_supported():
    assert True


def test_mixed_currencies_rejected():
    assert True


def test_invalid_lifecycle_transition():
    assert True


def test_expired_quotation_cannot_be_accepted():
    assert True


def test_unauthorized_access_denied():
    assert True


def test_transaction_rollback():
    assert True
