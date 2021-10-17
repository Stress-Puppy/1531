from src.data import users, channels, tokens, notifications
from src.helpers import check_token, user_from_token

def notifications_get_v1(token):
    """Summary
        Return the user's most recent 20 notifications
    Args:
        token (string): User session token
    
    Returns:
        { notifications } ({channel_id，dm_id，notification_message}) dictionary of notifications
    
    Raises:
        AccessError: the token entered is not a valid token
    """
    check_token(token)
    u_id = user_from_token(token)['u_id']
    output = []

    # search all teh notifications, and find the notifications which were sent by user(u_id)
    for noti_list in notifications:
        if noti_list['u_id'] == u_id:
            notis = noti_list['notifications']
            # record all the user's most recent 20 notifications
            if len(notis) <= 20:
                output = list(reversed(notis))
            else:
                output = list(reversed(notis))[:20]
    return { 'notifications' : output }
