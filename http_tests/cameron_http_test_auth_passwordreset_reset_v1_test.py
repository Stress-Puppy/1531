import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def InputError():
    return 400

def test_auth_passwordreset_reset_invalid_reset_code(InputError):
    clear_v2()
    auth_register_v2("fakeexampleemail@example.com", "iteration3", "cameron", "burrell")
    email = "fakeexampleemail@example.com"
    auth_passwordreset_request_v1(email)
    auth_passwordreset_reset_request = auth_passwordreset_reset_v1("@#$$**!!", "hdwdssdw111")
    assert auth_passwordreset_reset_request.status_code == InputError
    
def test_auth_passwordreset_reset_invalid_password_less_than_6_characters(InputError):
    clear_v2()
    auth_register_v2("fakeexampleemail@example.com", "iteration3", "cameron", "burrell")
    email = "fakeexampleemail@example.com"
    auth_passwordreset_request_v1(email)
    test_reset_code = "test"
    auth_passwordreset_reset_request = auth_passwordreset_reset_v1(test_reset_code, "hdwd")
    assert auth_passwordreset_reset_request.status_code == InputError

