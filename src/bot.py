import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database import Guild, User, Role, Base
from config import getToken
import asyncio
import time
import datetime

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix='^', intents=intents)

engine = create_engine('sqlite:///db/app.db') #Change to persistent file eventually
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
db = Session()

#* Print position in queue when asked
#* On restart add all users to queue if they weren't there
#* Settings:
#    * Wait Role(s)

@bot.command(name='queue', description="Show the queue of players in the waiting channel.",
help="Show the queue of players in the waiting channel.", brief="Show the queue")
async def queue(ctx):
    guild = await checkGuild(ctx.guild, db=db)
    users = guild.users
    if len(users) > 0:
        queue = "```yaml\nCurrent Queue:"
        i = 1
        for u in sorted(users, key=lambda x: x.jointime):
            nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
            t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
            queue += "\n" + str(i) + ": " + str(nick) + ": " + str(t)
            i += 1
        queue += "\n```"
        await ctx.channel.send(queue)
    else:
        await ctx.channel.send("```yaml\nQueue is empty\n```")
    

'''@bot.command(name='position')
async def position(ctx, arg):
    pass'''

@bot.command(name='grace', description="Set the grace period in the case of temporary disconnections",
help="Set the grace period for disconnections", brief="Change DC grace period")
async def grace(ctx, arg):
    if (check_auth(ctx)):
        if arg.isdigit():
            guild = await checkGuild(ctx.guild, db=db)
            guild.grace = int(arg)
            db.commit()
            await ctx.channel.send("```yaml\nGrace period changed to " + arg +"\n```")
        else:
            await ctx.channel.send("```yaml\nError: Expected an integer for grace period\n```")

@bot.command(name='waitchannel', description="Set the channel to monitor for waiting users",
help="Change the channel to monitor for waiting users", brief="Change wait channel")
async def waitchannel(ctx, arg):
    if (check_auth(ctx)):
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
    if (check_auth(ctx)):
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
    if (check_auth(ctx)):
        string = "```yaml\nServer: "
        guild = await checkGuild(ctx.guild, db=db)
        string += bot.get_guild(guild.id).name + "\n"
        string += "Wait Channel: " + ctx.guild.get_channel(guild.channel).name + "\n"
        string += "Grace Period: " + str(guild.grace) + " minutes\n"
        string += "Management role: " + str(ctx.guild.get_role(guild.management_role)) + "\n"
        string += "```"
        await ctx.channel.send(string)

@bot.event #Requires Intents.voice_states to be enabled
async def on_voice_state_update(member, before, after):
    guild = await checkGuild(member.guild, db=db)
    user = await get_user(member.id, db=db)
    chanid = guild.channel
    chan = member.guild.get_channel(chanid)
    if before.channel == chan and after.channel != chan:
        user.leavetime = int(time.time())
        user.guild = guild
        user.guild.users.remove(user)
    elif before.channel != chan and after.channel == chan:
        if ((int(time.time()) - user.leavetime) > (guild.grace * 60)):
            user.jointime = int(time.time())
        user.guild = guild
    db.commit()

async def checkGuild(in_guild, db=db):
    guild = db.query(Guild).filter(Guild.id==in_guild.id).one_or_none()
    if guild == None:
        guild = Guild(id=in_guild.id)
        guild.channel = await get_default_channel(in_guild)
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

async def update_users(in_guild, db=db):
    guild = bot.get_guild(in_guild.id)
    guild_db = await checkGuild(guild, db=db)
    chan = guild.get_channel(guild_db.channel)
    members = chan.voice_states
    for user in guild_db.users:
        u = user.id
        if u not in members:
            user.leavetime = int(time.time())
            user.guild = guild_db
            user.guild.users.remove(user)
    for user in members:
        u = await get_user(user) #from DB
        if u not in guild_db.users:
            try:
                #u.guild = guild_db #This doesn't work
                guild_db.users.append(u)
            except Exception as e:
                print(e)
            if (int(time.time()) - u.leavetime) > (guild_db.grace * 60):
                u.jointime = int(time.time())
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
    owner = await bot.application_info().owner
    if ctx.message.author == owner:
        allowed = True
    elif ctx.message.author.guild_permissions.administrator:
        allowed = True
    elif ctx.guild.get_role(checkGuild(ctx.guild).management_role) in ctx.message.author.roles:
        allowed = True
    return allowed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name="^help", type=discord.ActivityType.listening))
    await bot.wait_until_ready()
    for g in bot.guilds:
        await update_users(g, db=db)

if __name__ == "__main__":
    try:
        bot.run(getToken())
    except discord.LoginFailure:
        print("Login error.")
