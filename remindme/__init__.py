from .remindme import RemindMe
import asyncio

def setup(bot):
    n = RemindMe(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.handle_exception())
    bot.add_cog(n)