import pytest
from app import app, db
from app.models import Song

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_search_songs(client):
    song_to_add = Song(
        song_name="Hymn to Virgil",
        game="DanceDanceRevolution",
        higher_bpm=120,
        lower_bpm=100,
        licensed=True,
        changing_bpm=False,
        runtime=180,
        artist="Hozier"
    )
    db.session.add(song_to_add)
    db.session.commit()

    # Test for an exact match (song is found)
    response = client.get('/search?songName=Hymn to Virgil')
    assert response.status_code == 200
    assert b'Hymn to Virgil' in response.data

    # Test for a song that does not exist (song is not found)
    response = client.get('/search?songName=The Door')
    assert response.status_code == 200
    assert b'The Door' not in response.data

    response = client.get('/search?songName=')
    assert response.status_code == 200
    assert b'No results found' in response.data

    # Test for a partial match (if search supports partial matching)
    response = client.get('/search?songName=Hymn')
    assert response.status_code == 200
    assert b'Hymn to Virgil' in response.data

    # Test for case-insensitive search
    response = client.get('/search?songName=hYmn To ViRgIl')
    assert response.status_code == 200
    assert b'Hymn to Virgil' in response.data

    # Test for searching by artist name
    response = client.get('/search?artist=Hozier')
    assert response.status_code == 200
    assert b'Hymn to Virgil' in response.data

    # Test invalid query (e.g., invalid characters or malformed input)
    response = client.get('/search?songName=%%%')
    assert response.status_code == 400

    db.session.delete(song_to_add)
    db.session.commit()