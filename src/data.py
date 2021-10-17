next_u_id = {'id' : 0}
users = []
'''
{ 'u_id' : 0, 
  'handle_str' : 'lachyscott23', 
  'name_first' : '', 
  'name_last' : '', 
  'email' : 'lachy@gmail.com', 
  'password' : '12342323', 
  'channels' : [1,2,3,4], 
  'dms' : [1,2,3,4],
  'permission' : 0/1/2, 
  'profile_img_url' : <url>
  'stats' : {
     'channels_joined' : [{num_channels_joined, time_stamp}],
     'dms_joined' : [{num_dms_joined, time_stamp}], 
     'messages_sent' : [{num_messages_sent, time_stamp}]
    } 
  }
'''
next_channel_id = {'id' : 0}
channels = []
# { 'channel_id' : 0, 'name' : '', 'owner_members' : [], 'all_members' : [], 'is_public' : False, 'messages' : [], 'standup' : {'is_active' : True/False, 'creator' : <u_id>, 'messages' : [], 'time_finish' : <timestamp>}}
next_message_id = {'id' : 0}
messages = []
future_messages = []
# { 'message_id', 'channel_id', 'dm_id', 'author_id', 'message', 'time_created', 'reacts' : [<u_ids>], 'is_pinned' : True/False] }
next_dm_id = {'id' : 0}
dms = []
# { 'dm_id', 'name', 'creator', 'members', 'messages' }
tokens = []
# All currently active user session tokens
notifications = []
# Stores notifications for each user {'u_id' : 1, 'notifications' : []}
# { notifications } ({channel_id，dm_id，notification_message}) dictionary of notifications
dreams_stats = { 'channels_exist' : [], 'dms_exist' : [], 'messages_exist' : [] }
reset_codes = []
# [{'u_id' : 0, 'email' : 'checksameemail@gmail.com','code' : 123456, 'name' : 'cameron'}]
SECRET = 'DeepestDarkestSecret'
