from .privatechannels import PrivateChannels
import asyncio

def setup(bot):
    n = PrivateChannels(bot)
    #bot.add_listener(n.voice_state_update, "on_voice_state_update")
    bot.add_cog(n)