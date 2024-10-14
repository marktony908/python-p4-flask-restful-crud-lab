import json
import pytest
from app import app, db, Plant

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()  # Create the database and the tables
        # Seed the database with a test plant
        test_plant = Plant(
            name="Aloe",
            image="./images/aloe.jpg",
            price=11.50,
            is_in_stock=True
        )
        db.session.add(test_plant)
        db.session.commit()
        yield app.test_client()  # This is the test client
        db.drop_all()  # Cleanup after tests

class TestPlant:
    '''Flask application in app.py'''

    def test_plant_by_id_get_route(self, test_client):
        '''has a resource available at "/plants/<int:id>".'''
        response = test_client.get('/plants/1')
        assert response.status_code == 200

    def test_plant_by_id_get_route_returns_one_plant(self, test_client):
        '''returns JSON representing one Plant object at "/plants/<int:id>".'''
        response = test_client.get('/plants/1')
        data = json.loads(response.data.decode())

        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data

    def test_plant_by_id_patch_route_updates_is_in_stock(self, test_client):
        '''returns JSON representing updated Plant object with "is_in_stock" = False at "/plants/<int:id>".'''
        response = test_client.patch(
            '/plants/1',
            json={
                "is_in_stock": False,
            }
        )
        data = json.loads(response.data.decode())

        assert isinstance(data, dict)
        assert "id" in data
        assert data["is_in_stock"] == False

    def test_plant_by_id_delete_route_deletes_plant(self, test_client):
        '''deletes the specified Plant object at "/plants/<int:id>".'''
        lo = Plant(
            name="Live Oak",
            image="https://www.nwf.org/-/media/NEW-WEBSITE/Shared-Folder/Wildlife/Plants-and-Fungi/plant_southern-live-oak_600x300.ashx",
            price=250.00,
            is_in_stock=False,
        )

        with app.app_context():
            db.session.add(lo)
            db.session.commit()  # Ensure it is committed to the session
            plant_id = lo.id  # Store the ID for deletion

        response = test_client.delete(f'/plants/{plant_id}')
        assert response.status_code == 204  # Confirm deletion is successful

        # Check that the plant no longer exists
        response = test_client.get(f'/plants/{plant_id}')
        assert response.status_code == 404  # Confirm plant is deleted
