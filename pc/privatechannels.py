from discord.ext import commands
import asyncio, time, re, discord
from time import gmtime, strftime
from datetime import datetime
from discord.member import VoiceState
from discord.channel import VoiceChannel
from discord import Member

from redbot.core import Config, checks

#todo: automatically create voice channel, there is always 1 empty voice channel
#todo: automatically delete empty voice channels, except 1
#todo: allow "admin" of the voice and text channel to set limit of users who can join
#todo: allow "admin" to change the permission of the text channel (e.g. reading permission, comment permission)
#todo: text channel default: no reading rights, role permission default: reading rights
#todo: implement role. Only users who are in the voice channel gain a role.
#todo: create a list of default names

class PrivateChannels:
    default_channel = {
        "admin": None,  # first user to join an empty voice channel is admin, he can server mute/deafen
        "textchannel": None,  # a text channel is created and linked to the voice channel
        "role": None,  # a new role is created specific for that text channel, grants reading permission
        "logging": True,  # admin can choose to log (user join/leave, mute/deaf, ...)
    }
    default_guild = {
        "dynamiccategory": None
    }
    conf_id = 800858686

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_channel(**self.default_channel)
        self.config.register_guild(**self.default_guild)

    @commands.command()
    async def type(self, ctx):
        await ctx.trigger_typing()
        print('\n\n\n\n\n\n')

    @commands.command()
    async def debug(self, ctx):
        await ctx.trigger_typing()
        guild_group = self.config.guild(ctx.guild)
        category_id = await guild_group.dynamiccategory()
        print(category_id)


    @commands.command()
    async def pcinit(self, ctx):
        category = await ctx.guild.create_category('dynamic room')
        await self.config.guild(ctx.guild).dynamiccategory.set(category.id)

        print(dir(category))


    async def on_voice_state_update(self, member:Member, before:VoiceState, after:VoiceState):
        if not await self.config.dynamiccategory():
            # do nothing, user needs to run 'pcinit' to make use of this cog
            return

        await self.state_change(member, before, after)

        if before.channel != after.channel:
            await self.check_voice_channel(before.channel)
            await self.check_voice_channel( after.channel)


    async def state_change(self, member:Member, before:VoiceState, after:VoiceState):
        if before.deaf != after.deaf:
            await self.log_message(before.channel, 'guild deaf')
        if before.mute != after.mute:
            await self.log_message(before.channel, 'guild mute')
        if before.self_mute != after.self_mute:
            await self.log_message(before.channel, 'self mute')
        if before.self_deaf != after.self_deaf:
            await self.log_message(before.channel, 'self dead')
        if before.channel != after.channel:
            await self.log_message(before.channel, 'channel change')

    async def log_message(self, channel:VoiceChannel, message:str):
        #retrieve the text channel id from voice channel config
        #retrieve the text channel object and send the message

        #print(message)
        pass


    async def check_voice_channel(self, channel:VoiceChannel):
        # voice channel does not exist, do nothing
        if not channel:
            return

        guild_group = self.config.guild(channel.guild)

        # voice channel is not dynamic, do nothing
        if channel.category_id != await guild_group.dynamiccategory():
            return

        channel_group = self.config.channel(channel)


        #print(object)
        #print(type(object))
        #print([method_name for method_name in dir(object)
        #if callable(getattr(object, method_name))])

        #print(dir(object))


        if len(channel.members) == 0:
            #restore default config, destroy text channel, destroy role
            await channel_group.admin.set(None)

            text_channel = self.bot.get_channel(id=await channel_group.textchannel())
            await text_channel.delete()
            await channel_group.textchannel.set(None)

        else:
            if len(channel.members) == 1:
                #set admin of the channel, create text channel, create role
                await channel_group.admin.set(channel.members[0].id)
                
                category_id = await guild_group.dynamiccategory()
                category = self.bot.get_channel(id = category_id)
                text_channel = await channel.guild.create_text_channel(name=re.sub(r'\W+', '', channel.name), category=category)
                await channel_group.textchannel.set(text_channel.id)


            #set role for every user
            pass



