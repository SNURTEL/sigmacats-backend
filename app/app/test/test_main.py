import requests

def test_sanity(client) -> None:  # type: ignore
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_register():
    # api-endpoint
    URL = "http://localhost:8000/auth/register"

    # location given here
    location = "delhi technological university"

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'type': 'rider', 'username': 'mewash', 'name': 'jan', 'surname': 'kowalski', 'email': 'test@gmail.com', 'password': '123'}
    '''
curl \
-H "Content-Type: application/json" \
-X POST \
-d "{\"type\": \"rider\", \"username\": \"mewash\", \"name\": \"jan\", \"surname\": \"kowalski\", \"email\": \"test@gmail.com\", \"password\": \"studentdebil\"}" \
http://localhost:8000/auth/register
    '''

    '''
    curl \
-H "Content-Type: application/json" \
-X POST \
-d "{\"email\": \"king.arthur@camelot.bt\",\"password\": \"guinevere\"}" \
http://localhost:8000/auth/register
    '''

    # sending get request and saving the response as response object
    r = requests.post(url=URL, params=PARAMS)

    # extracting data in json format
    data = r.json()

    print(data)


if __name__ == "__main__":
    test_register()