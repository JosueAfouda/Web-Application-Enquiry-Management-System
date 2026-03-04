from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    password = "strong-password"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_access_token_encode_decode() -> None:
    token, _ = create_access_token(subject="abc", roles=["SuperAdmin"])
    payload = decode_access_token(token)

    assert payload["sub"] == "abc"
    assert payload["type"] == "access"


def test_decode_rejects_invalid_token() -> None:
    try:
        decode_access_token("invalid-token")
    except TokenError:
        return
    else:
        raise AssertionError("invalid token should raise TokenError")


def test_refresh_token_hash_is_deterministic() -> None:
    token = "refresh-token-example"

    assert hash_refresh_token(token) == hash_refresh_token(token)
