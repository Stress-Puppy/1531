import pytest

from src.auth import auth_register_v2, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.other import clear_v2
from src.error import InputError, AccessError

def test_auth_passwordreset_reset_invalid_reset_code():
    clear_v2()
    auth_register_v2("wed11bcactus@gmail.com", "iteration3", "cameron", "burrell")
    email = "wed11bcactus@gmail.com"
    auth_passwordreset_request_v1(email)
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1("@#$$**!!", "hdwdssdw111")

def test_auth_passwordreset_reset_invalid_password_less_than_6_characters():
    clear_v2()
    auth_register_v2("wed11bcactus@gmail.com", "iteration3", "cameron", "burrell")
    email = "wed11bcactus@gmail.com"
    auth_passwordreset_request_v1(email)
    test_reset_code = "test"
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(test_reset_code, "hdwd")

    
