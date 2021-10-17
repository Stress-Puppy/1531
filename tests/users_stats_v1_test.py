import pytest

from src.auth import auth_register_v2
from src.users import users_all_v1, users_stats_v1
from src.channel import channel_join_v2
from src.channels import channels_create_v2, channels_listall_v2
from src.message import message_send_v2, message_senddm_v1
from src.dm import dm_create_v1
from src.other import clear_v2
from src.error import AccessError

'''
Fetches the required statistics about the use of UNSW Dreams

Parameters:(token)
Return Type:{ dreams_stats }

Dictionary of shape {
     channels_exist: [{num_channels_exist, time_stamp}], 
     dms_exist: [{num_dms_exist, time_stamp}], 
     messages_exist: [{num_messages_exist, time_stamp}], 
     utilization_rate 
    }
'''

@pytest.fixture
def reg_user():
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_channel():
    def _create_channel(token):
        return channels_create_v2(token, 'channel', True)
    return _create_channel

@pytest.fixture
def crt_dm():
    def _create_dm(token, u_ids):
        return dm_create_v1(token, u_ids)
    return _create_dm

@pytest.fixture
def send_msg():
    def _send_message(token, channel_id):
        return message_send_v2(token, channel_id, "Test")
    return _send_message

@pytest.fixture
def send_dm():
    def _send_dm(token, dm_id):
        return message_senddm_v1(token, dm_id, "Test")
    return _send_dm

@pytest.fixture
def utilization():
    def _util(active_users, user_total):
        # num_users_who_have_joined_at_least_one_channel_or_dm / total_num_users
        inv = 0
        if user_total > 0:
            inv = active_users / user_total
        return inv # Assume returns 0 if Dreams is empty
    return _util

def test_empty_dreams(reg_user, utilization):
    clear_v2()

    token = reg_user(0)['token']

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 0
    assert len(users_stats['dms_exist']) == 0
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(0, 1)

def test_single_user_single_channel_full_util(reg_user, crt_channel, utilization):
    clear_v2()

    token = reg_user(0)['token']

    crt_channel(token)

    users_stats = users_stats_v1(token)['dreams_stats']

    assert users_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert len(users_stats['dms_exist']) == 0
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(1, 1)

def test_single_user_single_dm_full_util(reg_user, crt_dm, utilization):
    clear_v2()

    user = reg_user(0)
    token = user['token']
    user_id = user['auth_user_id']

    crt_dm(token, [user_id])

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 0
    assert users_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(1, 1)

def test_multi_user_no_channels(reg_user, utilization):
    clear_v2()

    token = reg_user(0)['token']

    user_count = 10
    for i in range(1, user_count):
        reg_user(i)

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 0
    assert len(users_stats['dms_exist']) == 0
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(0, user_count)

def test_multi_user_full_channel_util(reg_user, crt_channel, utilization):
    clear_v2()

    token = reg_user(0)['token']
    crt_channel(token)

    user_count = 10
    for i in range(1, user_count):
        user_token = reg_user(i)['token']
        crt_channel(user_token)

    users_stats = users_stats_v1(token)['dreams_stats']

    assert users_stats['channels_exist'][-1]['num_channels_exist'] == user_count
    assert len(users_stats['dms_exist']) == 0
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(user_count, user_count)

def test_multi_user_full_dm_util(reg_user, crt_dm, utilization):
    clear_v2()

    user = reg_user(0)
    token = user['token']
    user_id = user['auth_user_id']
    crt_dm(token, [user_id])

    dm_count = 10
    for i in range(1, dm_count):
        new_user = reg_user(i)
        new_user_token = new_user['token']
        new_user_id = new_user['auth_user_id']
        crt_dm(new_user_token, [new_user_id])

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 0
    assert users_stats['dms_exist'][-1]['num_dms_exist'] == dm_count
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(dm_count, dm_count)

def test_singe_dm_multi_message(reg_user, crt_dm, send_dm, utilization):
    clear_v2()

    user = reg_user(0)
    token = user['token']
    user_id = user['auth_user_id']
    dm_id = crt_dm(token, [user_id])['dm_id']

    msg_count = 10
    for _ in range(msg_count):
        send_dm(token, dm_id)

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 0
    assert len(users_stats['dms_exist']) == 1
    assert users_stats['messages_exist'][-1]['num_messages_exist'] == msg_count
    assert users_stats['utilization_rate'] == utilization(1, 1)

def test_single_channel_multi_message(reg_user, crt_channel, send_msg, utilization):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    msg_count = 10
    for _ in range(msg_count):
        send_msg(token, channel_id)

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 1
    assert len(users_stats['dms_exist']) == 0
    assert users_stats['messages_exist'][-1]['num_messages_exist'] == msg_count
    assert users_stats['utilization_rate'] == utilization(1, 1)

def test_partial_util_channels(reg_user, crt_channel, utilization):
    clear_v2()

    token = reg_user(0)['token']

    user_count = 10
    for i in range(1,user_count):
        new_user_token = reg_user(i)['token']
        if i % 2 == 0: # Only half of the users create channels
            crt_channel(new_user_token)

    channel_count = int(user_count/2-0.5) # Half of user count

    users_stats = users_stats_v1(token)['dreams_stats']

    assert users_stats['channels_exist'][-1]['num_channels_exist'] == channel_count
    assert len(users_stats['dms_exist']) == 0
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(channel_count, user_count)

def test_partial_util_dms(reg_user, crt_dm, utilization):
    clear_v2()

    token = reg_user(0)['token']

    user_count = 10
    for i in range(1,user_count):
        new_user = reg_user(i)
        new_user_token = new_user['token']
        new_user_id = new_user['auth_user_id']
        if i % 2 == 0: # Only half of the users create channels
            crt_dm(new_user_token, [new_user_id])

    dm_count = int(user_count/2-0.5) # Half of user count

    users_stats = users_stats_v1(token)['dreams_stats']

    assert len(users_stats['channels_exist']) == 0
    assert users_stats['dms_exist'][-1]['num_dms_exist'] == dm_count
    assert len(users_stats['messages_exist']) == 0
    assert users_stats['utilization_rate'] == utilization(dm_count, user_count)

def test_invalid_token(reg_user):
    clear_v2()
    reg_user(0)
    with pytest.raises(AccessError):
        users_stats_v1("Invalid_token")