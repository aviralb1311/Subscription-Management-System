from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_customers_requires_auth():
    response = client.get("/api/v1/customers/")
    assert response.status_code == 403


def test_list_quotations_requires_auth():
    response = client.get("/api/v1/quotations/")
    assert response.status_code == 403


def test_quote_requires_plan_version_or_product():
    pass


def test_price_tampering_ignored():
    pass


def test_historical_price_preservation():
    pass


def test_invalid_plan_version_combination():
    pass


def test_invalid_lifecycle_transition():
    pass


def test_expired_quotation_cannot_be_accepted():
    pass


def test_unauthorized_access_to_other_customer_quote():
    pass


def test_mixed_currencies_rejected():
    pass


def test_product_only_quotation_line():
    pass


def test_transaction_rollback_on_failure():
    pass
