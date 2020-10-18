import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database import Guild, User, Role, Base, TwitchChannel, Status
from config import getToken
import asyncio
import time
import datetime
from twitch_bot import T_Bot

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix='^', intents=intents)

engine = create_engine('sqlite:///db/app.db') #Change to persistent file eventually
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
db = Session()

t_bot = T_Bot(db)

#* Print position in queue when asked
#* On restart add all users to queue if they weren't there
#* Settings:
#    * Wait Role(s)

@bot.command(name='queue', description="Show the queue of players in the waiting channel.",
help="Show the queue of players in the waiting channel.", brief="Show the queue")
async def queue(ctx):
    guild = await checkGuild(ctx.guild, db=db)
    users = [ u for u in guild.users if u.waiting == Status.waiting ]
    tl = (guild.lastcall + guild.cooldown) - int(time.time())
    if (tl <= 0) or await check_auth(ctx) or guild.privcomms:
        if len(users) > 0:
            queue = "```yaml\nCurrent Queue:"
            i = 1
            for u in sorted(users, key=lambda x: x.jointime):
                nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
                queue += "\n" + str(i) + ": " + str(nick) + ": " + str(t)
                i += 1
            queue += "\nThis message will be auto updated until ^queue is used again\n```"
            if not guild.privcomms or await check_auth(ctx):
                guild.lastedit = (await ctx.channel.send(queue)).id
            else:
                await ctx.author.send(queue)
            if not await check_auth(ctx):
                guild.lastcall = int(time.time())
        else:
            if not guild.privcomms or await check_auth(ctx):
                guild.lastedit = (await ctx.channel.send("```yaml\nQueue is empty\n```")).id
            else:
                await ctx.author.send("```yaml\nQueue is empty\n```")
                try:
                    await ctx.message.delete()
                except:
                    pass
        db.commit()
    else:
        await ctx.channel.send("```yaml\nCommand on cooldown, please wait " + str(tl) + " seconds.\n```")

@bot.command(name='resetqueue', description="Reset the times for all users",
help="Resets all queue times.", brief="Reset queue times")
async def resetqueue(ctx):
    if await check_auth(ctx):
        guild = await checkGuild(ctx.guild, db=db)
        ct = int(time.time())
        for u in guild.users:
            u.jointime = ct
            u.leavetime = 0
        db.commit()
        await ctx.channel.send("```yaml\nAll queue times have been reset\n```")

@bot.command(name='resetplaying', description="Reset the times for all users",
help="Resets all playing times.", brief="Reset play times")
async def resetplaying(ctx):
    if await check_auth(ctx):
        guild = await checkGuild(ctx.guild, db=db)
        ct = int(time.time())
        for u in guild.users:
            u.jointime_playing = ct
            u.leavetime_playing = 0
        db.commit()
        await ctx.channel.send("```yaml\nAll playing times have been reset\n```")

@bot.command(name='privilegecommands', description="Toggle priviledge commands mode",
help="Toggles whether unprivileged users can use queue and playing", brief="Toggle privileged commands")
async def toggle_priv(ctx):
    if await check_auth(ctx):
        guild = await checkGuild(ctx.guild, db=db)
        guild.privcomms = not guild.privcomms
        db.commit
        if guild.privcomms:
            await ctx.channel.send("```yaml\nqueue and playing commands now DM unprivileged users\n```")
        else:
            await ctx.channel.send("```yaml\nqueue and playing commands can now be used by all users\n```")

@bot.command(name='waitchannel', description="Set the channel to monitor for waiting users",
help="Change the channel to monitor for waiting users", brief="Change wait channel")
async def waitchannel(ctx, arg):
    if (await check_auth(ctx)):
        opts = []
        for c in ctx.guild.voice_channels:
            if arg in c.name.lower():
                if arg == c.name.lower():
                    opts = [c]
                    break
                opts.append(c)
        if len(opts) == 1:
            guild = await checkGuild(ctx.guild, db=db)
            guild.channel = c.id 
            db.commit()
            await ctx.channel.send("```yaml\nWait channel set to " + c.name + "\n```")
        elif len(opts) == 0:
            await ctx.channel.send("```yaml\nNo channels match " + arg + ".\n```")
        else:
            chans = ""
            for c in opts:
                chans += c.name + "\n"
            await ctx.channel.send("```yaml\nToo many matches, please be more specific.\n" + chans + "```")

@bot.command(name='playing', description="Show the play time of current players.",
help="Show the play time of current players.", brief="Show the players")
async def playing(ctx):
    guild = await checkGuild(ctx.guild, db=db)
    users = [ u for u in guild.users if u.waiting == Status.playing ]
    tl = (guild.lastcall + guild.cooldown) - int(time.time())
    if (tl <= 0) or await check_auth(ctx) or guild.privcomms:
        if len(users) > 0:
            queue = "```yaml\nCurrent Players:"
            i = 1
            for u in sorted(users, key=lambda x: x.jointime_playing):
                nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                t = datetime.timedelta(seconds=(int(time.time()) - u.jointime_playing))
                queue += "\n" + str(i) + ": " + str(nick) + ": " + str(t)
                i += 1
            queue += "\n```"
            if not guild.privcomms or await check_auth(ctx):
                await ctx.channel.send(queue)
            else:
                await ctx.author.send(queue)
            if not await check_auth(ctx):
                guild.lastcall = int(time.time())
            db.commit()
        else:
            if not guild.privcomms or await check_auth(ctx):
                await ctx.channel.send("```yaml\nNo one is playing right now\n```")
            else:
                await ctx.author.send("```yaml\nNo one is playing right now\n```")
                try:
                    await ctx.message.delete()
                except:
                    pass
    else:
        await ctx.channel.send("```yaml\nCommand on cooldown, please wait " + str(tl) + " seconds.\n```")

@bot.command(name='playchannel', description="Set the channel to monitor for playing users",
help="Change the channel to monitor for playing users", brief="Change play channel")
async def playchannel(ctx, arg):
    if (await check_auth(ctx)):
        opts = []
        for c in ctx.guild.voice_channels:
            if arg in c.name.lower():
                if arg == c.name.lower():
                    opts = [c]
                    break
                opts.append(c)
        if len(opts) == 1:
            guild = await checkGuild(ctx.guild, db=db)
            guild.channel_playing = c.id 
            db.commit()
            await ctx.channel.send("```yaml\nWait channel set to " + c.name + "\n```")
        elif len(opts) == 0:
            await ctx.channel.send("```yaml\nNo channels match " + arg + ".\n```")
        else:
            chans = ""
            for c in opts:
                chans += c.name + "\n"
            await ctx.channel.send("```yaml\nToo many matches, please be more specific.\n" + chans + "```")


'''@bot.command(name='position')
async def position(ctx, arg):
    pass'''

@bot.command(name='cooldown', description="Set the cooldown of the queue command",
help="Set the cooldown of the queue command", brief="Change cooldown time")
async def set_cooldown(ctx, arg):
    if (await check_auth(ctx)):
        if arg.isdigit():
            guild = await checkGuild(ctx.guild, db=db)
            guild.cooldown = int(arg)
            db.commit()
            await ctx.channel.send("```yaml\nCooldown time changed to " + arg +" seconds\n```")
        else:
            await ctx.channel.send("```yaml\nError: Expected an integer for cooldown time\n```")

@bot.command(name='grace', description="Set the grace period in the case of temporary disconnections",
help="Set the grace period for disconnections", brief="Change DC grace period")
async def grace(ctx, arg):
    if (await check_auth(ctx)):
        if arg.isdigit():
            guild = await checkGuild(ctx.guild, db=db)
            guild.grace = int(arg)
            db.commit()
            await ctx.channel.send("```yaml\nGrace period changed to " + arg +" minutes\n```")
        else:
            await ctx.channel.send("```yaml\nError: Expected an integer for grace period\n```")

'''#@commands.check(check_auth)
@bot.command(name='allowrole')
async def allowrole(ctx, *args):
    pass

#@commands.check(check_auth)
@bot.command(name='denyrole')
async def denyrole(ctx, *args):
    pass
'''
@bot.command(name='managerole', description="(Optional) Set a role to manage this bot",
help="Set the role to manage this bot in additional to administrators", brief="Set bot controller role")
async def managerole(ctx, arg):
    if (await check_auth(ctx)):
        opts = []
        for c in ctx.guild.roles:
            if arg in c.name.lower():
                if arg == c.name.lower():
                    opts = [c]
                    break
                opts.append(c)
        if len(opts) == 1:
            guild = await checkGuild(ctx.guild, db=db)
            guild.management_role = c.id
            db.commit()
            await ctx.channel.send("```yaml\nManagement role set to " + c.name + "\n```")
        elif len(opts) == 0:
            await ctx.channel.send("```yaml\nNo roles match " + arg + ".\n```")
        else:
            chans = ""
            for c in opts:
                chans += c.name + "\n"
            await ctx.channel.send("```yaml\nToo many matches, please be more specific.\n" + chans + "```")

@bot.command(name='config', description="Show the current configuration",
help="Show the current configuration", brief="Show current config")
async def print_config(ctx):
    if (await check_auth(ctx)):
        string = "```yaml\nServer: "
        guild = await checkGuild(ctx.guild, db=db)
        string += bot.get_guild(guild.id).name + "\n"
        string += "Wait Channel: " + ctx.guild.get_channel(guild.channel).name + "\n"
        string += "Play Channel: " + ctx.guild.get_channel(guild.channel_playing).name + "\n"
        string += "Grace Period: " + str(guild.grace) + " minutes\n"
        string += "Cooldown Time: " + str(guild.cooldown) + " seconds\n"
        string += "Management role: " + str(ctx.guild.get_role(guild.management_role)) + "\n"
        string += "```"
        await ctx.channel.send(string)

@bot.command(name='addtwitch', description="Connect a Twitch channel",
help=f"Connect a Twitch channel for {t_bot.prefix}queue", brief="Connect a Twitch channel")
async def add_twitch(ctx):
    if await check_auth(ctx):
        guild = await checkGuild(ctx.guild, db=db)
        name = ctx.message.content.split(" ")[1]
        if name[0] == "#":
            name = name[1:]
        chan = db.query(TwitchChannel).filter(TwitchChannel.name==name).one_or_none()
        if chan is None: #Best case, Twitch channel not linked
            chan = TwitchChannel(name=name, guild=guild)
            if await t_bot.add_channel(chan):
                await ctx.send(f"```yaml\nTwitch channel {name} has been added.\nUse {t_bot.prefix}verifyqueue in Twitch chat to complete the connection\n```")
            else:
                await ctx.send(f"```yaml\nCould not find Twitch channel {name}")
        elif chan.verified: #Someone has already linked this Twitch channel
            await ctx.send(f"```yaml\nTwitch channel {name} has already been linked, use {t_bot.prefix}leavequeue in Twitch chat to remove existing connection\n```")
        else: #Twitch linked but not verified, reset the linking process
            chan.guild=guild
            if await t_bot.add_channel(chan):
                await ctx.send(f"```yaml\nTwitch channel {name} has been added.\nUse {t_bot.prefix}verifyqueue in Twitch chat to complete the connection\n```")
            else:
                await ctx.send(f"```yaml\nCould not find Twitch channel {name}")
        db.commit()

@bot.command(name='removetwitch', description="Remove a connected Twitch channel",
help=f"Remove a connected Twitch channel", brief="Remove a Twitch channel")
async def del_twitch(ctx):
    if await check_auth(ctx):
        guild = await checkGuild(ctx.guild, db=db)
        name = ctx.message.content.split(" ")[1]
        if name[0] == "#":
            name = name[1:]
        chan = db.query(TwitchChannel).filter(TwitchChannel.name==name).one_or_none()
        if chan is None:
            await ctx.send(f"```yaml\nCould not find Twitch channel {name}")
        else:
            if chan.guild == guild:
                await t_bot.del_channel(chan)
                db.delete(chan)
                await ctx.channel.send(f"```yaml\nTwitch channel {name} has been removed\n```")
            else:
                await ctx.channel.send(f"```yaml\nTwitch channel {name} is not linked to this server. Naughty!\n```")
        db.commit()

@bot.command(name='showtwitch', description="Show connected Twitch channels",
help=f"Show connected Twitch channels", brief="Show connected Twitch channels")
async def show_twitch(ctx):
    if await check_auth(ctx):
        guild = await checkGuild(ctx.guild, db=db)
        string = "```yaml\nLinked twitch channels:\n"
        verimsg = False
        if len(guild.twitch) > 0:
            for c in guild.twitch:
                string += c.name + " - " + ("Verified\n" if c.verified else "Unverified\n")
                if not c.verified:
                    verimsg = True
            if verimsg:
                string += f"A mod must use {t_bot.prefix}verifyqueue in twitch chat to verify channels\n"
            string += "```"
            await ctx.channel.send(string)
        else:
            await ctx.channel.send("```yaml\nNo twitch channels have been linked.\n```")

@bot.event #Requires Intents.voice_states to be enabled
async def on_voice_state_update(member, before, after):
    guild = await checkGuild(member.guild, db=db)
    user = await get_user(member.id, db=db)
    chanid = guild.channel
    chan = member.guild.get_channel(chanid)
    p_chan = member.guild.get_channel(guild.channel_playing)
    update = False
    if after.channel == chan and before.channel != chan: #Moved into waiting
        if user.guild != guild or ((int(time.time()) - user.leavetime) > (guild.grace * 60)):
            user.jointime = int(time.time())
        user.guild = guild
        guild.users.append(user)
        user.waiting = Status.waiting
        update = True
    elif after.channel == p_chan and before.channel != p_chan: #Moved into playing
        if user.guild != guild or ((int(time.time()) - user.leavetime_playing) > (guild.grace * 60)):
            user.jointime_playing = int(time.time())
        user.guild = guild
        guild.users.append(user)
        user.waiting = Status.playing
        update = True
    if before.channel == chan and after.channel != chan: #Left waiting
        user.leavetime = int(time.time())
        if after.channel != p_chan:
                user.waiting = Status.none
        user.guild = guild
        update = True
    elif before.channel == p_chan and after.channel != p_chan: #Left playing
        user.leavetime_playing = int(time.time())
        if after.channel != chan:
                user.waiting = Status.none
        user.guild = guild
        update = True
    db.commit()
    if update:
        await update_last(member.guild, db=db)

async def update_last(guild_d, db=db):
    guild = await checkGuild(guild_d, db=db)
    users = [ u for u in guild.users if u.waiting == Status.waiting ]
    msg = None
    for c in guild_d.text_channels:
        try:
            msg = await c.fetch_message(guild.lastedit)
        except:
            pass
        if not msg is None:
            break
    if msg is None:
        return
    try:
        tl = (msg.edited_at.timestamp() + guild.cooldown + 1) - int(time.time())
    except AttributeError:
        tl = 0
    if tl <= 0:
        if len(users) > 0:
            queue = "```yaml\nCurrent Queue:"
            i = 1
            for u in sorted(users, key=lambda x: x.jointime):
                nick = msg.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
                queue += "\n" + str(i) + ": " + str(nick) + ": " + str(t)
                i += 1
            queue += "\nThis message will be auto updated until ^queue is used again\n```"
            await msg.edit(content=queue)
        else:
            await msg.edit(content="```yaml\nQueue is empty\n```")

async def checkGuild(in_guild, db=db):
    guild = db.query(Guild).filter(Guild.id==in_guild.id).one_or_none()
    if guild == None:
        guild = Guild(id=in_guild.id)
        guild.channel = await get_default_channel(in_guild)
        guild.channel_playing = await get_default_playing(in_guild)
        db.add(guild)
        db.commit()
    return guild

async def get_default_channel(in_guild):
    channels = in_guild.voice_channels
    chan = channels[0]
    for c in channels:
        if "wait" in c.name.lower():
            chan = c
    return chan.id

async def get_default_playing(in_guild):
    channels = in_guild.voice_channels
    chan = channels[0]
    for c in channels:
        if "stream" in c.name.lower():
            chan = c
        elif "play" in c.name.lower():
            chan = c
    return chan.id

async def update_users(guild, db=db):
    guild_db = await checkGuild(guild, db=db)
    chan = guild.get_channel(guild_db.channel)
    chan_p = guild.get_channel(guild_db.channel_playing)
    members = chan.voice_states
    members_p = chan_p.voice_states
    for user in guild_db.users: #Remove users not in VC
        u = user.id
        if u not in {**members, **members_p}:
            user.leavetime = int(time.time())
            user.guild = guild_db
            user.waiting = Status.none
    for user in members: #Add users in waiting
        u = await get_user(user) #from DB
        if u not in guild_db.users:
            try:
                guild_db.users.append(u)
                u.waiting = Status.waiting
            except Exception as e:
                print(e)
            if (int(time.time()) - u.leavetime) > (guild_db.grace * 60):
                u.jointime = int(time.time())
    for user in members_p: #Add users in playing
        u = await get_user(user) #from DB
        if u not in guild_db.users:
            try:
                guild_db.users.append(u)
                u.waiting = Status.playing
            except Exception as e:
                print(e)
            if (int(time.time()) - u.leavetime_playing) > (guild_db.grace * 60):
                u.jointime_playing = int(time.time())
    db.commit()
    
async def get_user(user_id, db=db): #Add use if not in db
    try:
        user = db.query(User).filter(User.id==user_id).one()
    except NoResultFound:
        user = User(id=user_id)
        db.add(user)
        db.commit()
    return user

async def check_auth(ctx):
    allowed = False
    owner = (await bot.application_info()).owner
    manrole = ctx.guild.get_role((await checkGuild(ctx.guild)).management_role)
    if ctx.message.author == owner:
        allowed = True
    elif ctx.message.author.guild_permissions.administrator:
        allowed = True
    elif not manrole is None and manrole in ctx.message.author.roles:
        allowed = True
    return allowed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name="^help", type=discord.ActivityType.listening))
    await bot.wait_until_ready()
    for g in bot.guilds:
        await update_users(g, db=db)
    await t_bot.start()

if __name__ == "__main__":
    try:
        bot.run(getToken())
    except discord.LoginFailure:
        print("Login error.")
