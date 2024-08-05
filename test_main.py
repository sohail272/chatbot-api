from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import crud

client = TestClient(app)

def test_get_token():
    response = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_and_get_messages():
    token_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
    )
    token = token_response.json()["access_token"]

    mock_user_message = {"id": 1, "content": "Hello, world!", "sender": "user"}
    mock_system_message = {"id": 2, "content": "Your message was recorded as: Hello, world!", "sender": "system"}
    
    with patch("crud.create_message", side_effect=[mock_user_message, mock_system_message]):
        response = client.post(
            "/messages/",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Hello, world!"}
        )
        assert response.status_code == 200
        response_data = response.json()
        
        # Ensure both messages are returned and correct
        assert isinstance(response_data, list)
        assert response_data[0]["content"] == "Hello, world!"
        assert response_data[1]["content"] == "Your message was recorded as: Hello, world!"

def test_delete_message():
    token_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
    )
    token = token_response.json()["access_token"]

    mock_message = {"id": 1, "content": "Hello, world!", "sender": "user"}

    with patch("crud.get_message", return_value=mock_message), patch("crud.delete_message", return_value=mock_message):
        response = client.delete(
            "/messages/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["content"] == "Hello, world!"

def test_update_message():
    token_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
    )
    token = token_response.json()["access_token"]

    original_message = {"id": 1, "content": "Hello, world!", "sender": "user"}
    updated_message = {"id": 1, "content": "Updated content", "sender": "user"}

    with patch("crud.get_message", return_value=original_message), patch("crud.update_message", return_value=updated_message):
        response = client.put(
            "/messages/1",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Updated content"}
        )
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["content"] == "Updated content"
