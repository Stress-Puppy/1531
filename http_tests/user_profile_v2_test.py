import pytest

from http_tests.route_wrappers_test import *

# u_id, email, name_first, name_last, handle_str

@pytest.fixture
def user_details():
    def _user_details(num):
        return (f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _user_details

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

def test_access_own_profile(user_details):
    clear_v2()
    eAddress, pword, fName, lName = user_details(0)
    user = auth_register_v2(eAddress, pword, fName, lName)
    user_profile = user_profile_v2(user['token'], user['auth_user_id'])['user']
    assert user_profile['u_id'] == user['auth_user_id']
    assert user_profile['email'] == eAddress
    assert user_profile['name_first'] == fName
    assert user_profile['name_last'] == lName
    assert user_profile['handle_str'] == f"{fName}{lName}"

def test_access_other_profile(user_details, reg_user):
    clear_v2()
    eAddress, pword, fName, lName = user_details(0)
    user_1 = auth_register_v2(eAddress, pword, fName, lName)
    user_2 = reg_user(1)
    user_1_profile = user_profile_v2(user_2['token'], user_1['auth_user_id'])['user']
    assert user_1_profile['u_id'] == user_1['auth_user_id']
    assert user_1_profile['email'] == eAddress
    assert user_1_profile['name_first'] == fName
    assert user_1_profile['name_last'] == lName
    assert user_1_profile['handle_str'] == f"{fName}{lName}"

def test_change_email(user_details, email):
    clear_v2()
    eAddress, pword, fName, lName = user_details(0)
    user = auth_register_v2(eAddress, pword, fName, lName)
    new_eAddress = email(1)
    user_profile_setemail_v1(user['token'], new_eAddress)
    user_profile = user_profile_v2(user['token'], user['auth_user_id'])['user']
    assert user_profile['u_id'] == user['auth_user_id']
    assert user_profile['email'] == new_eAddress
    assert user_profile['name_first'] == fName
    assert user_profile['name_last'] == lName
    assert user_profile['handle_str'] == f"{fName}{lName}"

def test_change_name(user_details):
    clear_v2()
    eAddress, pword, fName, lName = user_details(0)
    user = auth_register_v2(eAddress, pword, fName, lName)
    new_fName = "New"
    new_lName = "Name"
    user_profile_setname_v2(user['token'], new_fName, new_lName)
    user_profile = user_profile_v2(user['token'], user['auth_user_id'])['user']
    assert user_profile['u_id'] == user['auth_user_id']
    assert user_profile['email'] == eAddress
    assert user_profile['name_first'] == new_fName
    assert user_profile['name_last'] == new_lName
    assert user_profile['handle_str'] == f"{fName}{lName}" # Assume handle doesn't change

def test_invalid_u_id(user_details, InputError):
    clear_v2()
    eAddress, pword, fName, lName = user_details(0)
    user = auth_register_v2(eAddress, pword, fName, lName)
    profile_request = user_profile_v2(user['token'], user['auth_user_id']+1)
    assert profile_request.status_code == InputError

def test_invalid_token(user_details, AccessError):
    clear_v2()
    eAddress, pword, fName, lName = user_details(0)
    user = auth_register_v2(eAddress, pword, fName, lName)
    profile_request = user_profile_v2("invalid_token", user['auth_user_id'])
    assert profile_request.status_code == AccessError
