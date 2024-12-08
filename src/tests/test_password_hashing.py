import bcrypt
import pytest

def hash_password(raw_password):
    if not isinstance(raw_password, str):
        raise ValueError("Password must be a string")
    return bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

def test_password_hashing():
    raw_password = "my_secure_password"
    hashed_password = hash_password(raw_password)

    assert hashed_password != raw_password.encode('utf-8')

    # bcrypt check should return True for the correct password
    assert bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password)

    # bcrypt check should return False for an incorrect password
    assert not bcrypt.checkpw("wrong_password".encode('utf-8'), hashed_password)

# Test that the same password gives different hashes (because of the salt)
def test_password_hashing_consistency():
    raw_password = "my_secure_password"
    hashed_password_1 = hash_password(raw_password)
    hashed_password_2 = hash_password(raw_password)

    # The hashes should be different due to the unique salt
    assert hashed_password_1 != hashed_password_2

    # Both hashes should still be valid for the same password
    assert bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password_1)
    assert bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password_2)

# Test edge cases like empty passwords and invalid input types
def test_password_edge_cases():
    empty_password = ""
    hashed_empty = hash_password(empty_password)
    assert bcrypt.checkpw(empty_password.encode('utf-8'), hashed_empty)

    with pytest.raises(ValueError):
        hash_password(None)

    with pytest.raises(ValueError):
        hash_password(12345)

    long_password = "a" * 1000
    hashed_long = hash_password(long_password)
    assert bcrypt.checkpw(long_password.encode('utf-8'), hashed_long)

    # Test special characters
    special_password = "!@#$%^&*()_+"
    hashed_special = hash_password(special_password)
    assert bcrypt.checkpw(special_password.encode('utf-8'), hashed_special)

    non_ascii_password = "pāsswørd"
    hashed_non_ascii = hash_password(non_ascii_password)
    assert bcrypt.checkpw(non_ascii_password.encode('utf-8'), hashed_non_ascii)

def test_hash_length():
    raw_password = "my_secure_password"
    hashed_password = hash_password(raw_password)

    assert len(hashed_password) == 60