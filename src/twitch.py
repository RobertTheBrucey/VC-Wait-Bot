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

class T_Bot(commands.bot):
    def __init__(self, db=None):
        super().__init__(
            irc_token=parser["twitch"]["irc_token"],
            client_id=parser["twitch"]["client_id"],
            nick=parser["twitch"]["nick"],
            prefix=parser["twitch"]["prefix"],
            initial_channels=chans #Change to read in from db
            )
        if db is None:
            engine = create_engine('sqlite:///db/app.db')
            Session = sessionmaker(bind=engine)
            Base.metadata.create_all(engine)
            db = Session()

    async def event_ready(self):
        print(f"Twitch connected as {self.nick}")

    async def event_message(self, ctx):
        if not ctx.author.name.lower() == parser["twitch"]["nick"]:
            await self.handle_commands(ctx)

    @command.command(name="queue")
    async def queue(self, ctx):
        users = self.db.query(Guild).filter(Guild.id==239303808012779520).one_or_none().users
        count = len(users)
        #longest = sorted(users, key=lambda x: x.jointime)[0]
        #t = datetime.timedelta(seconds=(int(time.time()) - longest.jointime))
        await ctx.send(f'There are {count} players waiting to play!')
    
    @commands.command(name="verifyqueue")
    async def verify(self, ctx):
        if ctx.author.is_mod:
            chan = self.db.query(TwitchChannel).filter(TwitchChannel.id==ctx.channel.name)

if __name__ == "__main__":
    t_bot = T_Bot()
    t_bot.run()