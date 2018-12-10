from redbot.core import Config, commands, checks
from redbot.core.bot import Red
from discord import Message, User, Member, TextChannel, GroupChannel, DMChannel, Reaction, VoiceState
from datetime import datetime
from .publisher import DiscordComponent
from autobahn.asyncio.wamp import ApplicationRunner
import json


class Crossbar(commands.Cog):
    """Crossbar client.

    The Crossbar client enables RPC and PubSub.
    """

    default_global_settings = {
        "enabled": True,
        "crossbar": {
            "URI": None,
            "user": None,
            "secret": None
        }
    }

    default_guild_settings = {

    }

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot

        self._config = Config.get_conf(cog_instance=self, identifier=800858686)
        self._config.register_global(**self.default_global_settings)
        self._config.register_guild(**self.default_guild_settings)
        self._is_enabled = None
        self.comp = None

    async def initialize(self):
        self._is_enabled = await self._config.enabled()

        def parametrized(dec):
            def layer(*args, **kwargs):
                def repl(f):
                    return dec(f, *args, **kwargs)
                return repl
            return layer

        @parametrized
        def crossbar_publish(f, topic: str):
            async def evaluate(*args, **kwargs):
                print(topic)
                if self._is_enabled: # and self.comp:
                    return await f(*args, **kwargs)
                else:
                    async def do_nothing():
                        pass
                    return do_nothing
            return evaluate

        # Note: Using isinstance for debugging reasons. (Make IDE show available methods, attributes, ...)

        @crossbar_publish("ON_MESSAGE")
        async def c_on_message(message: Message):
            print(message.content)

            for slot in message.__slots__:
                if not slot.startswith('_') and hasattr(message, slot):
                    res = getattr(message, slot)
                    print(slot, res, type(res))

        @crossbar_publish("ON_TYPING")
        async def c_on_typing(channel, user, when: datetime):
            if isinstance(channel, TextChannel) or isinstance(channel, GroupChannel) or isinstance(channel, DMChannel):
                pass
            if isinstance(user, User) or isinstance(user, Member):
                pass
            print(when)

        @crossbar_publish("ON_REACTION_ADD")
        async def c_on_reaction_add(reaction: Reaction, user):
            if isinstance(user, User) or isinstance(user, Member):
                pass
            print(user)

        @crossbar_publish("ON_MEMBER_JOIN")
        async def c_on_member_join(member: Member):
            print(member)

        @crossbar_publish("ON_MEMBER_REMOVE")
        async def c_on_member_remove(member: Member):
            print(member)

        @crossbar_publish("ON_MEMBER_UPDATE")
        async def c_on_member_update(before: Member, after: Member):
            print(after)

        @crossbar_publish("ON_VOICE_STATE_UPDATE")
        async def c_on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
            print(member)

        self.bot.add_listener(c_on_message, "on_message")
        self.bot.add_listener(c_on_typing, "on_typing")
        self.bot.add_listener(c_on_reaction_add, "on_reaction_add")
        self.bot.add_listener(c_on_member_join, "on_member_join")
        self.bot.add_listener(c_on_member_remove, "on_member_remove")
        self.bot.add_listener(c_on_member_update, "on_member_update")
        self.bot.add_listener(c_on_voice_state_update, "on_voice_state_update")

    @commands.command(name="connect")
    async def c_connect(self, ctx):
        self.comp = DiscordComponent(bot=self.bot)
        runner = ApplicationRunner(url="ws://crosku.herokuapp.com/ws", realm="realm1")
        await runner.run(make=self.comp, start_loop=False)

    @commands.group(name="crossbarset")
    @checks.admin_or_permissions(manage_guilds=True)
    async def _crossbarset(self, ctx):
        """Configure your crossbar.

        Configure your crossbar router, specify what messages to send, specify what RPCs you want to register."""
        pass

    @_crossbarset.command(name="creds")
    @checks.is_owner()
    async def _set_creds(self, ctx, crossbar_URI: str, user: str, secret: str):
        """Configure connection to your crossbar router. (This assumes you have a crossbar router running.)"""
        # todo: test the configured crossbar connection
        crossbar_config = {"URI": crossbar_URI, "user": user, "secret": secret}
        await self._config.crossbar.set(crossbar_config)
        await ctx.send("Crossbar connection configured.")

    @_crossbarset.command(name="toggle")
    async def _toggle_enable(self, ctx):
        """Enable/disable crossbar by invoking this command"""
        self._is_enabled = not self._is_enabled
        await self._config.enabled.set(self._is_enabled)
        if self._is_enabled:
            await ctx.send("Crossbar enabled.")
        else:
            await ctx.send("Crossbar disabled.")

    def __unload(self):
        # todo: is relevant when starting a crossbar router alongside Red-DiscordBot
        # todo: for now you have to run your crossbar router yourself
        pass


