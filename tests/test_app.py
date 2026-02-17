import os
import sqlite3
import tempfile

import pytest

from app import app


@pytest.fixture
def client(tmp_path):
    # prepare a fresh DB from schema.sql
    db_path = tmp_path / 'test.db'
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = sqlite3.connect(str(db_path))
    conn.executescript(sql)
    conn.commit()
    conn.close()

    app.config['DATABASE'] = str(db_path)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_list_giochi(client):
    rv = client.get('/giochi')
    assert rv.status_code == 200
    assert b'Catan' in rv.data or b'Ticket to Ride' in rv.data


def test_create_gioco(client):
    rv = client.post('/giochi', data={'nome': 'TestGame', 'numero_giocatori_massimo': '4', 'durata_media': '45', 'categoria': 'Party'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'TestGame' in rv.data


def test_create_partita(client):
    rv = client.post('/giochi/1/partite', data={'data': '2024-01-01', 'vincitore': 'Tester', 'punteggio_vincitore': '5'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Tester' in rv.data
