from .remindme import RemindMe
import asyncio

def setup(bot):
    n = RemindMe(bot)
    bot.add_cog(n)