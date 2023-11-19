def test_sanity(client) -> None:  # type: ignore
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
