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
            db.commit()
            await ctx.channel.send("```yaml\nAll queue times have been reset\n```")

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
            db.commit()
            await ctx.channel.send("```yaml\nAll playing times have been reset\n```")

    @commands.command(name='lobbychannel', aliases=["waitchannel", "queuechannel"], description="Set the channel to monitor for waiting users",
    help="Change the channel to monitor for waiting users", brief="Change wait channel")
    async def waitchannel(self, ctx, arg):
        """Set's the lobby channel
        """

        if (await check_auth(ctx, self.bot)):
            opts = [c for c in ctx.guild.voice_channels if arg in c.name.lower()]
            for c in opts:
                if arg == c.name.lower():
                    opts = [c]
            if len(opts) == 1:
                guild = await checkGuild(ctx.guild, db=self.db)
                guild.channel = opts[0].id
                db.commit()
                await ctx.channel.send(f"```yaml\nWait channel set to {c.name}\n```")
            elif len(opts) == 0:
                await ctx.channel.send(f"```yaml\nNo channels match {arg}\n```")
            else:
                chans = ""
                for c in opts:
                    chans += c.name + "\n"
                await ctx.channel.send(f"```yaml\nToo many matches, please be more specific.\n{chans}```")

    @commands.command(name='playchannel', description="Set the channel to monitor for playing users",
    help="Change the channel to monitor for playing users", brief="Change play channel")
    async def playchannel(self, ctx, arg):
        """Set's the active channel
        """

        if (await check_auth(ctx, self.bot)):
            opts = [c for c in ctx.guild.voice_channels if arg in c.name.lower()]
            for c in opts:
                if arg == c.name.lower():
                    opts = [c]
            if len(opts) == 1:
                guild = await checkGuild(ctx.guild, db=self.db)
                guild.channel_playing = c.id 
                db.commit()
                await ctx.channel.send(f"```yaml\nWait channel set to {c.name}\n```")
            elif len(opts) == 0:
                await ctx.channel.send(f"```yaml\nNo channels match {arg}\n```")
            else:
                chans = ""
                for c in opts:
                    chans += c.name + "\n"
                await ctx.channel.send(f"```yaml\nToo many matches, please be more specific.\n{chans}```")

    @commands.command(name='grace', description="Set the grace period in the case of temporary disconnections",
    help="Set the grace period for disconnections", brief="Change DC grace period")
    async def grace(self, ctx, arg):
        """Set's the grace period for leaving VC
        """

        if (await check_auth(ctx, self.bot)):
            if arg.isdigit():
                guild = await checkGuild(ctx.guild, db=self.db)
                guild.grace = int(arg)
                db.commit()
                await ctx.channel.send(f"```yaml\nGrace period changed to {arg} minutes\n```")
            else:
                await ctx.channel.send("```yaml\nError: Expected an integer for grace period\n```")