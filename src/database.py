from sqlalchemy import create_engine, Column, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class Guild(Base):
    __tablename__ = 'guilds'

    #Guild
    id = Column(Integer, primary_key=True)
    #Wait Channel
    channel = Column(Integer, default=0)
    #Users - FK
    
    #Grace Period
    grace = Column(Integer, default=5)
    #Allowed Queue Roles - FK
    #Denied Queue Roles - FK

    #Management Role
    management_role = Column(Integer, default=0)
    #Cooldown tracking
    cooldown = Column(Integer, default=0)
    lastcall = Column(Integer, default=0)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    guild = relationship("Guild", back_populates="users")
    jointime = Column(Integer, default=0, nullable=False)
    leavetime = Column(Integer, default=0, nullable=False)
Guild.users = relationship("User", order_by=User.jointime, back_populates="guild")

class RoleType(enum.Enum):
    none = 0
    allow = 1
    deny = 2

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    guild = relationship("Guild", back_populates="roles")
    role_type = Column(Enum(RoleType),nullable=False)
Guild.roles = relationship("Role", back_populates="guild")

class TwitchChannel(Base):
    __tablename__ = 'twitch'
    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    guild = relationship("Guild", back_populates="twitch")
    verified = Column(Integer, default=0) #0: unverified, 1: verification message sent, 2: verified
Guild.twitch = relationship("TwitchChannel", back_populates="guild")