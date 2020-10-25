import discord
from database import Guild, User
from sqlalchemy.orm.exc import NoResultFound

del_time = 30

async def get_user(user_id, db): #Add use if not in db
    """Retrieve User from the database, or create an entry for one

    Parameters
    ----------
    user_id : int
        Discord user ID to search for
    db : Session
        SQLAlchemy database session to query
    """

    user = db.query(User).filter(User.id==user_id).one_or_none() #Get the matching record
    if user is None: #If no User is found, create one
        user = User(id=user_id)
        db.add(user)
        db.commit()
    return user

async def checkGuild(in_guild, db) -> Guild:
    """Retrieve Guild from the database, or create and entry for one

    Parameters
    ----------
    in_guild : Guild
        Discord guild or Database guild to search for
    db : Session
        SQLAlchemy database session to query
    """

    guild = db.query(Guild).filter(Guild.id==in_guild.id).one_or_none()
    if guild is None:
        guild = Guild(id=in_guild.id)
        #Find and set default channels to monitor
        guild.channel = await get_default_channel(in_guild)
        guild.channel_playing = await get_default_playing(in_guild)
        db.add(guild)
        db.commit()
    return guild

async def get_default_channel(in_guild):
    """Search for a suitable waiting channel on new guild entry

    Parameters
    ----------
    in_guild : 
        Discord Guild to determine default channel for
    """

    channels = in_guild.voice_channels
    words = ["lobby","wait","queue"]
    chans = [c for c in channels if [d for d in words if d in c.name.lower()]] #Find list of channels matching words
    chan = chans[0] if chans else channels[0]
    return chan.id

async def get_default_playing(in_guild):
    """Search for a suitable waiting channel on new guild entry

    Parameters
    ----------
    in_guild : 
        Discord Guild to determine default channel for
    """

    channels = in_guild.voice_channels
    words = ["active","play","stream"]
    chans = [c for c in channels if [d for d in words if d in c.name.lower()]] #Find list of channels matching words
    chan = chans[0] if chans else channels[0]
    return chan.id

async def check_auth(ctx, bot):
    """Check if user is authorised to use privileged commands

    Parameters
    ----------
    ctx : Context
        Context from Discord message
    bot : commands.Bot
        Bot object to use to check for permissions
    """
    owner = (await bot.application_info()).owner
    try:
        manrole = ctx.guild.get_role((await checkGuild(ctx.guild)).management_role)
    except:
        manrole = None
    allowed = ctx.message.author == owner or \
    ctx.message.author.guild_permissions.administrator or \
    (not manrole is None and manrole in ctx.message.author.roles)
    return allowed

async def delete_own(guild_d, msg_id, db) -> None:
    """Delete last sent lobby message

    Parameters
    ----------
    guild_d : discord.Guild
        Discord Guild to update
    db : Session
        SQLAlchemy database session to query
    """

    guild = await checkGuild(guild_d, db=db)
    msg = None
    for c in guild_d.text_channels: #This block could be cleaner?
        try:
            msg = await c.fetch_message(msg_id)
        except:
            pass
        if msg:
            break
    if msg is None:
        return
    await msg.delete()
