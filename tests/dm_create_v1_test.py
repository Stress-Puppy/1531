import pytest

from src.other import clear_v2
from src.auth import auth_register_v2
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.data import next_dm_id

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def u_handle():
    def _user_handle(num):
        return f"firstname{num}lastname{num}"
    return _user_handle

@pytest.fixture
def dm_name():
    def _dm_name(handles):
        return ', '.join(sorted(handles))
    return _dm_name

def test_single_dm_to_single_user(reg_user, u_handle, dm_name):
    clear_v2()
    sender_token = reg_user(0)['token']
    sender_handle = u_handle(0)
    receiver_id = reg_user(1)['auth_user_id']
    receiver_handle = u_handle(1)
    dm = dm_create_v1(sender_token, [receiver_id])
    assert dm['dm_id'] == 0
    assert dm['dm_name'] == dm_name([receiver_handle, sender_handle])

def test_single_dm_to_multi_user(reg_user, u_handle, dm_name):
    clear_v2()
    sender_token = reg_user(0)['token']
    handles = [u_handle(0)]
    u_ids = []
    for i in range(1,4):
        receiver_id = reg_user(i)['auth_user_id']
        u_ids.append(receiver_id)
        handles.append(u_handle(i))
    dm = dm_create_v1(sender_token, u_ids)
    assert dm['dm_id'] == 0
    assert dm['dm_name'] == dm_name(handles)

def test_multi_dm_to_single_user(reg_user, u_handle, dm_name):
    clear_v2()
    sender_token = reg_user(0)['token']
    sender_handle = u_handle(0)
    receiver_id = reg_user(1)['auth_user_id']
    receiver_handle = u_handle(1)
    u_id = [receiver_id]
    for i in range(0,3):
        dm = dm_create_v1(sender_token, u_id)
        assert dm['dm_id'] == i
        assert dm['dm_name'] == dm_name([sender_handle, receiver_handle])

def test_multi_dm_to_multi_user(reg_user, u_handle, dm_name):
    clear_v2()
    sender_token = reg_user(0)['token']
    handles = [u_handle(0)]
    u_ids = []
    for i in range(1,4):
        receiver_id = reg_user(i)['auth_user_id']
        u_ids.append(receiver_id)
        handles.append(u_handle(i))
    for i in range(0,3):
        dm = dm_create_v1(sender_token, u_ids)
        assert dm['dm_id'] == i
        assert dm['dm_name'] == dm_name(handles)

def test_invalid_token(reg_user):
    clear_v2()
    reg_user(0)
    receiver_id = reg_user(1)['auth_user_id']
    with pytest.raises(AccessError):
        dm_create_v1("invalid_token", [receiver_id])

def test_invalid_u_id(reg_user):
    clear_v2()
    sender_token = reg_user(0)['token']
    receiver_id = reg_user(1)['auth_user_id']
    with pytest.raises(InputError):
        dm_create_v1(sender_token, [receiver_id+1])
