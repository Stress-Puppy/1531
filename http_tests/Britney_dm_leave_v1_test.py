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

# InputError when any of:
      
#         dm_id is not a valid DM
      
# AccessError when
      
#         Authorised user is not a member of DM with dm_id

# Given a DM ID, the user is removed as a member of this DM
    
# Parameters:(token, dm_id)
# Return Type:{}

# dm_leave_v1()

# commom case
def test_one_commom(reg_user):
    clear_v2()
    user = reg_user(0)
    token = user['token']
    second_user = reg_user(1)
    second_id = second_user['auth_user_id']

    # one dm id
    dm = dm_create_v1(token, [second_id])
    dm_id = dm['dm_id']
    
    dm_leave_v1(token, dm_id)

    dm_list = dm_list_v1(token)['dms']
    assert not len(dm_list)

def test_more_commom(reg_user):
    
    clear_v2()
    user = reg_user(0)
    token = user['token']
    second_user = reg_user(1)
    second_id = second_user['auth_user_id']
    
    # more dm id
    dm1 = dm_create_v1(token, [second_id])
    dm_id1 = dm1['dm_id']
    dm2 = dm_create_v1(token, [second_id])
    dm_id2 = dm2['dm_id']
    dm3 = dm_create_v1(token, [second_id])
    dm_id3 = dm3['dm_id']
    dm_leave_v1(token, dm_id1)
    dm_leave_v1(token, dm_id2)
    dm_leave_v1(token, dm_id3)

    dm_list = dm_list_v1(token)['dms']
    assert not len(dm_list)


# invaile token 
def test_invalid_token(reg_user, AccessError):
    
    clear_v2()
    first_user = reg_user(0)
    first_token = first_user['token']
    first_id = first_user['auth_user_id']
    dm = dm_create_v1(first_token, [first_id])
    dm_id = dm['dm_id']

    dm_leave_request = dm_leave_v1("invalid_token", dm_id)
    assert dm_leave_request.status_code == AccessError

# AccessError when:  Authorised user is not a member of DM with dm_id
def test_not_creator(reg_user, AccessError):
    clear_v2()
    first_user = reg_user(0)
    first_token = first_user['token']
    first_id = first_user['auth_user_id']
    dm = dm_create_v1(first_token, [first_id])
    dm_id = dm['dm_id']

    second_user = auth_register_v2("britney@league.com", "goodpass123", "Stress", "Puppy")
    second_token = second_user['token']
    dm_leave_request = dm_leave_v1(second_token, dm_id)
    assert dm_leave_request.status_code == AccessError

def test_not_creator_again(reg_user, AccessError):
    
    clear_v2()
    first_user = reg_user(0)
    first_token = first_user['token']
    second_user = reg_user(1)
    second_id = second_user['auth_user_id']
    second_token = second_user['token']
    dm = dm_create_v1(first_token, [second_id])
    dm_id = dm['dm_id']
    
    # already leave case
    dm_leave_v1(second_token, dm_id)

    dm_leave_request = dm_leave_v1(second_token, dm_id)
    assert dm_leave_request.status_code == AccessError

# InputError when:   dm_id does not refer to a valid DM 
def test_invalid_dm_id(reg_user, InputError):
    clear_v2()
    user = reg_user(0)
    token = user['token']
    u_id = user['auth_user_id']
    dm = dm_create_v1(token, [u_id])
    dm_id = dm['dm_id']
    
    dm_leave_request = dm_leave_v1(token, dm_id + 1)
    assert dm_leave_request.status_code == InputError


