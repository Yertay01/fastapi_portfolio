import json
from uuid import uuid4

import pytest

from db.models import PortalRole


async def test_update_user(
    client, create_user_in_database, get_user_from_database, user_roles
):
    user_data = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": user_roles,
    }
    user_data_updated = {
        "name": "Linus",
        "surname": "Torvalds",
        "email": "linuxmaster@gmail.com",
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data["user_id"])
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] == user_data_updated["is_active"]
    assert user_from_db["user_id"] == user_data_updated["user_id"]


async def test_update_user_check_one_is_updated(
    client, create_user_in_database, get_user_from_database
):
    user_data_1 = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    user_data_2 = {
        "user_id": uuid4(),
        "name": "Linus",
        "surname": "Torvalds",
        "email": "linuxmaster@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    user_data_3 = {
        "user_id": uuid4(),
        "name": "Nursultan",
        "surname": "Nazarbayev",
        "email": "elbasy01@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    user_data_updated = {
        "name": "Vladimir",
        "surname": "Putin",
        "email": "motherrussia@gmail.com",
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    for user_data in [user_data_1, user_data_2, user_data_3]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data_1['user_id']}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data_1["user_id"])
    users_from_db = await get_user_from_database(user_data_1["user_id"])
    user_from_db = dict(users_from_db[0])

    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] is user_data_1["is_active"]
    assert user_from_db["user_id"] == user_data_1["user_id"]

    # check other users that data has not been changed
    users_from_db = await get_user_from_database(user_data_2["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_2["name"]
    assert user_from_db["surname"] == user_data_2["surname"]
    assert user_from_db["email"] == user_data_2["email"]
    assert user_from_db["is_active"] is user_data_2["is_active"]
    assert user_from_db["user_id"] == user_data_2["user_id"]

    users_from_db = await get_user_from_database(user_data_3["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_3["name"]
    assert user_from_db["surname"] == user_data_3["surname"]
    assert user_from_db["email"] == user_data_3["email"]
    assert user_from_db["is_active"] is user_data_3["is_active"]
    assert user_from_db["user_id"] == user_data_3["user_id"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": "At least one parameter for user update info should be provided"
            },
        ),
        ({"name": "123"}, 422, {"detail": "Name should contains only letters"}),
        (
            {"email": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
        (
            {"surname": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "surname"],
                        "msg": "ensure this value has at least 1 characters",
                        "type": "value_error.any_str.min_length",
                        "ctx": {"limit_value": 1},
                    }
                ]
            },
        ),
        (
            {"name": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "ensure this value has at least 1 characters",
                        "type": "value_error.any_str.min_length",
                        "ctx": {"limit_value": 1},
                    }
                ]
            },
        ),
        ({"surname": "123"}, 422, {"detail": "Surname should contains only letters"}),
        (
            {"email": "123"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
    ],
)
async def test_update_user_validation_error(
    client,
    create_user_in_database,
    get_user_from_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_update_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)

    user_data_updated = {
        "name": "Linus",
        "surname": "Torvalds",
        "email": "linuxmaster@gmail.com",
    }

    resp = client.patch(
        "/user/?user_id=123",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_update_user_not_found_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)
    user_data_updated = {
        "name": "Linus",
        "surname": "Torvalds",
        "email": "linuxmaster@gmail.com",
    }
    user_id = uuid4()
    resp = client.patch(
        f"/user/?user_id={user_id}",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == 404
    resp_data = resp.json()
    assert resp_data == {"detail": f"User with id {user_id} not found."}


async def test_update_user_duplicate_email_error(client, create_user_in_database):
    user_data_1 = {
        "user_id": uuid4(),
        "name": "Alisher",
        "surname": "Yertayev",
        "email": "alisherertaev@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    user_data_2 = {
        "user_id": uuid4(),
        "name": "Linus",
        "surname": "Torvalds",
        "email": "linuxmaster@gmail.com",
        "is_active": True,
        "hashed_password": "password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    user_data_updated = {
        "email": user_data_2["email"],
    }
    for user_data in [user_data_1, user_data_2]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data_1['user_id']}",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )
