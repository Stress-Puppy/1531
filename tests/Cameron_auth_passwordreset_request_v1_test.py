import pytest

from src.auth import auth_register_v2, auth_passwordreset_request_v1
from src.other import clear_v2
from src.error import InputError, AccessError

    
def test_auth_passwordreset_request_v1_valid():
    clear_v2()
    auth_register_v2("wed11bcactus@gmail.com", "iteration3", "cameron", "burrell")
    email = "wed11bcactus@gmail.com"
    assert auth_passwordreset_request_v1(email) == {}
    
def test_no_users():
    clear_v2()
    email = "wed11bcactus@gmail.com"
    assert auth_passwordreset_request_v1(email) == {}

def test_unused_email():
    clear_v2()
    auth_register_v2("wed11bcactus@gmail.com", "iteration3", "cameron", "burrell")
    email = "wed11baero@gmail.com"
    assert auth_passwordreset_request_v1(email) == {}