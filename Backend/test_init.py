from app import create_app

app = create_app()

with app.test_client() as client:
    resp = client.get('/api/login/init')
    print('Status:', resp.status_code)
    print('Content-Type:', resp.content_type)
    try:
        print('Response:', resp.get_json())
    except:
        print('Response (raw):', resp.data.decode())
