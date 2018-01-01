from .tweets import Tweets
import asyncio

def setup(bot):
    n = Tweets(bot)
    bot.add_cog(n)