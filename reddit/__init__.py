from .reddit import Reddit
from redbot.core.bot import Red


async def setup(bot: Red):
    cog = Reddit(bot)
    bot.add_cog(cog)
