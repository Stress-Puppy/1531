import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def user_details():
    return ("example@email.com", "Password", "Auth", "User")

@pytest.fixture
def InputError():
    return 400

#   InputError when any of:
      
#   Email entered is not a valid email
#   Email entered does not belong to a user
#   Password is not correct

#   Parameters:
#   (email, password)
#   Return Type:
#   { token, auth_user_id }

#   Email entered is not a valid email
def test_auth_login_v2_invalid_email(user_details, InputError): 
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    invalid_email = "ankitrai326.com"
    test_password = "afuayqwgfu"
    
    login_request = auth_login_v2(invalid_email, test_password) 
    assert login_request.status_code == InputError

#   Email entered does not belong to a user
def test_auth_login_v2_no_user(user_details, InputError): 
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    unused_email = "my.ownsite@ourearth.org"
    unused_password = "e5r423tfywy"
    
    login_request = auth_login_v2(unused_email, unused_password)  
    assert login_request.status_code == InputError

#   Password is not correct
def test_auth_login_v2_incorrect_password(user_details, InputError): 
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    password = "password"
    
    login_request = auth_login_v2(email, password) 
    assert login_request.status_code == InputError

#   login succeeful
def test_auth_login_v2_correct_password(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    user = auth_register_v2(email, pwd, fName, lName)
    
    assert auth_login_v2(email, pwd)['auth_user_id'] == user['auth_user_id']
