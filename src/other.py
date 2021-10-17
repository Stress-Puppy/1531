from src.data import next_u_id, users, next_channel_id, channels, next_message_id, messages, next_dm_id, dms, tokens, dreams_stats, notifications, reset_codes
from src.error import InputError
from src.helpers import check_token, user_from_token, find_channel, find_dm, erase_data
import os

def clear_v2():
    """Summary
    Resets the internal data of the system (users, channels, dms and messages)
    """
    global users, channels, dms, messages, tokens, notifications, next_u_id, next_channel_id, next_dm_id, next_message_id
    
    next_u_id['id'] = 0
    users.clear()

    next_channel_id['id'] = 0
    channels.clear()

    next_dm_id['id'] = 0
    dms.clear()

    next_message_id['id'] = 0
    messages.clear()

    tokens.clear()

    notifications.clear()

    # Clear each data list in dreams_stats dict
    for lst in dreams_stats.values():
        lst.clear()

    reset_codes.clear()

    # Delete all profile photos excluding the default one
    profile_photos_directory = 'static/profile_photos'
    for filename in os.listdir(profile_photos_directory):
        if filename != 'default.jpg':
            filepath = os.path.join(profile_photos_directory, filename)
            os.remove(filepath)

    erase_data()
    return {}

def search_v2(token, query_str):

    """Summary
        Given a query string, return a collection of messages in all of the channels/DMs that the user has joined that match the query
    Args:
        token (string): A user session token
        query_str (string): a string for search message
    
    Returns:
        Dictionary: { messages } ({ message_id, u_id, message, time_created })  Contains the imformation of messages
    
    Raises:
        InputError: query_str is above 1000 characters
    """
    query_str = query_str.lower()

    # InputError: query_str is above 1000 characters
    if len(query_str) > 1000:
        raise InputError("query_str is above 1000 characters")
    
    check_token(token)
    auth_user_id = user_from_token(token)['u_id']
    
    output = []
    # search all the messages
    for message in messages:
        user_is_member = False

        # if this message is send to the channel, find the channel
        if message['channel_id'] != -1:
            channel = find_channel(message['channel_id'])
            user_is_member = (auth_user_id in channel['all_members'] and query_str in message['message'].lower())
        # if this message is send to the dm, find the dm
        else:
            dm = find_dm(message['dm_id'])
            user_is_member = (auth_user_id in dm['members'] and query_str in message['message'].lower())
       
        # list all the detail of this messagen, and append it to the putput
        if user_is_member:
            react_dict = { 'react_id' : 1,
                           'u_ids' : message['reacts'],
                           'is_this_user_reacted' : auth_user_id in message['reacts'] }

            message_detail = { 'message_id' : message['message_id'],
                               'u_id' : message['author_id'], 
                               'message' : message['message'], 
                               'time_created' :  message['time_created'], 
                               'reacts' : [react_dict],
                               'is_pinned' : message['is_pinned']}
            output.append(message_detail)
    return { 'messages': output}
