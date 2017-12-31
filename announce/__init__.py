from .announce import Announce

def setup(bot):
    bot.add_cog(Announce(bot))