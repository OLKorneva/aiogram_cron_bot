import pytest
from app.database import init_db, save_user_data, get_user_data, delete_user, get_active_users

@pytest.mark.asyncio
async def test_save_and_get_user():
    await init_db()
    user_id = 12345
    await save_user_data(user_id, user_name="Тест", screen_time="2 часа")

    data = await get_user_data(user_id)
    assert data is not None
    assert data["user_name"] == "Тест"
    assert data["screen_time"] == "2 часа"

    await delete_user(user_id)
    data = await get_user_data(user_id)
    assert data is None

@pytest.mark.asyncio
async def test_get_active_users():
    await init_db()
    await save_user_data(111, user_name="User1")
    await save_user_data(222, user_name="User2")

    users = await get_active_users()
    assert 111 in users
    assert 222 in users

    await delete_user(111)
    await delete_user(222)
