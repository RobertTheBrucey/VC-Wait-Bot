import discord
from discord.ext import commands
from Util import *
from database import Guild, Role

class Admin(commands.Cog):
    """
    General Admin Commands Cog

    Command List
    ------------
    config
    cooldown
    managerole
    privilegecommands
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

    @commands.command(name='getme', description="Sends the bot invite link",
    help="Sends you an invite link for this bot", brief="Add this bot to your server!")
    async def getme(self, ctx):
        await ctx.author.send("```yaml\nClick this to add me to your server!\nhttps://discord.com/api/oauth2/authorize?client_id=765426185638903808&permissions=11264&scope=bot\n```")

    @commands.command(name='restrictcommands', aliases=["privilegecommands"], description="Toggle priviledge commands mode",
    help="Toggles whether unprivileged users can use queue and playing", brief="Toggle privileged commands")
    async def toggle_priv(self, ctx):
        if await check_auth(ctx, self.bot):
            guild = await checkGuild(ctx.guild, db=self.db)
            guild.privcomms = not guild.privcomms
            self.db.commit()
            if guild.privcomms:
                await ctx.channel.send("```yaml\nRegular commands now DM unprivileged users\n```")
            else:
                await ctx.channel.send("```yaml\nRegular commands can now be used by all users\n```")

    @commands.command(name='cooldown', description="Set the cooldown of the queue command",
    help="Set the cooldown of the queue command", brief="Change cooldown time")
    async def set_cooldown(self, ctx, arg=None):
        if (await check_auth(ctx, self.bot)):
            print(f"Arg is {arg}")
            guild = await checkGuild(ctx.guild, db=self.db)
            if not arg is None:
                if arg.isdigit():
                    guild.cooldown = int(arg)
                    self.db.commit()
                    await ctx.channel.send(f"```yaml\nCooldown time changed to {arg} seconds\n```")
                else:
                    await ctx.channel.send("```yaml\nError: Expected an integer for cooldown time\n```")
            else:
                await ctx.channel.send(f"```yaml\nCooldown is currently {guild.cooldown} seconds\n```")

    @commands.command(name='managerole', description="(Optional) Set a role to manage this bot",
    help="Set the role to manage this bot in additional to administrators", brief="Set bot controller role")
    async def managerole(self, ctx, arg=None):
        if (await check_auth(ctx, self.bot)):
            guild = await checkGuild(ctx.guild, db=self.db)
            if arg:
                opts = [c for c in ctx.guild.roles if arg in c.name.lower()]
                for c in ctx.guild.roles:
                    if arg == c.name.lower():
                        opts = [c]
                if len(opts) == 1:
                    guild.management_role = opts[0].id
                    db.commit()
                    await ctx.channel.send(f"```yaml\nManagement role set to {c.name} \n```")
                elif len(opts) == 0:
                    await ctx.channel.send(f"```yaml\nNo roles match {arg}\n```")
                else:
                    chans = ""
                    for c in opts:
                        chans += c.name + "\n"
                    await ctx.channel.send(f"```yaml\nToo many matches, please be more specific.\n{chans}\n```")
            else:
                await ctx.channel.send(f"```yaml\nCurrent Management role is {ctx.guild.get_role(guild.management_role)}\n```")

    #Should change this to work better with cogs
    @commands.command(name='config', description="Show the current configuration",
    help="Show the current configuration", brief="Show current config")
    async def print_config(self, ctx):
        if (await check_auth(ctx, self.bot)):
            guild = await checkGuild(ctx.guild, db=self.db)
            string = "```yaml\nServer: "
            string += self.bot.get_guild(guild.id).name + "\n"
            string += "Lobby Channel: " + ctx.guild.get_channel(guild.channel).name + "\n"
            string += "Active Channel: " + ctx.guild.get_channel(guild.channel_playing).name + "\n"
            string += "Grace Period: " + str(guild.grace) + " minutes\n"
            string += "Cooldown Time: " + str(guild.cooldown) + " seconds\n"
            string += "Management role: " + str(ctx.guild.get_role(guild.management_role)) + "\n"
            string += "```"
            await ctx.channel.send(string)