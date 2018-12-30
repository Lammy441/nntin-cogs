from .tamagotchi import Tamagotchi
from redbot.core.bot import Red


async def setup(bot: Red):
    cog = Tamagotchi(bot)
    bot.add_cog(cog)
