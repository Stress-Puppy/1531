from src.data import users, channels, next_channel_id, dreams_stats

from src.error import InputError, AccessError

from src.helpers import check_token, user_from_token, update_channel_stats, update_user_channel_stats


def channels_list_v2(token):
    '''
    <Provide a list of all channels (and their associated details) that the authorised user is part of>

    Arguments:
        <token>        (<string>)     - <User session token>

    Exceptions:
        AccessError - Occurs when the token is not a vaild token

    Return Value:
        Returns <{ channels }>      on <return the list of these channels that user is apart of>

    '''

    global users, channels
    check_token(token)
    auth_user_id = user_from_token(token)['u_id']

    channelList = []

    # search all the channel 
    for channel in channels:
        # if the auth user is a menber of this channel, add this channel to the channellist
        if auth_user_id in channel['all_members']:
            channelList.append({ 'channel_id' : channel['channel_id'], 'name': channel['name']})

    # if this user is not in any channel, just return the empty channellist list
    return { 'channels' : channelList }
    

def channels_listall_v2(token):
    """Summary
        Provide a list of all channels (and their associated details)
    Args:
        token (string): A user session token
    
    Returns:
        Dictionary: Contains the list of all channels, and their associated details

    Raises:
        AccessError: When an invalid token is given
    """
    check_token(token)

    # Collect channel information for each channel
    output = []
    for channel in channels:
        channel_details = { 'channel_id' : channel['channel_id'], 'name' : channel['name'] }
        output.append(channel_details)

    return { 'channels' : output }


def channels_create_v2(token, name, is_public):
    '''
    <this function will create a channel with the auth_user_id being the creater of the channel, it will give the name of the channel and then set it to public or private>

    Arguments:
        <token>        (<string>)     - <User session token>
        <name>         (<string>)     - <this is the name of the new channel which will be created in this function>
        <is_public>    (<boolean>)    - <this parameter will discrible if this channel is a public channel or a private channel>

    Exceptions:
        InputError  - Occurs when name is more than 20 characters long
        AccessError - Occurs when the token is not a vaild token
    Return Value:
        Returns <{ channel_id }>       on <when channel is successfully created, return the id of this new channel>
    
    '''

    global users, channels, next_channel_id

    check_token(token)
    auth_user = user_from_token(token)
    auth_user_id = auth_user['u_id']

    # Name is more than 20 characters long
    if len(name) > 20:
        raise InputError(f"The name entered: {name} is more than 20 characters long")

    channel_id = next_channel_id['id']

    next_channel_id['id'] += 1

    # create a new channel
    new_channel = {
        'channel_id' : channel_id,
        'name' : name,
        'owner_members' : [auth_user_id],
        'all_members': [auth_user_id],
        'is_public' : is_public,
        'messages' : [],
        'standup' : { 
                      'is_active' : False, 
                      'creator' :0, 
                      'messages' : [], 
                      'time_finish' : 0
                    }
    }
    
    # add the new channel to the channels list
    channels.append(new_channel)

    update_channel_stats() # Record newly increased number of channels in Dreams stats

    auth_user['channels'].append(channel_id) # Add the channel's id to the user's list of channels
    update_user_channel_stats(auth_user_id)

    return { 'channel_id' : new_channel['channel_id'] }
