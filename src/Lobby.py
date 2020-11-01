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
        self.db = bot.db

    @commands.command(name='lobby', aliases=["waiting", "queue"], description="Show the queue of players in the waiting channel.",
    help="Show the queue of players in the waiting channel.", brief="Show the queue", pass_context=True)
    async def lobby(self, ctx):
        """Prints the current lobby with times users have been waiting
        """

        if not isinstance(ctx.channel, discord.channel.DMChannel):
            async with ctx.channel.typing():
                auth = await check_auth(ctx, self.bot)
                guild = await checkGuild(ctx.guild, db=self.db)
                users = [ u for u in guild.users if u.waiting == Status.waiting ]
                tl = (guild.lastcall + guild.cooldown) - int(time.time())
                if tl <= 0 or auth or guild.privcomms:
                    queue = ""
                    if users:
                        queue = "```yaml\nCurrent Lobby:"
                        i = 1
                        for u in sorted(users, key=lambda x: x.jointime):
                            nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                            t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
                            queue += f"\n{i}: {nick}: {t}"
                            i += 1
                        if not guild.privcomms or auth:
                            queue += "\nThis message will be auto updated until ^lobby is used again\n```"
                            await delete_own(ctx.guild, guild.lastedit, self.db)
                            guild.lastedit = (await ctx.channel.send(queue)).id
                        else:
                            queue +="\n```"
                            await ctx.author.send(queue)
                            try:
                                await ctx.message.delete()
                            except:
                                pass
                    else:
                        queue = "```yaml\nLobby is empty\n```"
                        if not guild.privcomms or auth:
                            await delete_own(ctx.guild, guild.lastedit, self.db)
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
                    await ctx.channel.send(f"```yaml\nCommand on cooldown, please wait {tl} seconds.\n```", delete_after=del_time)

    @commands.command(name='active', aliases=["playing"], description="Show the play time of current players.",
    help="Show the play time of current players.", brief="Show the players")
    async def playing(self, ctx):
        """Prints the current lobby with times users have been active
        """

        if not isinstance(ctx.channel, discord.channel.DMChannel):
            async with ctx.channel.typing():
                auth = await check_auth(ctx, self.bot)
                guild = await checkGuild(ctx.guild, db=self.db)
                users = [ u for u in guild.users if u.waiting == Status.playing ]
                tl = (guild.lastcall + guild.cooldown) - int(time.time())
                if tl <= 0 or auth or guild.privcomms:
                    if users:
                        queue = "```yaml\nCurrent Active Users:"
                        i = 1
                        for u in sorted(users, key=lambda x: x.jointime_playing):
                            nick = ctx.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                            t = datetime.timedelta(seconds=(int(time.time()) - u.jointime_playing))
                            queue += f"\n{i}: {nick}: {t}"
                            i += 1
                        if not guild.privcomms or auth:
                            queue += "\nThis message will be auto updated until ^active is used again\n```"
                            await delete_own(ctx.guild, guild.lastplay, self.db)
                            guild.lastplay = (await ctx.channel.send(queue)).id
                        else:
                            queue +="\n```"
                            await ctx.author.send(queue)
                            try:
                                await ctx.message.delete()
                            except:
                                pass
                    else:
                        queue = "```yaml\nNo one is Active right now\n```"
                        if not guild.privcomms or auth:
                            await delete_own(ctx.guild, guild.lastplay, self.db)
                            guild.lastplay = (await ctx.channel.send(queue)).id
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
                    await ctx.channel.send(f"```yaml\nCommand on cooldown, please wait {tl} seconds.\n```", delete_after=del_time)

    @commands.command(name='activerecord', aliases=["playingrecord"], description="Show the record longest active time.",
    help="Show the record longest active user.", brief="Show the active record")
    async def playingrecord(self, ctx):
        """Shows the current active time record holder
        """

        auth = await check_auth(ctx, self.bot)
        guild = await checkGuild(ctx.guild, db=self.db)
        if guild.record_active_time:
            chan = ctx.guild.get_channel(guild.channel_playing)
            if ctx.guild.get_member(guild.record_active_user_id) is None:
                guild.record_active_time = 0
            for user in chan.voice_states:
                u = await get_user(user, db=self.db)
                if int(time.time()) - u.jointime > guild.record_active_time:
                    guild.record_active_time = int(time.time()) - u.jointime_playing
                    guild.record_active_user = u
            self.db.commit()
            nick = ctx.guild.get_member(guild.record_active_user_id).display_name
            t = datetime.timedelta(seconds=guild.record_active_time)
            msg = f"```yaml\nThe current active time record holder is {nick} with a time of {t}\n```"
            if auth or not guild.privcomms:
                await ctx.channel.send(msg)
            else:
                await ctx.author.send(msg)
                try:
                    await ctx.message.delete()
                except:
                    pass

    @commands.command(name='lobbyrecord', aliases=["queuerecord","waitingrecord"], description="Show the record longest lobby time.",
    help="Show the record longest lobby user.", brief="Show the lobby record")
    async def lobbyrecord(self, ctx):
        """Shows the current lobby time record holder
        """

        auth = await check_auth(ctx, self.bot)
        guild = await checkGuild(ctx.guild, db=self.db)
        if guild.record_lobby_time:
            chan = ctx.guild.get_channel(guild.channel)
            if ctx.guild.get_member(guild.record_lobby_user.id) is None:
                guild.record_lobby_time = 0
            for user in chan.voice_states:
                u = await get_user(user, db=self.db)
                if int(time.time()) - u.jointime > guild.record_lobby_time:
                    guild.record_lobby_time = int(time.time()) - u.jointime
                    guild.record_lobby_user = u
            self.db.commit()
            print(guild.record_lobby_user.id)
            nick = ctx.guild.get_member(guild.record_lobby_user.id).display_name
            t = datetime.timedelta(seconds=guild.record_lobby_time)
            msg = f"```yaml\nThe current lobby time record holder is {nick} with a time of {t}\n```"
            if auth or not guild.privcomms:
                await ctx.channel.send(msg)
            else:
                await ctx.author.send(msg)
                try:
                    await ctx.message.delete()
                except:
                    pass

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
        update_p = False
        if after.channel == chan and before.channel != chan: #Moved into waiting
            if (user.guild != guild) or ((int(time.time()) - user.leavetime) > (guild.grace * 60)): #grace period handling
                user.jointime = int(time.time()) #grace period handling
            user.guild = guild
            user.waiting = Status.waiting
            update = True
        elif after.channel == p_chan and before.channel != p_chan: #Moved into playing
            if (user.guild != guild) or ((int(time.time()) - user.leavetime_playing) > (guild.grace * 60)): #grace period handling
                user.jointime_playing = int(time.time()) #grace period handling
            user.guild = guild
            user.waiting = Status.playing
            update_p = True
        if before.channel == chan and after.channel != chan: #Left waiting
            user.leavetime = int(time.time())
            if user.jointime == 0:
                user.jointime = user.leavetime
            dur = user.leavetime - user.jointime
            if dur > guild.record_lobby_time:
                guild.record_lobby_time = dur
                guild.record_lobby_user = user
            elif not member.guild.get_member(guild.record_lobby_user_id):
                guild.record_lobby_time = dur
                guild.record_lobby_user = user
            if after.channel != p_chan:
                    user.waiting = Status.none
            user.guild = guild
            update = True
        elif before.channel == p_chan and after.channel != p_chan: #Left playing
            user.leavetime_playing = int(time.time())
            if user.jointime_playing == 0:
                user.jointime_playing = user.leavetime_playing
            dur = user.leavetime_playing - user.jointime_playing
            if dur > guild.record_active_time:
                guild.record_active_time = dur
                guild.record_active_user = user
            elif not member.guild.get_member(guild.record_active_user_id):
                guild.record_active_time = dur
                guild.record_active_user = user
            if after.channel != chan:
                    user.waiting = Status.none
            user.guild = guild
            update_p = True
        self.db.commit()
        if update:
            await self.update_last(member.guild, db=self.db)
        if update_p:
            await self.update_play(member.guild, db=self.db)

    async def update_last(self, guild_d, db):
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
        async with msg.channel.typing():
            try:
                tl = (msg.edited_at.timestamp() + guild.cooldown + 1) - int(time.time())
            except AttributeError: #Catch if message is uneditted
                tl = 0
            if tl <= 0:
                if users:
                    queue = "```yaml\nCurrent Lobby:"
                    i = 1
                    for u in sorted(users, key=lambda x: x.jointime):
                        nick = msg.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                        t = datetime.timedelta(seconds=(int(time.time()) - u.jointime))
                        queue += f"\n{i}: {nick}: {t}"
                        i += 1
                    queue += "\nThis message will be auto updated until ^lobby is used again\n```"
                    await msg.edit(content=queue)
                else:
                    await msg.edit(content="```yaml\nLobby is empty\n```")

    async def update_play(self, guild_d, db):
        """Update last sent lobby message

        Parameters
        ----------
        guild_d : discord.Guild
            Discord Guild to update
        db : Session
            SQLAlchemy database session to query
        """

        guild = await checkGuild(guild_d, db=self.db)
        users = [ u for u in guild.users if u.waiting == Status.playing ]
        msg = None
        for c in guild_d.text_channels: #This block could be cleaner?
            try:
                msg = await c.fetch_message(guild.lastplay)
            except:
                pass
            if msg:
                break
        if msg is None:
            return
        async with msg.channel.typing():
            try:
                tl = (msg.edited_at.timestamp() + guild.cooldown + 1) - int(time.time())
            except AttributeError: #Catch if message is uneditted
                tl = 0
            if tl <= 0:
                if users:
                    queue = "```yaml\nCurrent Active Users:"
                    i = 1
                    for u in sorted(users, key=lambda x: x.jointime_playing):
                        nick = msg.guild.get_member(u.id).display_name #Duplicate displaynames are not handled
                        t = datetime.timedelta(seconds=(int(time.time()) - u.jointime_playing))
                        queue += f"\n{i}: {nick}: {t}"
                        i += 1
                    queue += "\nThis message will be auto updated until ^active is used again\n```"
                    await msg.edit(content=queue)
                else:
                    await msg.edit(content="```yaml\nNo one is Active right now\n```")

    async def update_users(self, guild):
        """Update user status in monitored channels
        
        Parameters
        ----------
        guild : discord.Guild
            Discord Guild to update users for
        """
        
        guild_db = await checkGuild(guild, db=self.db)
        members = guild.get_channel(guild_db.channel).voice_states if guild.get_channel(guild_db.channel) else {} #Wait channel
        members_p = guild.get_channel(guild_db.channel_playing).voice_states if guild.get_channel(guild_db.channel_playing) else {} #Play channel
        
        for user in guild_db.users: #Remove users not in VC
            u = user.id
            if u not in {**members, **members_p}:
                if user.waiting == Status.waiting:
                    user.leavetime = int(time.time())
                else:
                    user.leavetime_playing = int(time.time())
                user.guild = guild_db
                user.waiting = Status.none
        for user in members: #Add users in waiting
            u = await get_user(user, self.db) #get User from DB
            if u not in guild_db.users:
                u.guild = guild_db
                u.waiting = Status.waiting
                if (int(time.time()) - u.leavetime) > (guild_db.grace * 60) or u.jointime == 0: #Grace period handling
                    u.jointime = int(time.time())
        for user in members_p: #Add users in playing
            u = await get_user(user, self.db) #get User from DB
            if u not in guild_db.users:
                u.guild = guild_db
                u.waiting = Status.playing
                if (int(time.time()) - u.leavetime_playing) > (guild_db.grace * 60) or u.jointime_playing == 0: #Grace period handling
                    u.jointime_playing = int(time.time())
        self.db.commit()
        await self.update_last(guild, db=self.db)
        await self.update_play(guild, db=self.db)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Updating user status's")
        for g in self.bot.guilds:
            await self.update_users(g)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Joined new guild: {guild}")
        await self.update_users(guild)

def setup(bot):
    bot.add_cog(Lobby(bot))