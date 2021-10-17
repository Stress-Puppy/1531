import pytest

from src.auth import auth_register_v2
from src.user import user_stats_v1
from src.channel import channel_join_v2
from src.channels import channels_create_v2
from src.message import message_send_v2, message_senddm_v1
from src.dm import dm_create_v1
from src.other import clear_v2
from src.error import AccessError

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
def involvement():
    def _involvement(chs_joined, dms_joined, msgs_sent, ch_total, dm_total, msg_total):
        totals = ch_total + dm_total + msg_total
        inv = 0
        if totals > 0:
            inv = (chs_joined + dms_joined + msgs_sent) / totals
        return inv # Assume returns 0 if Dreams is empty
    return _involvement

def test_empty_dreams_no_involvement(reg_user, involvement):
    clear_v2()

    token = reg_user(0)['token']

    user_stats = user_stats_v1(token)['user_stats']

    assert len(user_stats['channels_joined']) == 0
    assert len(user_stats['dms_joined']) == 0
    assert len(user_stats['messages_sent']) == 0
    assert user_stats['involvement_rate'] == involvement(0, 0, 0, 0, 0, 0)

def test_non_empty_dreams_no_involvement(reg_user, crt_channel, crt_dm, send_msg, involvement):
    clear_v2()

    user_1_token = reg_user(0)['token']

    user_2 = reg_user(1)
    user_2_token = user_2['token']
    user_2_id = user_2['auth_user_id']

    channel_id = crt_channel(user_2_token)['channel_id']

    crt_dm(user_2_token, [user_2_id])

    send_msg(user_2_token, channel_id)

    user_stats = user_stats_v1(user_1_token)['user_stats']

    assert len(user_stats['channels_joined']) == 0
    assert len(user_stats['dms_joined']) == 0
    assert len(user_stats['messages_sent']) == 0
    assert user_stats['involvement_rate'] == involvement(0, 0, 0, 1, 1, 1)

def test_one_channel_dm_and_message_all_involved(reg_user, crt_channel, crt_dm, send_msg, involvement):
    clear_v2()

    user = reg_user(0)
    token = user['token']
    user_id = user['auth_user_id']

    channel_id = crt_channel(token)['channel_id']

    crt_dm(token, [user_id])

    send_msg(token, channel_id)

    user_stats = user_stats_v1(token)['user_stats']

    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 1
    assert user_stats['involvement_rate'] == involvement(1, 1, 1, 1, 1, 1)

def test_multi_channel_dm_and_messages_all_involved(reg_user, crt_channel, crt_dm, send_msg, involvement):
    clear_v2()

    user = reg_user(0)
    token = user['token']
    user_id = user['auth_user_id']

    crt_count = 10

    for _ in range(crt_count):
        channel_id = crt_channel(token)['channel_id']

        crt_dm(token, [user_id])

        send_msg(token, channel_id)

    user_stats = user_stats_v1(token)['user_stats']
    inv = involvement(crt_count, crt_count, crt_count, crt_count, crt_count, crt_count)

    assert user_stats['channels_joined'][-1]['num_channels_joined'] == crt_count
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == crt_count
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == crt_count
    assert user_stats['involvement_rate'] == inv

def test_multi_channel_dm_and_messages_half_involved(reg_user, crt_channel, crt_dm, send_msg, involvement):
    clear_v2()

    user_1_token = reg_user(0)['token']

    user_2 = reg_user(1)
    user_2_token = user_2['token']
    user_2_id = user_2['auth_user_id']

    crt_count = 10

    for _ in range(crt_count):
        # User is involved in half of all activities
        inv_channel_id = crt_channel(user_1_token)['channel_id']
        uninv_channel_id = crt_channel(user_2_token)['channel_id']

        crt_dm(user_1_token, [user_2_id])
        crt_dm(user_2_token, [user_2_id])

        send_msg(user_1_token, inv_channel_id)
        send_msg(user_2_token, uninv_channel_id)

    user_stats = user_stats_v1(user_1_token)['user_stats']
    inv = involvement(crt_count, crt_count, crt_count, 2*crt_count, 2*crt_count, 2*crt_count)

    assert user_stats['channels_joined'][-1]['num_channels_joined'] == crt_count
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == crt_count
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == crt_count
    assert user_stats['involvement_rate'] == inv

def test_invalid_token(reg_user):
    clear_v2()
    reg_user(0)
    with pytest.raises(AccessError):
        user_stats_v1("Invalid token")
