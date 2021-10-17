from datetime import datetime, timezone, timedelta
from src.data import channels
from src.helpers import check_token, user_from_token, valid_channel, is_channel_member, find_channel
from src.error import InputError, AccessError

'''
Sending a message to get buffered in the standup queue, assuming a standup is currently active

Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
        message (string): a message string 
Returns: 
        empty dictionary 

InputError when any of:
    Channel ID is not a valid channel
    Message is more than 1000 characters (not including the username and colon)
    An active standup is not currently running in this channel
AccessError when
    The authorised user is not a member of the channel that the message is within
'''

def standup_send_v1(token, channel_id, message):
    
    check_token(token)

    sender = user_from_token(token)
    u_id = sender['u_id']

    # InputError when Channel ID is not a valid channel
    if valid_channel(channel_id) == False:
        raise InputError(f"Channel ID {channel_id} is not a valid channel")

    # InputError when Message is more than 1000 characters (not including the username and colon)
    if len(message) > 1000:
        raise InputError(f"Message more than 1000 characters") 

    # AccessError when The authorised user is not a member of the channel that the message is within
    if is_channel_member(u_id, channel_id) == False:
        raise AccessError(f"The authorised user {u_id} is not a member of the channel that the message is within") 

    for channel in channels:
        if channel['channel_id'] == channel_id:
            # InputError when An active standup is not currently running in this channel
            if channel['standup']['is_active'] == False:
                raise InputError("An active standup is not currently running in this channel") 
            else:
                message_dict = {'author_handle' : sender['handle_str'], 'message' : message}
                channel['standup']['messages'].append(message_dict)

    return {}

'''
For a given channel, return whether a standup is active in it, and what time the standup 
finishes. If no standup is active, then time_finish returns None

Parameters:(token, channel_id)
Return Type:{ is_active, time_finish }

InputError when any of:
    Channel ID is not a valid channel
'''

def standup_active_v1(token, channel_id):
    """Summary
        For a given channel, return whether a standup is active in it, and what time the standup 
        finishes. If no standup is active, then time_finish returns None
    Args:
        token (string): A user session token
        channel_id (int): A channel id number
    
    Returns:
        output: Dictionary of the form { is_active, time_finish }, where is_active is a Boolean
                and time_finish is a time stamp if is_active is True, else None
    
    Raises:
        InputError: When the channel id parameter does not refer to a valid channel
        AccessError: When the token parameter is an invalid jwt token
    """
    check_token(token)

    target_channel = find_channel(channel_id)
    if target_channel == {}:
        raise InputError(f'Channel ID {channel_id} is not a valid channel')

    channel_standup = target_channel['standup']
    is_active = channel_standup['is_active']
    t_finish = channel_standup['time_finish']

    output = {
               'is_active' : is_active, 
               'time_finish' : t_finish if is_active else None
             }
    return output

def standup_start_v1(token, channel_id, length):
    '''
    Summary:
       For a given channel, 
       start the standup period whereby for the next "length" seconds if someone calls "standup_send" with a message, 
       it is buffered during the X second window then at the end of the X second window a message will be added to the message queue 
       in the channel from the user who started the standup. X is an integer that denotes the number of seconds that the standup occurs for
    Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
        length (int): A length of how long the standup runs
    Returns: 
        dictionary which contains the time_finished 
    Raises:
        InputError when:
            Channel ID is not a valid channel
            An active standup is currently running in this channel
        AccessError when:
            Authorised user is not in the channel
    '''
    global channels
    check_token(token)
    
    if valid_channel(channel_id) == False:
        raise InputError(f'Channel ID {channel_id} is not a valid channel')
    
    auth_user_id = user_from_token(token)['u_id']

    if is_channel_member(auth_user_id, channel_id) == False:
        raise AccessError(f'Authorised user is not in the channel')

    current_channel = find_channel(channel_id)
    
    if current_channel['standup']['is_active'] == True:
        raise InputError(f'An active standup is currently running in this channel')
    
    standup_period_finish = datetime.now(timezone.utc) + timedelta(seconds=length)
    timestamp = standup_period_finish.replace(tzinfo=timezone.utc).timestamp()
    
    # what will i add to the message here
    #dummy = ''
    #message_id = message_sendlater_v1(token, channel_id, dummy, timestamp)
    #message id here or standup send
    #standup_info = {}
    #create the standup dicitonary in channel create 
    current_channel['standup']['is_active'] = True
    current_channel['standup']['creator'] = auth_user_id
    current_channel['standup']['messages'] = []
    current_channel['standup']['time_finish'] = timestamp
    
  
    #current_channel['standup'] = standup_info
    
    return {
        'time_finish': timestamp
    }
