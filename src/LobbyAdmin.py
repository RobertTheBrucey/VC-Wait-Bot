import discord
from discord.ext import commands
from database import Guild, User, Role, Status
from Util import *
import time, datetime

class LobbyAdmin(commands.Cog):
    """
    Lobby Admin Commands Cog

    Command List
    ------------
    grace
    playchannel
    resetactive - aliases: resetplaying
    resetlobby - aliases: resetwaiting, resetqueue
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


    @commands.command(name='resetlobby', aliases=["resetwaiting","resetqueue"], description="Reset the times for all users",
    help="Resets all queue times.", brief="Reset queue times")
    async def resetqueue(self, ctx):
        """Resets all the lobby waiting times
        """

        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            ct = int(time.time())
            for u in guild.users:
                u.jointime = ct
                u.leavetime = 0
            self.db.commit()
            await ctx.channel.send("```yaml\nAll lobby times have been reset\n```")
    
    @commands.command(name='resetlobbyrecord', aliases=["resetwaitingrecord","resetqueuerecord"], description="Reset the record lobby time",
    help="Resets lobby record time.", brief="Reset lobby record")
    async def resetqueuerecord(self, ctx):
        """Resets all the lobby waiting times
        """

        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            guild.record_lobby_time = 0
            self.db.commit()
            await ctx.channel.send("```yaml\nLobby record time has been reset\n```")

    @commands.command(name='resetactive', aliases=["resetplaying"], description="Reset the times for all users",
    help="Resets all playing times.", brief="Reset play times")
    async def resetplaying(self, ctx):
        """Reset all the active times
        """

        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            ct = int(time.time())
            for u in guild.users:
                u.jointime_playing = ct
                u.leavetime_playing = 0
            self.db.commit()
            await ctx.channel.send("```yaml\nAll active times have been reset\n```")
    
    @commands.command(name='resetactiverecord', aliases=["resetplayingrecord"], description="Reset the record active time",
    help="Resets active record time.", brief="Reset active record")
    async def resetplayingrecord(self, ctx):
        """Reset all the active times
        """

        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            guild.record_active_time = 0
            self.db.commit()
            await ctx.channel.send("```yaml\nActive record has been reset\n```")

    @commands.command(name='lobbychannel', aliases=["waitchannel", "queuechannel"], description="Set the channel to monitor for waiting users",
    help="Change the channel to monitor for waiting users", brief="Change wait channel")
    async def waitchannel(self, ctx, arg):
        """Set's the lobby channel
        """

        if (await check_auth(ctx, self.bot)):
            guild = await checkGuild(ctx.guild, db=self.db)
            if arg:
                opts = [c for c in ctx.guild.voice_channels if arg in c.name.lower()]
                for c in opts:
                    if arg == c.name.lower():
                        opts = [c]
                if len(opts) == 1:
                    guild.channel = opts[0].id
                    self.db.commit()
                    await ctx.channel.send(f"```yaml\nWait channel set to {c.name}\n```")
                elif len(opts) == 0:
                    await ctx.channel.send(f"```yaml\nNo channels match {arg}\n```")
                else:
                    chans = ""
                    for c in opts:
                        chans += c.name + "\n"
                    await ctx.channel.send(f"```yaml\nToo many matches, please be more specific.\n{chans}```")
            else:
                await ctx.channel.send(f"```yaml\nCurrent Lobby Channel is {ctx.guild.get_channel(guild.channel).name}\n```")

    @commands.command(name='activechannel', aliases=["playchannel"] ,description="Set the channel to monitor for playing users",
    help="Change the channel to monitor for playing users", brief="Change play channel")
    async def playchannel(self, ctx, arg):
        """Set's the active channel
        """

        if (await check_auth(ctx, self.bot)):
            guild = await checkGuild(ctx.guild, db=self.db)
            if arg:
                opts = [c for c in ctx.guild.voice_channels if arg in c.name.lower()]
                for c in opts:
                    if arg == c.name.lower():
                        opts = [c]
                        break
                if len(opts) == 1:
                    guild.channel_playing = c.id 
                    self.db.commit()
                    await ctx.channel.send(f"```yaml\nActive channel set to {c.name}\n```")
                elif len(opts) == 0:
                    await ctx.channel.send(f"```yaml\nNo channels match {arg}\n```")
                else:
                    chans = ""
                    for c in opts:
                        chans += c.name + "\n"
                    await ctx.channel.send(f"```yaml\nToo many matches, please be more specific.\n{chans}```")
            else:
                await ctx.channel.send(f"```yaml\nCurrent Active channel is {ctx.guild.get_channel(guild.channel_playing).name}\n```")

    @commands.command(name='grace', description="Set the grace period in the case of temporary disconnections",
    help="Set the grace period for disconnections", brief="Change DC grace period")
    async def grace(self, ctx, arg=None):
        """Set's the grace period for leaving VC
        """

        if (await check_auth(ctx, self.bot)):
            guild = await checkGuild(ctx.guild, db=self.db)
            if arg:
                if arg.isdigit():
                    guild.grace = int(arg)
                    self.db.commit()
                    await ctx.channel.send(f"```yaml\nGrace period changed to {arg} minutes\n```")
                else:
                    await ctx.channel.send("```yaml\nError: Expected an integer for grace period\n```")
            else:
                await ctx.channel.send(f"```yaml\nCurrent Grace Period is {guild.grace} minutes\n```")