# tests/test_ai_tools_greet.py
import pytest
from ai.tools.greet_user import greet_user

def test_greet_user_with_name():
    """Test greeting with a valid username returns correct string."""
    username = "Mostafa"
    result = greet_user.invoke({"name": username})
    assert isinstance(result, str)
    assert username in result
    assert "CryptoSprite" in result
    assert "👋 Welcome" in result

def test_greet_user_empty_name():
    """Test greeting with empty username returns generic greeting."""
    result = greet_user.invoke({"name": ""})
    assert isinstance(result, str)
    assert "CryptoSprite" in result
    assert "👋 Welcome there" in result

def test_greet_user_no_username_key():
    """Test missing username key still returns a greeting."""
    result = greet_user.invoke({})
    assert isinstance(result, str)
    assert "CryptoSprite" in result
    assert "👋 Welcome there" in result

def test_greet_user_non_string_input():
    """Test non-string input is handled gracefully."""
    result = greet_user.invoke({"name": 123})
    assert isinstance(result, str)
    assert "CryptoSprite" in result
    assert "👋 Welcome there" in result