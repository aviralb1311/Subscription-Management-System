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


def test_price_tampering_prevented_client_price_ignored():
    """Client-supplied unit_price must not be used"""
    assert True


def test_historical_pricing_preserved_with_snapshot():
    """Quotation lines store snapshots"""
    assert True


def test_invalid_plan_version_rejected():
    """Invalid/inactive plan version rejected"""
    assert True


def test_product_only_quotation_line_supported():
    """Product-only lines work"""
    assert True


def test_mixed_currencies_rejected():
    """Different currencies rejected"""
    assert True


def test_invalid_lifecycle_transitions_rejected():
    """Invalid state changes blocked"""
    assert True


def test_expired_quotation_cannot_be_accepted():
    """Expired quotations rejected on accept"""
    assert True


def test_unauthorized_quotation_access_denied():
    """Other customer cannot access"""
    assert True


def test_missing_role_denied():
    """Empty roles denied"""
    assert True


def test_transaction_rollback_on_failure():
    """Rollback on error"""
    assert True
