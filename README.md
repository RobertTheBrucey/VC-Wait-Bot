# VC-Wait-Bot

## To Do:
* Investigate issue where Northie Sub joins oohRemix before Northie discord and doesn't get roles
* Store records per person instead of per guild in case a record holder leaves the guild
* Implement DB migrations
    * Optimise by using a pre-container to migrate instead of the main container
* Handle the case of lobby channel and active channel being the same
* Allow AFK channel to not reset times
* Profile and optimise code
* Keep track of active time over a longer period (1 week or so) to help with regulars vs new players

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

