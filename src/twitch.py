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
        if db is None:
            engine = create_engine('sqlite:///db/app.db')
            Session = sessionmaker(bind=engine)
            Base.metadata.create_all(engine)
            db = Session()
        chans = [c.name for c in db.query(TwitchChannel).all()]
        chans += parser["twitch"]["initial_channels"].split(",")
        super().__init__(
            irc_token=parser["twitch"]["irc_token"],
            client_id=parser["twitch"]["client_id"],
            nick=parser["twitch"]["nick"],
            prefix=parser["twitch"]["prefix"],
            initial_channels=chans #Change to read in from db
            )
        

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

    @command.command(name="queue2")
    async def queue2(self, ctx):
        chan = self.db.query(TwitchChannel).filter(TwitchChannel.name==ctx.channel.name).one_or_none()
        users = chan.guild.users
        count = len(users)
        await ctx.send(f'There are {count} players waiting to play!')
    
    async def add_channel(self, chan):
        success = True
        try:
            await self.join_channels([chan.name])
        except:
            success = False
        return success

    async def del_channel(self, chan):
        await self.part_channels([chan.name])
    
    @commands.command(name="verifyqueue")
    async def verify(self, ctx):
        if ctx.author.is_mod:
            chan = self.db.query(TwitchChannel).filter(TwitchChannel.name==ctx.channel.name).one_or_none()
            if not chan is None:
                chan.verified = True
                self.db.commit()

    @commands.command(name="leavequeue")
    async def leavequeue(self, ctx):
        if ctx.author.is_mod:
            chan = self.db.query(TwitchChannel).filter(TwitchChannel.name==ctx.channel.name).one_or_none()
            if not chan is None:
                await ctx.send("Goodbye!")
                await self.part_channels([chan.name])
                self.db.delete(chan)
                self.db.commit()

if __name__ == "__main__":
    t_bot = T_Bot()
    t_bot.run()