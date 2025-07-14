import sys
import os
import pytest

# Asegura que app.py sea accesible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_redirects(client):
    response = client.get('/')
    assert response.status_code in [200, 302]

def test_login_page(client):
    response = client.get('/login')
    html = response.data.decode('utf-8')
    assert "Iniciar Sesión" in html
    assert response.status_code == 200
