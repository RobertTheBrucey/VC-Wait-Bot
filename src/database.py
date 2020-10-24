from sqlalchemy import create_engine, Column, Integer, Boolean, Enum, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class Guild(Base):
    """
    Represents a Discord Guild

    Attributes
    ----------
    id : int
        Discord's internal ID number for the guild
    channel : int
        Discord's internal ID for the channel to monitor for waiting users
    channel_playing : int
        Discord's internal ID for the channel to monitor for playing users
    grace : int
        Time in minutes to allow disconnected users to reconnect and not lose their place
    management_role : int
        Discord's internal ID for a role that can manage the bot
    cooldown : int
        Time in seconds between repeated commands from unprivileged users
    privcomms : bool
        Boolean if set all commands are privileged, regular commands will be DMd then deleted
    lastcall : int
        Unix time of last command invocation
    lastedit : int
        Discord ID of last queue command sent by this bot
    """

    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    channel = Column(Integer, default=0)
    channel_playing = Column(Integer, default=0)
    grace = Column(Integer, default=5)
    management_role = Column(Integer, default=0)
    cooldown = Column(Integer, default=0)
    lastcall = Column(Integer, default=0)
    lastedit = Column(Integer, default=0)
    privcomms = Column(Boolean, default=False)
    lastplay = Column(Integer, default=0)
    record_lobby_time = Column(Integer, default=0)
    record_lobby_user_id = Column(Integer, ForeignKey('users.id'))
    record_lobby_user = relationship("User", uselist=False, foreign_keys=[record_lobby_user_id], primaryjoin="User.id==Guild.record_lobby_user_id")
    record_active_time = Column(Integer, default=0)
    record_active_user_id = Column(Integer, ForeignKey('users.id'))
    record_active_user = relationship("User", uselist=False, foreign_keys=[record_active_user_id], primaryjoin="User.id==Guild.record_active_user_id")
    users = relationship("User", back_populates="guild", primaryjoin="User.guild_id==Guild.id")
    

class Status(enum.Enum):
    """
    Status enum for users in Voice Chats

    Contains none, waiting and playing values
    """

    none = 0
    waiting = 1
    playing = 2

class User(Base):
    """
    Represents a Discord User

    Attributes
    ----------
    id : int
        Discord ID for the user
    guild_id : int
        Discord ID of the guild containing the last monitored channel the user joined
    guild : Guild
        Relationship back to Guild
    jointime : int
        Unix time the user joined waiting channel
    leavetime : int
        Unix time the user left the waiting channel
    jointime_playing : int
        Unix time the user joined the playing channel
    leavetime_playing : int
        Unix time the user left the playing channel
    waiting : Status enum
        Enum representing the user's current status (none, waiting, playing)
    """ 
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    guild = relationship("Guild", back_populates="users", primaryjoin="User.guild_id==Guild.id", post_update=True)
    jointime = Column(Integer, default=0, nullable=False)
    leavetime = Column(Integer, default=0, nullable=False)
    jointime_playing = Column(Integer, default=0, nullable=False)
    leavetime_playing = Column(Integer, default=0, nullable=False)
    waiting = Column(Enum(Status), default=Status.none)
#Guild.users = relationship("User", order_by=User.jointime, back_populates="guild")

class RoleType(enum.Enum):
    """
    Enum describing the role type (none, allow, deny) for future use
    """

    none = 0
    allow = 1
    deny = 2

class Role(Base):
    """
    Represents a Discord Role

    Attributes
    ----------
    id : int
        Discord ID for the role
    guild_id : int
        Discord ID for the guild the role is in
    guild : Guild
        Relationship to Guild
    role_type : RoleType enum
        Enum describing the role type
    """

    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    guild = relationship("Guild", back_populates="roles")
    role_type = Column(Enum(RoleType),nullable=False)
Guild.roles = relationship("Role", back_populates="guild")

class TwitchChannel(Base):
    """
    Represents a Twitch Channel

    Attributes
    ----------
    id : int
        Unused field for Twitch id (which is harder to get than you'd expect)
    name : str
        Name of the Twitch channel (Not including # prefix)
    guild_id : int
        Discord ID of the guild associated with this channel
    guild : Guild
        Relationship to Discord Guild
    verified : bool
        Records whether a mod has verified the Twitch channel
    cooldown : int
        Time in seconds between commands in Twitch chat
    lastcall : int
        Unix time of last command sent to Twitch
    """

    __tablename__ = 'twitch'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    guild = relationship("Guild", back_populates="twitch")
    verified = Column(Boolean, default=False)
    cooldown = Column(Integer, default=2)
    lastcall = Column(Integer, default=0)
Guild.twitch = relationship("TwitchChannel", back_populates="guild")