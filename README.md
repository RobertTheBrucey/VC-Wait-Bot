# VC-Wait-Bot

## To Do:
* Add a record command for default record type or both records
* Investigate issue where Northie Sub joins Northie discord then oohRemix discord and doesn't get roles
* File "/src/Lobby.py", line 322, in update_play
    nick = msg.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
    AttributeError: 'NoneType' object has no attribute 'display_name'
* Store records per person instead of per guild in case a record holder leaves the guild
* Implement DB migrations
    * Optimise by using a pre-container to migrate instead of the main container
* Handle the case of lobby channel and active channel being the same
* Allow AFK channel to not reset times
* Profile and optimise code
* Keep track of active time over a longer period (1 week or so) to help with regulars vs new players
* Cache owner in case of discord partial outage

## Done:
* Log when user joins VC
* Log when user leaves VC
* Print ordered list when asked
* Grace period for temporary DCs
* On restart add all users to queue if they weren't there
* Settings:
    * Wait channel
    * Grace period
    * Queue Role
* Twitch integration
* Longer term options
    * Play room
    * Time played
* Delete user's command text if bot has perms and user is unprivileged
* Reset wait times
* Need to handle the case of being added to a server while people are in the VC or when config changes

## Commands layout:
* Lobby
    * lobby
        * waiting
        * queue
    * active
        * playing

* Lobby Admin
    * grace
    * activechannel
        * playactive
    * lobbychannel
        * waitchannel
        * queuechannel
    * resetactive
        * resetplaying
    * resetlobby
        * resetwaiting
        * resetqueue
* Admin
    * config
    * cooldown
    * managerole
    * privilegecommands
* Twitch
    * addtwitch
    * removetwitch
    * showtwitch

