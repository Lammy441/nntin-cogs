from .crossbar import Crossbar
from redbot.core.bot import Red
from redbot.core.errors import CogLoadError


async def setup(bot: Red):
    try:
        cog = Crossbar(bot)
        await cog.initialize()
    except ImportError:
        raise CogLoadError("You need `crossbar`: https://pypi.org/project/crossbar")
    else:
        bot.add_listener(cog.c_on_message, "on_message")
        bot.add_listener(cog.c_on_typing, "on_typing")
        bot.add_listener(cog.c_on_reaction_add, "on_reaction_add")
        bot.add_listener(cog.c_on_member_join, "on_member_join")
        bot.add_listener(cog.c_on_member_remove, "on_member_remove")
        bot.add_listener(cog.c_on_member_update, "on_member_update")
        bot.add_listener(cog.c_on_voice_state_update, "on_voice_state_update")

        bot.add_cog(cog)
