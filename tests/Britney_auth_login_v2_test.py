import pytest

from src.error import InputError
from src.auth import auth_register_v2, auth_login_v2
from src.other import clear_v2

#   InputError when any of:
      
#   Email entered is not a valid email
#   Email entered does not belong to a user
#   Password is not correct

#   Parameters:
#   (email, password)
#   Return Type:
#   { token, auth_user_id }

@pytest.fixture
def user_details():
    return ("example@email.com", "Password", "Auth", "User")

#   three tests for failing cases

def test_auth_login_v2_invalid_email(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    invalid_email = "ankitrai326.com"
    test_password = "afuayqwgfu"
    
    with pytest.raises(InputError): 
        auth_login_v2(invalid_email, test_password) 

def test_auth_login_v2_no_user(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    unused_email = "my.ownsite@ourearth.org"
    unused_password = "e5r423tfywy"
    
    with pytest.raises(InputError): 
        auth_login_v2(unused_email, unused_password) 

def test_auth_login_v2_incorrect_password(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    password = "password"
    
    with pytest.raises(InputError): 
        auth_login_v2(email, password) 


#   login succeeful

def test_auth_login_v2_correct_password(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    user = auth_register_v2(email, pwd, fName, lName)
    
    assert auth_login_v2(email, pwd)['auth_user_id'] == user['auth_user_id']
