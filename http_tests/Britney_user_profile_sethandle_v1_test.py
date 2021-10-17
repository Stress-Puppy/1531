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
      
#         handle_str must be between 3 and 20 characters
#         handle is already used by another user

# Parameters:(token, handle_str)
# Return Type:{}

# Update the authorised user's handle (i.e. display name)

# user_profile_sethandle_v1()

# invaile token 
def test_invalid_token(reg_user, AccessError):

    clear_v2()
    handle_str = 'stresspuppy'

    sethandle_request = user_profile_sethandle_v1("invalid_token", handle_str)
    assert sethandle_request.status_code == AccessError
        
#         commom case 1
def test_single_change(reg_user):

    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    handle_str = 'stresspuppy'
    user_profile_sethandle_v1(user_token, handle_str)
    user_details = user_profile_v2(user_token, user_id)['user']
    assert user_details['handle_str'] == 'stresspuppy'

#         commom case 2
def test_more_change(reg_user):

    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    handle_str = 'stresspuppy'
    user_profile_sethandle_v1(user_token, handle_str)
    first_details = user_profile_v2(user_token, user_id)['user']

    second_user = reg_user(1)
    second_token = second_user['token']
    second_id =  second_user['auth_user_id']
    handle_second = 'sweetsong'
    user_profile_sethandle_v1(second_token, handle_second)
    second_details = user_profile_v2(second_token, second_id)['user']

    assert first_details['handle_str'] == 'stresspuppy'
    assert second_details['handle_str'] == 'sweetsong'

#         handle_str must be between 3 and 20 characters
def test_length(reg_user, InputError):
    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    handle_short = 'hi'
    handle_long = 'a'*100

    sethandle_request = user_profile_sethandle_v1(user_token, handle_short)
    assert sethandle_request.status_code == InputError

    sethandle_request = user_profile_sethandle_v1(user_token, handle_long)
    assert sethandle_request.status_code == InputError

#         handle is already used by another user
def test_used_handle(reg_user, InputError):
    clear_v2()

    first_user = reg_user(0)
    first_token = first_user['token']
    user_profile_sethandle_v1(first_token, 'stresspuppy')

    second_user = reg_user(1)
    second_token = second_user['token']

    sethandle_request = user_profile_sethandle_v1(second_token, 'stresspuppy')
    assert sethandle_request.status_code == InputError
