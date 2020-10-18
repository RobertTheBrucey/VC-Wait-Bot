import discord
from discord.ext import commands
from twitch_bot import T_Bot
from database import Guild, Role, TwitchChannel
from Util import *

class Twitch(commands.Cog):
    """
    Twitch Commands Cog

    Command List
    ------------
    addtwitch
    removetwitch
    showtwitch
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

        self.t_bot = T_Bot(self.db)
    
    @commands.command(name='addtwitch', description="Connect a Twitch channel",
    help=f"Connect a Twitch channel for lobby", brief="Connect a Twitch channel")
    async def add_twitch(self, ctx):
        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            name = ctx.message.content.split(" ")[1]
            if name[0] == "#":
                name = name[1:]
            chan = self.db.query(TwitchChannel).filter(TwitchChannel.name==name).one_or_none()
            if chan is None: #Best case, Twitch channel not linked
                chan = TwitchChannel(name=name, guild=guild)
                if await self.t_bot.add_channel(chan):
                    await ctx.send(f"```yaml\nTwitch channel {name} has been added.\nUse {self.t_bot.prefix}verifyqueue in Twitch chat to complete the connection\n```")
                else:
                    await ctx.send(f"```yaml\nCould not find Twitch channel {name}")
            elif chan.verified: #Someone has already linked this Twitch channel
                await ctx.send(f"```yaml\nTwitch channel {name} has already been linked, use {self.t_bot.prefix}leavequeue in Twitch chat to remove existing connection\n```")
            else: #Twitch linked but not verified, reset the linking process
                chan.guild=guild
                if await self.t_bot.add_channel(chan):
                    await ctx.send(f"```yaml\nTwitch channel {name} has been added.\nUse {self.t_bot.prefix}verifyqueue in Twitch chat to complete the connection\n```")
                else:
                    await ctx.send(f"```yaml\nCould not find Twitch channel {name}")
            self.db.commit()

    @commands.command(name='removetwitch', description="Remove a connected Twitch channel",
    help=f"Remove a connected Twitch channel", brief="Remove a Twitch channel")
    async def del_twitch(self, ctx):
        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            name = ctx.message.content.split(" ")[1]
            if name[0] == "#":
                name = name[1:]
            chan = self.db.query(TwitchChannel).filter(TwitchChannel.name==name).one_or_none()
            if chan is None:
                await ctx.send(f"```yaml\nCould not find Twitch channel {name}")
            else:
                if chan.guild == guild:
                    await self.t_bot.del_channel(chan)
                    db.delete(chan)
                    await ctx.channel.send(f"```yaml\nTwitch channel {name} has been removed\n```")
                else:
                    await ctx.channel.send(f"```yaml\nTwitch channel {name} is not linked to this server. Naughty!\n```")
            self.db.commit()
    
    @commands.command(name='showtwitch', description="Show connected Twitch channels",
    help=f"Show connected Twitch channels", brief="Show connected Twitch channels")
    async def show_twitch(self, ctx):
        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=db)
            string = "```yaml\nLinked twitch channels:\n"
            verimsg = False
            if guild.twitch:
                for c in guild.twitch:
                    string += c.name + " - " + ("Verified\n" if c.verified else "Unverified\n")
                    if not c.verified:
                        verimsg = True
                if verimsg:
                    string += f"A mod must use {self.t_bot.prefix}verifyqueue in twitch chat to verify channels\n"
                string += "```"
                await ctx.channel.send(string)
            else:
                await ctx.channel.send("```yaml\nNo twitch channels have been linked.\n```")