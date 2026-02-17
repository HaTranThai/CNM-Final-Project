"""Basic auth and health tests."""
import pytest


def test_health_endpoint_exists():
    """Verify the health router is configured."""
    from app.api.routes.health import router
    assert router is not None
    routes = [r.path for r in router.routes]
    assert "/health" in routes


def test_security_hash():
    """Test password hashing."""
    from app.core.security import hash_password, verify_password
    hashed = hash_password("test123")
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_token():
    """Test JWT token creation and decoding."""
    from app.core.security import create_access_token, decode_access_token
    token = create_access_token(data={"sub": "test-user-id"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test-user-id"


if __name__ == "__main__":
    test_health_endpoint_exists()
    test_security_hash()
    test_jwt_token()
    print("All auth tests passed! ✅")
