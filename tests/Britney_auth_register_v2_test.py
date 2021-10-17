import pytest

from src.error import InputError
from src.other import clear_v2

from src.auth import auth_register_v2, auth_login_v2
from src.user import user_profile_v2

# Test Case
# General case
@pytest.fixture
def user_details(): 
    return ("akali@league.com", "goodpass123", "Shen", "Ionia")

# Error cases
# 1. email is not valid (use method in gitlab) 
def test_not_valid_email():
    clear_v2()
    with pytest.raises(InputError):  
        auth_register_v2("garen!league.com", "goodpass123", "Garen", "Demacia")
        # Invalid email format (no @)

# 2. email is already being used
def test_already_used_email(user_details):
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    with pytest.raises(InputError):
        auth_register_v2(email, pwd, fName, lName)
    # Duplicate emails

# 3. password < 6 characters
def test_pass_too_short():
    clear_v2()
    with pytest.raises(InputError):
        auth_register_v2("akali@league.com", "abc", "Akali", "Ionia")

# 4. NOT 1 <= name_first, name_last length <= 50
def test_name_length_error():
    clear_v2()
    with pytest.raises(InputError):
        auth_register_v2("akali@league.com", "goodpass123", "", "Ionia")
    with pytest.raises(InputError):
        # first name < 1 so error
        auth_register_v2("aatrox@league.com", "goodpass123", \
            "Now hear the silence of annihilation!They think me defeated, enchained. But I am unbowed... Noble is this carnage.", "Darkin")
    with pytest.raises(InputError):
        # long first name
        auth_register_v2("azir@league.com", "goodpass123", "Azir", "")
    with pytest.raises(InputError):
        # no last name
        auth_register_v2("azir@league.com", "goodpass123", "Azir", " Shurima! Your emperor has returned!Shurima will once again stretch to the horizon.\
            Shurima will once again stretch to the horizon.Shurima will once again stretch to the horizon.")
        # long last name

# # 5. commom case
# def test_correct_case():
#     clear_v2()
#     email, pwd, fName, lName = user_details()

#     token = jwt.encode(user, SECRET, algorithm='HS256')

#     assert auth_register_v2(email, pwd, fName, lName) == { 'token' : token, 'auth_user_id' : 0 }

        
# 5. handle error 
#   repeat error  
def test_handle_repeat():
    clear_v2()
    user1 = auth_register_v2("britney@league.com", "goodpass123", "Stress", "Puppy")
    user2 = auth_register_v2("britney2@league.com", "goodpass123", "Stress", "Puppy")
    user3 = auth_register_v2("britney3@league.com", "goodpass123", "Stress", "Puppy")
    
    user_1 = user_profile_v2(user1['token'], user1['auth_user_id'])['user']
    user_2 = user_profile_v2(user2['token'], user2['auth_user_id'])['user']
    user_3 = user_profile_v2(user3['token'], user3['auth_user_id'])['user']
        
 
    assert user_1['handle_str'] == "stresspuppy"
    assert user_2['handle_str'] == "stresspuppy0"
    assert user_3['handle_str'] == "stresspuppy1"

#   (concatenation length > 20)
#   Appending number -> might result in exceeding 20 character limit
def test_handle_cut_off_and_appengding_number():
    clear_v2()
    user1 = auth_register_v2("azir@league.com", "password", "azir", "thisIsLongerThanTwenty")
    user2 = auth_register_v2("azir1@league.com", "password", "azir", "thisIsLongerThanTwenty")
    
    user_1 = user_profile_v2(user1['token'], user1['auth_user_id'])['user']
    user_2 = user_profile_v2(user2['token'], user2['auth_user_id'])['user']
    
    assert user_1['handle_str'] == "azirthisislongerthan"
    assert user_2['handle_str'] == "azirthisislongerthan0"


#   handle including whitespace or @
def test_handle_invalid_char():
    clear_v2()
    user1 = auth_register_v2("shen@league.com", "goodpass123", "shen", "@ nia")
    
    user = user_profile_v2(user1['token'], user1['auth_user_id'])['user']
    assert user['handle_str'] == "shennia"
