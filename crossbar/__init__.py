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
        bot.add_cog(cog)
