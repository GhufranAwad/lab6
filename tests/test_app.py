import pytest
from app import app, db
from models import Contact

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_contact():
    contact = Contact(
        name='John Doe',
        phone='1234567890',
        email='john@example.com',
        type='Personal'
    )
    db.session.add(contact)
    db.session.commit()
    return contact
def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_add_contact(client):
    data = {
        'name': 'Jane Doe',
        'phone': '9876543210',
        'email': 'jane@example.com',
        'type': 'Personal'
    }
    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Jane Doe' in response.data

def test_update_contact(client, sample_contact):
    data = {
        'name': 'John Smith',
        'phone': sample_contact.phone,
        'email': sample_contact.email,
        'type': sample_contact.type,
        'submit': 'Update'
    }
    response = client.post(
        f'/update/{sample_contact.id}',
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    updated_contact = db.session.get(Contact, sample_contact.id)
    assert updated_contact.name == 'John Smith'
# Test Case: Delete Contact
def test_delete_contact(client, sample_contact):
    response = client.get(f'/delete/{sample_contact.id}', follow_redirects=True)
    assert response.status_code == 200

    # Ensure contact is deleted
    deleted_contact = db.session.get(Contact, sample_contact.id)
    assert deleted_contact is None
#test case : search contact 
def test_search_contact(client, sample_contact):
    response = client.get('/contacts?search=John')
    assert response.status_code == 200
    assert b'John Doe' in response.data

# Added the following API Test CASES
def test_get_contacts_api(client, sample_contact):
    response = client.get('/api/contacts')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'John Doe'

def test_get_single_contact_api(client, sample_contact):
    response = client.get(f'/api/contacts/{sample_contact.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'John Doe'

def test_create_contact_api(client):
    data = {
        'name': 'API User',
        'phone': '5555555555',
        'email': 'api@example.com',
        'type': 'work'
    }
    response = client.post('/api/contacts', json=data)
    assert response.status_code == 201
    assert response.get_json()['name'] == 'API User'

# # New API Test Cases
def test_update_contact_api(client, sample_contact):
    updated_data = {'name': 'Updated Name'}
    response = client.put(f'/api/contacts/{sample_contact.id}', json=updated_data)
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Name'

def test_delete_contact_api(client, sample_contact):
    response = client.delete(f'/api/contacts/{sample_contact.id}')
    assert response.status_code == 204  # No Content
    assert db.session.get(Contact, sample_contact.id) is None  # Ensure deleted

def test_list_contact_api(client, sample_contact):
    response = client.get('/api/contacts')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1  # Ensure at least one contact is present

# Error Handling Tests
#  test error cases 
def test_invalid_contact_creation(client):
    data = {'name': 'Invalid User'}  # Missing required fields
    response = client.post('/api/contacts', json=data)
    assert response.status_code == 400  # Bad Request

def test_get_nonexistent_contact(client):
    response = client.get('/api/contacts/999')  # Nonexistent ID
    assert response.status_code == 404  # Not Found



