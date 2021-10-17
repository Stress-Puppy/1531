import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

def test_invite_single_user(reg_user):
    clear_v2()
    sender = reg_user(0)
    receiver_id = reg_user(1)['auth_user_id']

    dm = dm_create_v1(sender['token'], [receiver_id])

    invitee_id = reg_user(2)['auth_user_id']
    dm_invite_v1(sender['token'], dm['dm_id'], invitee_id)

    dm_members = [sender['auth_user_id'], receiver_id, invitee_id]
    dm_details = dm_details_v1(sender['token'], dm['dm_id'])
    for user in dm_details['members']:
        assert user['u_id'] in dm_members

def test_invite_multi_user(reg_user):
    clear_v2()
    sender = reg_user(0)
    receiver_id = reg_user(1)['auth_user_id']
    dm = dm_create_v1(sender['token'], [receiver_id])
    dm_members = [sender['auth_user_id'], receiver_id]

    for i in range(2,5):
        invitee_id = reg_user(i)['auth_user_id']
        dm_invite_v1(sender['token'], dm['dm_id'], invitee_id)
        dm_members.append(invitee_id)

    dm_details = dm_details_v1(sender['token'], dm['dm_id'])
    for user in dm_details['members']:
        assert user['u_id'] in dm_members

def test_invalid_token(reg_user, AccessError):
    clear_v2()
    sender_token = reg_user(0)['token']
    receiver_id = reg_user(1)['auth_user_id']
    dm = dm_create_v1(sender_token, [receiver_id])
    invitee_id = reg_user(2)['auth_user_id']
    invite_request = dm_invite_v1("invalid_token", dm['dm_id'], invitee_id)
    assert invite_request.status_code == AccessError

def test_invalid_dm_id(reg_user, InputError):
    clear_v2()
    sender_token = reg_user(0)['token']
    receiver_id = reg_user(1)['auth_user_id']
    dm = dm_create_v1(sender_token, [receiver_id])
    invitee_id = reg_user(2)['auth_user_id']
    invite_request = dm_invite_v1(sender_token, dm['dm_id']+1, invitee_id)
    assert invite_request.status_code == InputError

def test_invalid_u_id(reg_user, InputError):
    clear_v2()
    sender_token = reg_user(0)['token']
    receiver_id = reg_user(1)['auth_user_id']
    dm = dm_create_v1(sender_token, [receiver_id])
    invitee_id = reg_user(2)['auth_user_id']
    invite_request = dm_invite_v1(sender_token, dm['dm_id'], invitee_id+1)
    assert invite_request.status_code == InputError

def test_invite_from_non_member(reg_user, AccessError):
    clear_v2()
    sender_token = reg_user(0)['token']
    receiver_id = reg_user(1)['auth_user_id']
    dm = dm_create_v1(sender_token, [receiver_id])
    invitee = reg_user(2)
    invite_request = dm_invite_v1(invitee['token'], dm['dm_id'], invitee['auth_user_id'])
    assert invite_request.status_code == AccessError
