from .privatechannels import PrivateChannels
import asyncio

def setup(bot):
    n = PrivateChannels(bot)
    #bot.add_listener(n.voice_state_update, "on_voice_state_update")
    loop = asyncio.get_event_loop()
    loop.create_task(n.workqueue())
    bot.add_cog(n)