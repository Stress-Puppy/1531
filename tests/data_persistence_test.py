import pytest
from src.helpers import package_data, write_data, read_data, erase_data
from src.other import clear_v2
from src.auth import auth_register_v2, auth_passwordreset_request_v1
from src.channels import channels_create_v2
from src.dm import dm_create_v1
from src.message import message_senddm_v1

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
def crt_channel():
    def _create_channel(token, is_public):
        return channels_create_v2(token, 'channel_1', is_public)
    return _create_channel

# Test basic functionality of data persistence helper functions
def test_write_data(reg_user, crt_channel, email):
    clear_v2()
    token = reg_user(0)['token']
    u_id_1 = reg_user(1)['auth_user_id']

    dm_id = dm_create_v1(token, [u_id_1])['dm_id']

    message_senddm_v1(token, dm_id, "Test")

    crt_channel(token, True)

    auth_passwordreset_request_v1(email(0))

    data_pre_write = package_data()

    write_data()
    read_data()

    data_post_write = package_data()

    assert data_pre_write == data_post_write
    # Check that data structures in data.py are identical before and after writing to
    # and reading from the data.p file

def test_read_empty_file():
    clear_v2()
    data_pre_read = package_data()
    read_data()
    data_post_read = package_data()
    assert data_post_read == data_pre_read
    # Data before reading from a blank data.p file should be unchanged by reading from the file

def test_erase_data(reg_user):
    clear_v2()
    data_post_clear = package_data()
    reg_user(0)['token'] # Create some data
    write_data()
    erase_data()
    read_data()
    data_post_erase = package_data()
    assert data_post_erase == data_post_clear
    # Data following erasure and reading from a blank file should be at default values
