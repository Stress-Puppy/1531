import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def email():
    def _email(num):
        return f"example{num}@email.com"
    return _email

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

def test_single_change(reg_user, email):
    clear_v2()
    user = reg_user(0)
    new_email = email(1)
    user_profile_setemail_v1(user['token'], new_email)
    user_details = user_profile_v2(user['token'], user['auth_user_id'])['user']
    assert user_details['email'] == new_email

def test_change_email_then_change_back(reg_user, email):
    clear_v2()
    user = reg_user(0)
    original_email = email(0)
    new_email = email(1)
    user_profile_setemail_v1(user['token'], new_email)
    user_details = user_profile_v2(user['token'], user['auth_user_id'])['user']
    assert user_details['email'] == new_email
    user_profile_setemail_v1(user['token'], original_email)
    user_details = user_profile_v2(user['token'], user['auth_user_id'])['user']
    assert user_details['email'] == original_email

def test_change_email_then_other_user_change_to_original_email(reg_user, email):
    clear_v2()
    user_1 = reg_user(0)
    user_2 = reg_user(1)
    user_1_original_email = email(0)
    user_1_new_email = email(2)
    user_profile_setemail_v1(user_1['token'], user_1_new_email)
    user_profile_setemail_v1(user_2['token'], user_1_original_email)
    user_1_profile = user_profile_v2(user_1['token'], user_1['auth_user_id'])['user']
    user_2_profile = user_profile_v2(user_2['token'], user_2['auth_user_id'])['user']
    assert user_1_profile['email'] == user_1_new_email
    assert user_2_profile['email'] == user_1_original_email

def test_invalid_email(reg_user, email, InputError):
    clear_v2()
    user_token = reg_user(0)['token']
    invalid_email = "email"
    setemail_request = user_profile_setemail_v1(user_token, invalid_email)
    assert setemail_request.status_code == InputError

def test_used_email(reg_user, email, InputError):
    clear_v2()
    user_1_token = reg_user(0)['token']
    reg_user(1)
    user_2_email = email(1)
    setemail_request = user_profile_setemail_v1(user_1_token, user_2_email)
    assert setemail_request.status_code == InputError

def test_invalid_token(reg_user, email, AccessError):
    clear_v2()
    reg_user(0)
    new_email = email(1)
    setemail_request = user_profile_setemail_v1("invalid token", new_email)
    assert setemail_request.status_code == AccessError
