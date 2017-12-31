from .tweets import Tweets
import asyncio

def setup(bot):
    n = Tweets(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.handle_exception())
    bot.add_cog(n)