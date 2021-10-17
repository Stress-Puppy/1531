* Assume that user/stats/v1 always returns 0  for a user's involvement if there are no channels, dms or messages in Dreams (would otherwise cause division by zero error) 

* Assume that stats are updated at the smallest possible time scale I.e. whenever a new channel, dm or message is created 

* Assume that user/profile/uploadphoto/v1 raises an InputError if the x_start and/or y_start input is greater than or equal to the x_end and/or y_end inputs respectively. 

* Assume that user/profile/uploadphoto/v1 raises an InputError when the url fails to be connected to for any reason (raises a ConnectionError) 

* Assume that creating a channel/dm counts as joining it for the channels/dms_joined stats used in users_stats_v1 

* Assume that the channels joined/dms joined stats are based on the channels or dms that the user is currently in 

* Assume that the default profile photo for every user is "default.jpg" which will be found in the 'static/profile_photos' directory. The url to this image is also the default value for profile_img_url for each user upon registration. 

* /standup x will start the standup (x is a number), user does not need to type /standup x everytime they send message during the standup, all messages during this time period will be added to the standup messages 