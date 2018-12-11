from redbot.core import Config, commands, checks
from redbot.core.bot import Red
from discord import Message, User, Member, TextChannel, GroupChannel, DMChannel, Reaction, VoiceState, Guild
from datetime import datetime
from .publisher import DiscordComponent
from autobahn.asyncio.wamp import ApplicationRunner
from .tojson import tojson


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
            def layer(*args):
                def repl(f):
                    return dec(f, *args)
                return repl
            return layer

        @parametrized
        def crossbar_publish(f, _topic: str):
            async def evaluate(*args):
                # todo: create discord guild specific topics instead of having a global one
                topic = "nntin.github.io.discord." + _topic
                print(topic)
                if self._is_enabled:  # and self.comp:
                    payload = tojson([
                        (arg.__class__.__name__, arg) for arg in args
                    ])

                    # print(payload)
                    if self.comp:
                        print("Firing payload. 2")
                        self.comp.publish(topic=topic, payload=payload)
                    return await f(*args)
                else:
                    async def do_nothing():
                        pass
                    return do_nothing
            return evaluate

        # Note: functions below seemingly defined without logic
        # Note: logic is in @crossbar_publish

        @crossbar_publish("ON_MESSAGE")
        async def c_on_message(message: Message):
            pass

        @crossbar_publish("ON_TYPING")
        async def c_on_typing(channel, user, when: datetime):
            pass

        @crossbar_publish("ON_REACTION_ADD")
        async def c_on_reaction_add(reaction: Reaction, user):
            pass

        @crossbar_publish("ON_MEMBER_JOIN")
        async def c_on_member_join(member: Member):
            pass

        @crossbar_publish("ON_MEMBER_REMOVE")
        async def c_on_member_remove(member: Member):
            pass

        @crossbar_publish("ON_MEMBER_UPDATE")
        async def c_on_member_update(before: Member, after: Member):
            pass

        @crossbar_publish("ON_VOICE_STATE_UPDATE")
        async def c_on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
            pass

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


