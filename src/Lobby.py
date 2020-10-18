import discord
from discord.ext import commands
from database import Guild, User, Role, Status
from Util import *
import time, datetime

class Lobby(commands.Cog):
    """
    Lobby Commands Cog

    Command List
    ------------
    lobby - aliases: waiting, queue
    active - aliases: playing
    """

    def __init__(self, bot):
        """
        Parameters
        ----------
        bot : Bot
            Bot to add this cog to
        """
        
        self.bot = bot
        self._last_member = None
        self.db = bot.db
    
    @commands.command(name='lobby', aliases=["waiting", "queue"], description="Show the queue of players in the waiting channel.",
    help="Show the queue of players in the waiting channel.", brief="Show the queue")
    async def queue(self, ctx):
        """Prints the current lobby with times users have been waiting
        """

        auth = await check_auth(ctx, self.bot)
        guild = await checkGuild(ctx.guild, db=self.db)
        users = [ u for u in guild.users if u.waiting == Status.waiting ]
        tl = (guild.lastcall + guild.cooldown) - int(time.time())
        if tl <= 0 or auth or guild.privcomms:
            queue = ""
            if users:
                queue = "```yaml\nCurrent Queue:"
                i = 1
                for u in sorted(users, key=lambda x: x.jointime):
                    nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                    t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
                    queue += f"\n{i}: {nick}: {t}"
                    i += 1
                queue += "\nThis message will be auto updated until ^queue is used again\n```"
            else:
                queue = "```yaml\nQueue is empty\n```"
                if not guild.privcomms or auth:
                    guild.lastedit = (await ctx.channel.send(queue)).id
                    if not auth:
                        guild.lastcall = int(time.time())
                else:
                    await ctx.author.send(queue)
                    try:
                        await ctx.message.delete()
                    except:
                        pass
            self.db.commit()
        else:
            await ctx.channel.send(f"```yaml\nCommand on cooldown, please wait {tl} seconds.\n```")

    @commands.command(name='active', aliases=["playing"], description="Show the play time of current players.",
    help="Show the play time of current players.", brief="Show the players")
    async def playing(self, ctx):
        """Prints the current lobby with times users have been active
        """

        auth = await check_auth(ctx, self.bot)
        guild = await checkGuild(ctx.guild, db=self.db)
        users = [ u for u in guild.users if u.waiting == Status.playing ]
        tl = (guild.lastcall + guild.cooldown) - int(time.time())
        if tl <= 0 or auth or guild.privcomms:
            if users:
                queue = "```yaml\nCurrent Players:"
                i = 1
                for u in sorted(users, key=lambda x: x.jointime_playing):
                    nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                    t = datetime.timedelta(seconds=(int(time.time()) - u.jointime_playing))
                    queue += f"\n{i}: {nick}: {t}"
                    i += 1
                queue += "\n```"
            else:
                queue = "```yaml\nNo one is playing right now\n```"
                if not guild.privcomms or auth:
                    guild.lastedit = (await ctx.channel.send(queue)).id
                    if not auth:
                        guild.lastcall = int(time.time())
                else:
                    await ctx.author.send(queue)
                    try:
                        await ctx.message.delete()
                    except:
                        pass
            self.db.commit()
        else:
            await ctx.channel.send(f"```yaml\nCommand on cooldown, please wait {tl} seconds.\n```")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Update database on voice chat change
        """
        #I would like this to be cleaner, but it's not obvious how...
        guild = await checkGuild(member.guild, db=self.db)
        user = await get_user(member.id, db=self.db)
        chanid = guild.channel
        chan = member.guild.get_channel(chanid)
        p_chan = member.guild.get_channel(guild.channel_playing)
        update = False
        if after.channel == chan and before.channel != chan: #Moved into waiting
            if user.guild != guild or ((int(time.time()) - user.leavetime) > (guild.grace * 60)): #grace period handling
                user.jointime = int(time.time()) #grace period handling
            user.guild = guild
            user.waiting = Status.waiting
            update = True
        elif after.channel == p_chan and before.channel != p_chan: #Moved into playing
            if user.guild != guild or ((int(time.time()) - user.leavetime_playing) > (guild.grace * 60)): #grace period handling
                user.jointime_playing = int(time.time()) #grace period handling
            user.guild = guild
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
        self.db.commit()
        if update:
            await update_last(member.guild, db=self.db)

    async def update_last(self, guild_d, db) -> None:
        """Update last sent lobby message

        Parameters
        ----------
        guild_d : discord.Guild
            Discord Guild to update
        db : Session
            SQLAlchemy database session to query
        """

        guild = await checkGuild(guild_d, db=self.db)
        users = [ u for u in guild.users if u.waiting == Status.waiting ]
        msg = None
        for c in guild_d.text_channels: #This block could be cleaner?
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
        except AttributeError: #Catch if message is uneditted
            tl = 0
        if tl <= 0:
            if users:
                queue = "```yaml\nCurrent Queue:"
                i = 1
                for u in sorted(users, key=lambda x: x.jointime):
                    nick = msg.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                    t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
                    queue += f"\n{i}: {nick}: {t}"
                    i += 1
                queue += "\nThis message will be auto updated until ^queue is used again\n```"
                await msg.edit(content=queue)
            else:
                await msg.edit(content="```yaml\nQueue is empty\n```")

    async def update_users(self, guild) -> None:
        """Update user status in monitored channels

        Parameters
        ----------
        guild : discord.Guild
            Discord Guild to update users for
        """

        guild_db = await checkGuild(guild, db=self.db)
        members = guild.get_channel(guild_db.channel).voice_states #Wait channel
        members_p = guild.get_channel(guild_db.channel_playing).voice_states #Play channel

        for user in guild_db.users: #Remove users not in VC
            u = user.id
            if u not in {**members, **members_p}:
                user.leavetime = int(time.time())
                user.guild = guild_db
                user.waiting = Status.none
        for user in members: #Add users in waiting
            u = await get_user(user) #get User from DB
            if u not in guild_db.users:
                u.guild = guild_db
                u.waiting = Status.waiting
                if (int(time.time()) - u.leavetime) > (guild_db.grace * 60): #Grace period handling
                    u.jointime = int(time.time())
        for user in members_p: #Add users in playing
            u = await get_user(user) #get User from DB
            if u not in guild_db.users:
                u.guild = guild_db
                u.waiting = Status.playing
                if (int(time.time()) - u.leavetime_playing) > (guild_db.grace * 60): #Grace period handling
                    u.jointime_playing = int(time.time())
        self.db.commit()
        
    #@bot.event
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Updating user status's")
        for g in self.bot.guilds:
            await update_users(g)