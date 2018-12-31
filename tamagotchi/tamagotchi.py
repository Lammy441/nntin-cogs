from discord import Member, Message
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Context
from .pet import Pet
from .helper import ExtendedEmbed as Embed
from datetime import datetime
import random
import asyncio

"""
This cog is designed to retain users. Initially they have to be attentive to their pet. At the later stage
the pet will need minimum care. They can also choose to restart the game by raising a new pet.
"""


class Tamagotchi(commands.Cog):
    """
    Take good care of your Tamagotchi

    Your Tamagotchi's happiness increases when it's healthy and not hungry. The happier your Tamagotchi is the
    more points you will earn.
    You can still your pet's hunger by feeding it. Be careful. Your pet can die if you don't feed it for 2 entire
    days. Occasionally your pet will poop. If you don't clean its litter box its health will decrease. Although your
    pet can't die to low health point generation will be slowed down.

    Once you've given your pet enough care he will become an adult. Adult pets cannot die since they've developed
    the skill of hunting their own prey. You can still interact with them. You can also retire them by releasing
    them into the wild. If you ignore your pet he will instead abandon you.
    Adult pets generate points at a much slower rate but they also require minimal care.

    Points can be spent to unlock different pet types. Some require less attention and reach adulthood faster.
    The general twist however is the longer a pet lives and the more attention it needs the more points you are
    going to earn. Some guilds may allow you to unlock roles with those points.
    """

    default_guild = {
        "text_channel_id": None
    }
    default_member = {
        "dead_tamagotchis": [],             # collection of pets that died under you
        "retired_tamagotchis": [],          # collection of adult pets that were released into the wild
        "abandoned_tamagotchis": [],        # collection of adult pets that abandoned you
        "tama_name": None,                  # your pet name
        "tama_points": 0,                   # accumulated points
        "tama_birthdate": None,             # birthday timestamp
        "tama_timestamp": None,             # timestamp of last interaction
        "tama_happiness": None,             # 0-1000 happiness status as of timestamp
        "tama_health": None,                # 0-1000 health status as of timestamp
        "tama_hunger": None,                # 0-1000 hunger status as of timestamp
        "tama_adult_event": None,           # a programmed forced event: your pet is now an adult
        "tama_next_random_event": None,     # a programmed forced event: good thing you can earn points
        "tama_next_event": None,            # a programmed event that will happen, can be postponed by interacting
                                            # usually a bad thing since it means you have been neglecting it
        "tama_next_poop_event": None,       # a programmed event: Your pet poops
        "tama_clean_poop": False,           # whether you have to clean poop
        "owner_id": None                    # that's you!
    }
    conf_id = 800858686

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_member(**self.default_member)
        self.running = True

        self.bot.loop.create_task(self._check())

    async def _check_future_events(self):
        members_dict = await self.config.all_members()
        for guild_id in members_dict.keys():
            for member_id in members_dict[guild_id].keys():
                _dict = members_dict[guild_id][member_id]

                if _dict["tama_name"] is None:
                    continue

                print(_dict)
                if "tama_next_event" in _dict \
                        and _dict["tama_next_event"] is not None \
                        and _dict["tama_next_event"] - datetime.utcnow().timestamp() < 0:
                    # next_event is caused when hunger or health goes below a threshold
                    guild = self.bot.get_guild(guild_id)
                    member = guild.get_member(member_id)
                    await self._status_event(member)

    async def _status_event(self, member: Member):
        async with self.config.member(member)() as member_group:
            pet = Pet(member_group=member_group)
            member_group["tama_next_event"] = pet.get_next_event()

            embed = Embed(color=member.color, title="Did you forget someone?",
                          description=pet.hunger_health_event())
            embed.add_field(name="Hunger", value=pet.hunger_event())
            embed.add_field(name="Health", value=pet.health_event())
            embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')

            async with self.config.guild(member.guild)() as guild_group:
                if "text_channel_id" in guild_group and guild_group["text_channel_id"]:
                    channel = self.bot.get_channel(guild_group["text_channel_id"])
                    await channel.send(embed=embed)
                else:
                    await member.send(embed=embed)

            await self._update(member, member_group)

    async def _check(self):
        while self.running:
            print(datetime.utcnow())
            #try:
            await self._check_future_events()
            #except:
                #print("Something went wrong.")
            await asyncio.sleep(1)

    def __unload(self):
        self.running = False

    async def _update(self, member: Member, member_group):
        """
        calculating the new status of the pet, method is called when
        doing anything health/hunger related with your pet and after a event
        """
        pet = Pet(member_group=member_group)
        member_group["tama_next_event"] = pet.get_next_event()

    @commands.group()
    async def tama(self, ctx):
        """
        Tamagotchi commands
        """
        pass

    @tama.command()
    async def hatch(self, ctx: Context, name):
        """
        Don't have a tamagotchi yet? A nearby farm found some eggs.

        Syntax:
            [p]tama hatch Linley
        """
        async with self.config.member(ctx.author)() as member_group:
            embed = None
            if not member_group["tama_name"]:
                member_group["tama_name"] = name
                unix_time = datetime.utcnow().timestamp()
                member_group["tama_birthdate"] = unix_time
                member_group["tama_timestamp"] = unix_time
                member_group["tama_happiness"] = random.randint(900, 1000)
                member_group["tama_health"] = random.randint(900, 1000)
                member_group["tama_hunger"] = random.randint(900, 1000)
                member_group["owner_id"] = ctx.author.id

                pet = Pet(member_group=member_group)
                member_group["tama_next_event"] = pet.get_next_event()
                member_group["tama_next_poop_event"] = pet.get_next_poop_event()
                # member_group["tama_next_random_event"] = pet.get_next_random_event()

                embed = Embed(color=ctx.author.color)

                embed.populate_fields(pet.hatch_success())

            else:
                await self._update(ctx.author, member_group)

                pet = Pet(member_group=member_group)
                embed = Embed(color=ctx.author.color)
                embed.populate_fields(pet.hatch_fail())
                member_group["tama_points"] = 0.9 * member_group["tama_points"]
                member_group["tama_happiness"] = 0.8 * member_group["tama_happiness"]
            embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')
            await ctx.send(embed=embed)

    @tama.command()
    @checks.is_owner()
    async def kill(self, ctx: Context):
        """
        Developer command only. Sorry you can't kill your pet.
        """
        async with self.config.member(ctx.author)() as member_group:
            member_group.clear()
            await ctx.tick()

    @tama.command()
    async def test(self, ctx: Context):
        async with self.config.member(ctx.author)() as member_group:
            print(member_group)
            print(type(member_group))
