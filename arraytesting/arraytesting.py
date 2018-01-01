from discord.ext import commands

from redbot.core import Config

class Arraytesting:
    default_channel = {
        "ids": []
    }
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_channel(**self.default_channel)

    @commands.command()
    async def addid(self, ctx, id:int):
        """adds an id to the config"""
        channel_group = self.config.channel(ctx.channel)
        async with channel_group.ids() as ids:
            ids.append(id)
        await ctx.send("ID has been added!")

    @commands.command()
    async def showconfig(self, ctx):
        """shows the config of the channel"""
        channel_group = self.config.channel(ctx.channel)
        async with channel_group() as channelconfig:
            await ctx.send(channelconfig)

    @commands.command()
    async def showsubconfig(self, ctx):
        """shows a specific part of the config"""
        channel_group = self.config.channel(ctx.channel)
        async with channel_group.ids() as subconfig:
            await ctx.send(subconfig)
