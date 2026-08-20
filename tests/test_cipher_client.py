import os

os.environ.setdefault("CIPHER_CLIENT_ID", "test")
os.environ.setdefault("CIPHER_CLIENT_SECRET", "test")

from backend.cipher_client import CipherClient


def test_clean_params_removes_none_and_serializes_boolean():
    result = CipherClient._clean_params({"a": None, "b": True, "c": False, "d": "x"})
    assert result == {"b": "true", "c": "false", "d": "x"}
