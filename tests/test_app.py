import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    """Test that the home page loads correctly."""
    rv = client.get('/')
    assert rv.status_code == 200
    # Check if a key phrase is in the response
    assert b"Tambah Transaksi Baru" in rv.data

def test_add_transaction(client):
    """Test adding a new transaction."""
    # Follow_redirects=True allows the test client to follow the redirect
    # to the homepage after the POST request.
    rv = client.post('/tambah', data=dict(
        deskripsi="Test Pengeluaran",
        jumlah="10000",
        jenis="pengeluaran"
    ), follow_redirects=True)

    assert rv.status_code == 200
    # Check if the new transaction now appears on the home page
    assert b"Test Pengeluaran" in rv.data
    assert b"- Rp 10,000" in rv.data