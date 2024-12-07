import bcrypt
import pytest

def hash_password(raw_password):
    if not isinstance(raw_password, str):
        raise ValueError("Password must be a string")
    return bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

def test_password_hashing():
    raw_password = "my_secure_password"
    hashed_password = hash_password(raw_password)

    # Ensure hashed password is different from the raw password
    assert hashed_password != raw_password.encode('utf-8')

    # Ensure bcrypt can verify the correct password
    assert bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password)

    # Ensure bcrypt rejects an incorrect password
    assert not bcrypt.checkpw("wrong_password".encode('utf-8'), hashed_password)

def test_password_edge_cases():
    empty_password = ""
    hashed_empty = hash_password(empty_password)
    assert bcrypt.checkpw(empty_password.encode('utf-8'), hashed_empty)

    # Test invalid input types
    with pytest.raises(ValueError):
        hash_password(None)
    with pytest.raises(ValueError):
        hash_password(12345)
