from uuid import uuid4


async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
    }

    await create_user_in_database(**user_data)
    resp = client.delete(f"/user/?user_id={user_data['user_id']}")
    assert resp.status_code == 200
    assert resp.json() == {"deleted_user_id": str(user_data["user_id"])}
    users_from_db = await get_user_from_database(user_data["user_id"])
    users_from_db = dict(users_from_db[0])
    assert users_from_db["name"] == user_data["name"]
    assert users_from_db["surname"] == user_data["surname"]
    assert users_from_db["email"] == user_data["email"]
    assert users_from_db["is_active"] == user_data["is_active"]
    assert users_from_db["user_id"] == user_data["user_id"]


async def test_delete_user_not_found(client):
    user_id = uuid4()
    resp = client.delete(f"/user/?user_id={user_id}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {user_id} not found"}


async def test_delete_user_user_id_validation_error(client):
    resp = client.delete(f"/user/?user_id=123")
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }
