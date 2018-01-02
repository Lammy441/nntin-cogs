from discord.ext import commands
from discord.member import VoiceState
from discord.channel import VoiceChannel
from discord import Member, PermissionOverwrite
from random import choice
from asyncio import Queue
import re

from redbot.core import Config, checks

#todo: allow "admin" of the voice and text channel to set limit of users who can join
#todo: allow "admin" to change the permission of the text channel (e.g. read, send, connect, ... permission)
#todo: allow admin to give role
#todo: remove debug messages and unnecessary code
#todo: implement logs in text channel
#todo: implement message: requires manage role and manage channel permission.
#todo: priority low: implement a garbage collector that runs perodically, that deletes too many
#todo: empty voice channels, roles and text channels.
#todo: priority low: give a user a timeout from the dynamic voice channels for switching too often

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
    channel_names = ['antimage', 'axe', 'bane', 'bloodseeker', 'crystal_maiden', 'drow_ranger', 'earthshaker',
                     'juggernaut', 'mirana', 'nevermore', 'morphling', 'phantom_lancer', 'puck', 'pudge', 'razor',
                     'sand_king', 'storm_spirit', 'sven', 'tiny', 'vengefulspirit', 'windrunner', 'zuus', 'kunkka',
                     'lina', 'lich', 'lion', 'shadow_shaman', 'slardar', 'tidehunter', 'witch_doctor', 'riki', 'enigma',
                     'tinker', 'sniper', 'necrolyte', 'warlock', 'beastmaster', 'queenofpain', 'venomancer',
                     'faceless_void', 'skeleton_king', 'death_prophet', 'phantom_assassin', 'pugna', 'templar_assassin',
                     'viper', 'luna', 'dragon_knight', 'dazzle', 'rattletrap', 'leshrac', 'furion', 'life_stealer',
                     'dark_seer', 'clinkz', 'omniknight', 'enchantress', 'huskar', 'night_stalker', 'broodmother',
                     'bounty_hunter', 'weaver', 'jakiro', 'batrider', 'chen', 'spectre', 'doom_bringer',
                     'ancient_apparition', 'ursa', 'spirit_breaker', 'gyrocopter', 'alchemist', 'invoker', 'silencer',
                     'obsidian_destroyer', 'lycan', 'brewmaster', 'shadow_demon', 'lone_druid', 'chaos_knight', 'meepo',
                     'treant', 'ogre_magi', 'undying', 'rubick', 'disruptor', 'nyx_assassin', 'naga_siren',
                     'keeper_of_the_light', 'wisp', 'visage', 'slark', 'medusa', 'troll_warlord', 'centaur',
                     'magnataur', 'shredder', 'bristleback', 'tusk', 'skywrath_mage', 'abaddon', 'elder_titan',
                     'legion_commander', 'ember_spirit', 'earth_spirit', 'terrorblade', 'phoenix', 'oracle', 'techies',
                     'winter_wyvern', 'arc_warden', 'abyssal_underlord', 'monkey_king', 'pangolier', 'dark_willow']

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_channel(**self.default_channel)
        self.config.register_guild(**self.default_guild)
        self.q = Queue()

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
        await ctx.guild.create_voice_channel(name=choice(self.channel_names), category=category)


    async def on_voice_state_update(self, member:Member, before:VoiceState, after:VoiceState):
        if not await self.config.dynamiccategory():
            # do nothing, user needs to run 'pcinit' to make use of this cog
            return

        await self.state_change(member, before, after)

        # ensuring that the method is runned only one at a time
        # todo: this is wrong! you are passing variables into the queue. It calculates the whole function before
        # todo: you need to the function to the queue and call it at a later date.
        if before.channel != after.channel:
            await self.q.put(self.check_voice_channel(before.channel, member))
            await self.q.put(self.check_voice_channel( after.channel, member))

    async def workqueue(self):
        while True:
            try:
                awaitThis = await self.q.get()
                await awaitThis
            except:
                print("Error")

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


    async def check_voice_channel(self, channel:VoiceChannel, member:Member):
        # voice channel does not exist, do nothing
        if not channel:
            return

        guild_group = self.config.guild(channel.guild)

        # voice channel is not dynamic, do nothing
        if channel.category_id != await guild_group.dynamiccategory():
            return

        channel_group = self.config.channel(channel)

        if len(channel.members) == 0:
            #restore default config, destroy text channel, destroy role
            #reset admin
            await channel_group.admin.set(None)

            #reset channel
            text_channel = self.bot.get_channel(id=await channel_group.textchannel())
            await channel_group.textchannel.set(None)
            if text_channel:
                await text_channel.delete()

            #reset role
            role_id = await channel_group.role()
            for role in channel.guild.roles:
                if role.id == role_id:
                    await role.delete()
            await channel_group.role.set(None)

            #delete voice channel
            if channel:
                try:
                    await channel.delete()
                except:
                    pass

        else:
            if len(channel.members) == 1:
                #check if there is already an admin
                if not await channel_group.admin():
                    #set admin
                    await channel_group.admin.set(channel.members[0].id)

                    #create text channel
                    overwrites = {
                        channel.guild.default_role: PermissionOverwrite(read_messages=False),
                        channel.guild.me: PermissionOverwrite(read_messages=True)
                    }
                    category_id = await guild_group.dynamiccategory()
                    category = self.bot.get_channel(id = category_id)
                    text_channel = await channel.guild.create_text_channel(name=re.sub(r'\W+', '', channel.name),
                                                                           category=category, overwrites=overwrites)

                    await channel_group.textchannel.set(text_channel.id)

                    #create role
                    role = await channel.guild.create_role(name=re.sub(r'\W+', '', channel.name),
                                                           mentionable=True)
                    await channel_group.role.set(role.id)

                    #set role permission
                    overwrite = PermissionOverwrite()
                    overwrite.read_messages = True
                    await text_channel.set_permissions(target=role, overwrite=overwrite)

                    #create new empty voice channel for other to use
                    await channel.guild.create_voice_channel(name=choice(self.channel_names), category=category)

                    #announce in text channel admin

            #set/take role from members
            role_id = await channel_group.role()
            for role in channel.guild.roles:
                if role.id == role_id:
                    if member in channel.members:
                        await member.add_roles(role)
                    else:
                        #take away role
                        await member.remove_roles(role)



