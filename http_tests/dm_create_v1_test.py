import pytest

from http_tests.route_wrappers_test import *

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

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

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

def test_invalid_token(reg_user, AccessError):
    clear_v2()
    reg_user(0)
    receiver_id = reg_user(1)['auth_user_id']
    create_request = dm_create_v1("invalid_token", [receiver_id])
    assert create_request.status_code == AccessError

def test_invalid_u_id(reg_user, InputError):
    clear_v2()
    sender_token = reg_user(0)['token']
    receiver_id = reg_user(1)['auth_user_id']
    create_request = dm_create_v1(sender_token, [receiver_id+1])
    assert create_request.status_code == InputError
