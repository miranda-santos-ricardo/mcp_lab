import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from week2_lab21_models import (
    CustomerProfile,
    CustomerPolicies,
)

from week2_lab21_service import (
    get_customer,
    get_policies,
    CustomerNotFoundError
)

def test_profile_schema_is_valid():
    schema = CustomerProfile.model_json_schema()
    Draft202012Validator.check_schema(schema)


def test_policies_schema_is_valid():
    schema = CustomerPolicies.model_json_schema()
    Draft202012Validator.check_schema(schema)


def test_customer_profile_success():
    result = get_customer("CUST-001")
    assert result.full_name == "Alice Martin"


def test_customer_not_found():
    with pytest.raises(CustomerNotFoundError):
        get_customer("CUST-999")


def test_active_policies_only():
    result = get_policies("CUST-001", "ACTIVE")

    assert len(result.policies) == 1
    assert result.policies[0].policy_id == "POL-001"


def test_customer_with_no_policies():
    result = get_policies("CUST-002")

    assert result.policies == []


def test_customer_profile_rejects_extra_fields():
    with pytest.raises(ValidationError):
        CustomerProfile.model_validate({
            "customer_id": "CUST-001",
            "full_name": "Alice Martin",
            "status": "ACTIVE",
            "admin": True,
        })


def test_customer_profile_rejects_bad_status():
    with pytest.raises(ValidationError):
        CustomerProfile.model_validate({
            "customer_id": "CUST-001",
            "full_name": "Alice Martin",
            "status": "UNKNOWN",
        })

def test_customer_output_matches_schema():
    customer = get_customer("CUST-001")

    schema = CustomerProfile.model_json_schema()
    payload = customer.model_dump(mode="json")

    Draft202012Validator(schema).validate(payload)