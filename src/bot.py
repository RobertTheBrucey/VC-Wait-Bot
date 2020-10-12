import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database import Guild, User, Role
import time

bot = commands.Bot(command_prefix='^')

engine = create_engine('sqlite:///:memory') #Change to persistent file eventually
db = sessionmaker(bind=engine)

#* Log when user joins VC
#* Log when user leaves VC
#* Print ordered list when asked
#* Print position in queue when asked
#* Grace period for temporary DCs
#* On restart add all users to queue if they weren't there
#* Settings:
#    * Wait channel
#    * Grace period
#    * Queue Role
#    * Wait Role(s)

@bot.command(name='queue')
async def queue(ctx):
    users = checkGuild(ctx.guild).users
    queue = "```nim\nCurrent Queue:"
    i = 1
    for u in sorted(users, key=lambda x: x.jointime):
        queue += "\n" + str(i) + ": " + ctx.guild.get_member(u.id).nick + ": " + str(int(time.time()) - u.jointime )
        i += 1
    queue += "\n```"
    ctx.channel.send(queue)

@bot.command(name='position')
async def position(ctx, arg):
    pass

@bot.command(name='graceperiod')
async def grace(ctx, arg):
    pass

@bot.command(name='waitchannel')
async def waitchannel(ctx, arg):
    pass

@bot.command(name='allowrole')
async def allowrole(ctx, *args):
    pass

@bot.command(name='denyrole')
async def denyrole(ctx, *args):
    pass

@bot.command(name='managerole')
async def managerole(ctx, arg):
    pass

@bot.event #Requires Intents.voice_states to be enabled
async def on_voice_state_update(member, before, after):
    checkGuild(member.guild)
    user = get_user(member.id)
    chan = member.guild.get_channel(user.guild.channel)
    if before.channel == chan and after.channel != chan:
        user.leavetime = int(time.time())
        user.guild = checkGuild(member.guild)
        user.guild.users.remove(user)
    elif before.channel != chan and after.channel == chan:
        user.jointime = int(time.time())
        user.guild = checkGuild(member.guild)
        user.guild.users.append(user)

async def checkGuild(in_guild):
    guild = None
    for g in db.query(Guild.id).filter(id=in_guild.id):
        guild = g
    if guild == None:
        guild = Guild(id=in_guild.id)
        guild.channel = get_default_channel(in_guild)
        db.add(guild)
        db.commit()
    update_users(guild)
    return guild

async def get_default_channel(in_guild):
    channels = in_guild.voice_channels
    chan = channels[0]
    for c in channels:
        if "wait" in c.name.lower():
            chan = c
    return chan.id

async def update_users(in_guild):
    chan = bot.get_guild(in_guild.id).get_channel(in_guild.channel)
    for user in chan.members:
        u = get_user(u.id) #from DB
        if u not in in_guild.users:
            in_guild.users.append(u)
            if (int(time.time()) - u.leavetime) < (in_guild.grace * 60):
                u.jointime = int(time.time())
    for user in in_guild.users:
        u = user.id
        if u not in chan.members:
            user.leavetime = int(time.time())
    db.commit()
    
async def get_user(user_id): #Add use if not in db
    try:
        user = db.query(User).filter(id=user_id).one()
    except NoResultFound:
        user = User(id=user_id)
        db.commit()
    return user