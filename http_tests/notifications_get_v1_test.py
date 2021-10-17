import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def u_handle():
    def _user_handle(num):
        return f"firstname{num}lastname{num}"
    return _user_handle

# Tags a user in a message and returns the message contents
@pytest.fixture
def tag_message():
    def _tag_message(token, channel_id, channel_num, tagger_num, tagee_num, message_num):
        message_text = f"@firstname{tagee_num}lastname{tagee_num} {message_num}"
        message_send_v2(token, channel_id, message_text)
        return f"firstname{tagger_num}lastname{tagger_num} tagged you in channel_{channel_num}: {message_text[0:20]}"
    return _tag_message

# Tags a user in a dm and returns its dm_id and contents
@pytest.fixture
def tag_dm():
    def _tag_dm(token, dm, tagger_num, tagee_num, dm_num):
        dm_text = f"@firstname{tagee_num}lastname{tagee_num} {dm_num}"
        message_senddm_v1(token, dm['dm_id'], dm_text)
        return f"firstname{tagger_num}lastname{tagger_num} tagged you in {dm['dm_name']}: {dm_text[0:20]}"
    return _tag_dm

@pytest.fixture
def crt_channel():
    def _create_channel(token, num):
        return channels_create_v2(token, f'channel_{num}', True)
    return _create_channel

@pytest.fixture
def ch_add_str(): # Notification message sent when user is added to a channel
    def _channel_add_str(handle, num):
        return f"{handle} added you to channel_{num}"
    return _channel_add_str

@pytest.fixture
def AccessError():
    return 403

def test_single_channel_add(reg_user, u_handle, crt_channel, ch_add_str):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    channel_id = crt_channel(user_1_token, 0)['channel_id']
    channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == 1
    notif = notifs[0]
    assert notif['channel_id'] == channel_id
    assert notif['dm_id'] == -1
    assert notif['notification_message'] == ch_add_str(u_handle(0), 0)

def test_fewer_than_20_channel_adds(reg_user, u_handle, crt_channel, ch_add_str):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    add_count = 10
    channel_ids = []
    for i in range(add_count):
        channel_id = crt_channel(user_1_token, i)['channel_id']
        channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
        channel_ids.append(channel_id)
    channel_ids.reverse()
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == add_count
    for i in range(add_count):
        print(notifs[i])
        assert notifs[i]['channel_id'] == channel_ids[i]
        assert notifs[i]['dm_id'] == -1
        assert notifs[i]['notification_message'] == ch_add_str(u_handle(0), add_count-i-1)

def test_twenty_channel_adds(reg_user, u_handle, crt_channel, ch_add_str):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    add_count = 20
    channel_ids = []
    for i in range(add_count):
        channel_id = crt_channel(user_1_token, i)['channel_id']
        channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
        channel_ids.append(channel_id)
    channel_ids.reverse()
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == add_count
    for i in range(add_count):
        print(notifs[i])
        assert notifs[i]['channel_id'] == channel_ids[i]
        assert notifs[i]['dm_id'] == -1
        assert notifs[i]['notification_message'] == ch_add_str(u_handle(0), 19-i)

def test_more_than_twenty_channel_adds(reg_user, u_handle, crt_channel, ch_add_str):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    add_count = 21
    channel_ids = []
    for i in range(add_count):
        channel_id = crt_channel(user_1_token, i)['channel_id']
        channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
        channel_ids.append(channel_id)
    channel_ids.reverse()
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == add_count - 1
    for i in range(len(notifs)):
        assert notifs[i]['channel_id'] == channel_ids[i]
        assert notifs[i]['dm_id'] == -1
        assert notifs[i]['notification_message'] == ch_add_str(u_handle(0), 20-i)

def test_single_channel_tag(reg_user, u_handle, crt_channel, tag_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    channel_id = crt_channel(user_1_token, 0)['channel_id']
    channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
    message_text = tag_message(user_1_token, channel_id, 0, 0, 1, 0)
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == 2
    notif = notifs[0]
    assert notif['channel_id'] == channel_id
    assert notif['dm_id'] == -1
    assert notif['notification_message'] == message_text

def test_multiple_channel_tag(reg_user, u_handle, crt_channel, tag_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    channel_id = crt_channel(user_1_token, 0)['channel_id']
    channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
    message_count = 10
    messages_texts = []
    for i in range(message_count):
        messages_texts.append(tag_message(user_1_token, channel_id, 0, 0, 1, i))
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == message_count + 1
    for i in reversed(range(message_count)):
        assert notifs[i]['channel_id'] == channel_id
        assert notifs[i]['dm_id'] == -1
        assert notifs[i]['notification_message'] == messages_texts[i]

def test_twenty_channel_tag(reg_user, u_handle, crt_channel, tag_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    channel_id = crt_channel(user_1_token, 0)['channel_id']
    channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
    message_count = 20
    messages_texts = []
    for i in range(message_count):
        messages_texts.append(tag_message(user_1_token, channel_id, 0, 0, 1, i))
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == message_count
    for i in reversed(range(message_count)):
        assert notifs[i]['channel_id'] == channel_id
        assert notifs[i]['dm_id'] == -1
        assert notifs[i]['notification_message'] == messages_texts[i]

def test_more_than_twenty_channel_tag(reg_user, u_handle, crt_channel, tag_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    channel_id = crt_channel(user_1_token, 0)['channel_id']
    channel_invite_v2(user_1_token, channel_id, user_2['auth_user_id'])
    message_count = 21
    messages_texts = []
    for i in range(message_count):
        messages_texts.append(tag_message(user_1_token, channel_id, 0, 0, 1, i))
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == message_count - 1
    for i in reversed(range(message_count-1)):
        assert notifs[i]['channel_id'] == channel_id
        assert notifs[i]['dm_id'] == -1
        assert notifs[i]['notification_message'] == messages_texts[i+1]

def test_single_dm_tag(reg_user, u_handle, crt_channel, tag_dm):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    dm = dm_create_v1(user_1_token, [user_2['auth_user_id']])
    dm_text = tag_dm(user_1_token, dm, 0, 1, 0)
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == 2
    notif = notifs[0]
    assert notif['channel_id'] == -1
    assert notif['dm_id'] == dm['dm_id']
    assert notif['notification_message'] == dm_text

def test_multiple_dm_tag(reg_user, u_handle, crt_channel, tag_dm):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    dm = dm_create_v1(user_1_token, [user_2['auth_user_id']])
    dm_count = 10
    dms_texts = []
    for i in range(dm_count):
        dms_texts.append(tag_dm(user_1_token, dm, 0, 1, i))
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == dm_count + 1
    for i in reversed(range(dm_count)):
        assert notifs[i]['channel_id'] == -1
        assert notifs[i]['dm_id'] == dm['dm_id']
        assert notifs[i]['notification_message'] == dms_texts[i]

def test_twenty_dm_tag(reg_user, u_handle, crt_channel, tag_dm):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    dm = dm_create_v1(user_1_token, [user_2['auth_user_id']])
    dm_count = 20
    dms_texts = []
    for i in range(dm_count):
        dms_texts.append(tag_dm(user_1_token, dm, 0, 1, i))
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == dm_count
    for i in reversed(range(dm_count)):
        assert notifs[i]['channel_id'] == -1
        assert notifs[i]['dm_id'] == dm['dm_id']
        assert notifs[i]['notification_message'] == dms_texts[i]

def test_more_than_twenty_dm_tag(reg_user, u_handle, crt_channel, tag_dm):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2 = reg_user(1)
    dm = dm_create_v1(user_1_token, [user_2['auth_user_id']])
    dm_count = 21
    dms_texts = []
    for i in range(dm_count):
        dms_texts.append(tag_dm(user_1_token, dm, 0, 1, i))
    notifs = notifications_get_v1(user_2['token'])['notifications']
    assert len(notifs) == dm_count - 1
    for i in reversed(range(dm_count-1)):
        assert notifs[i]['channel_id'] == -1
        assert notifs[i]['dm_id'] == dm['dm_id']
        assert notifs[i]['notification_message'] == dms_texts[i+1]

def test_invalid_token(reg_user, AccessError):
    clear_v2()
    reg_user(0)
    notification_request = notifications_get_v1("Invalid token")
    assert notification_request.status_code == AccessError
