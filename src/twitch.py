from twitchio.ext import commands
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Guild, User, Role, Base, TwitchChannel
import time
import datetime

parser = ConfigParser()
parser.read( "config.ini" )
chans = parser["twitch"]["initial_channels"].split(",")

engine = create_engine('sqlite:///db/app.db') #Change to persistent file eventually
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
db = Session()

bot = commands.Bot(
    irc_token=parser["twitch"]["irc_token"],
    client_id=parser["twitch"]["client_id"],
    nick=parser["twitch"]["nick"],
    prefix=parser["twitch"]["prefix"],
    initial_channels=chans
)

print(chans)

@bot.event
async def event_ready():
    print("Bot Ready")

@bot.event
async def event_message(ctx):
    if not ctx.author.name.lower() == parser["twitch"]["nick"]:
        await bot.handle_commands(ctx)

@bot.command(name="queue")
async def queue(ctx):
    users = db.query(Guild).filter(Guild.id==239303808012779520).one_or_none().users
    count = len(users)
    #longest = sorted(users, key=lambda x: x.jointime)[0]
    #t = datetime.timedelta(seconds=(int(time.time()) - longest.jointime))
    await ctx.send(f'There are {count} players waiting to play!')

if __name__ == "__main__":
    bot.run()