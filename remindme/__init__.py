from .remindme import RemindMe
import asyncio

def setup(bot):
    n = RemindMe(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.check_reminders())
    bot.add_cog(n)