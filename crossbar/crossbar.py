from redbot.core import Config, commands, checks
from redbot.core.bot import Red
from discord import Message, User, Member, TextChannel, GroupChannel, DMChannel, Reaction, VoiceState
from discord.abc import Messageable
from datetime import datetime


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

    async def initialize(self):
        self._is_enabled = await self._config.enabled()

    # Note: Using isinstance for debugging reasons. (Make IDE show available methods, attributes, ...)
    async def c_on_message(self, message: Message):
        if self._is_enabled:
            pass

    async def c_on_typing(self, channel, user, when: datetime):
        if self._is_enabled:
            if isinstance(channel, TextChannel) or isinstance(channel, GroupChannel) or isinstance(channel, DMChannel):
                pass
            if isinstance(user, User) or isinstance(user, Member):
                pass

    async def c_on_reaction_add(self, reaction: Reaction, user):
        if self._is_enabled:
            if isinstance(user, User) or isinstance(user, Member):
                pass

    async def c_on_member_join(self, member: Member):
        if self._is_enabled:
            pass

    async def c_on_member_remove(self, member: Member):
        if self._is_enabled:
            pass

    async def c_on_member_update(self, before: Member, after: Member):
        if self._is_enabled:
            pass

    async def c_on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if self._is_enabled:
            pass

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


