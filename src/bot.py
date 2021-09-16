import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from config import getToken
from Lobby import Lobby
from LobbyAdmin import LobbyAdmin
from Admin import Admin
from Twitch import Twitch

#Set the required intents for tracking users in voice chat
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

#Initialise Discord Bot, command_prefix could be added to config
bot = commands.Bot(command_prefix='^', intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    # When connected, change presence and start twitch bot
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name="^help", type=discord.ActivityType.listening))
    print(f"Currently in {len(bot.guilds)} guilds")
    for g in bot.guilds:
        print(g)
    if bot.get_cog("Twitch"):
        await bot.get_cog("Twitch").t_bot.start()

if __name__ == "__main__":
    #Start DataBase engine
    engine = create_engine('sqlite:///db/app.db')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine) #Create tables if empty
    db = Session()
    bot.db = db

    #Load all Cogs for this bot
    bot.add_cog(Admin(bot))
    bot.add_cog(LobbyAdmin(bot))
    bot.add_cog(Lobby(bot))
    bot.add_cog(Twitch(bot))
    try:
        from RoleSync import RoleSync
        #bot.add_cog(RoleSync(bot))
    except:
        pass
    try:
        from VoiceRole import VoiceRole
        #bot.add_cog(VoiceRole(bot))
    except:
        pass

    try:
        bot.run(getToken())
    except discord.LoginFailure:
        print("Login error.")