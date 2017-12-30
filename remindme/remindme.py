from discord.ext import commands
import asyncio, time, re, discord
from time import gmtime, strftime
from datetime import datetime

from redbot.core import Config, checks

class RemindMe:
    """Never forget anything anymore."""
    default_user = {
        "reminders": []
    }
    #default_reminder is not used. It merely shows you the structure.
    default_reminder = {
        'FUTURE': None,
        'TEXT': None
    }
    conf_id = 800858686

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_user(**self.default_user)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def remindme(self, ctx, hms: str, text: str):
        """Sends you <text> when the time (hours:minutes:seconds) is up
        Example:
        [p]remindme 10:00 remind me in 10 minutes"""
        await ctx.trigger_typing()
        pattern = 'remindme (((?P<hours>\d+):)?(?P<minutes>\d{1,2}):)?(?P<seconds>\d{1,2})( (?P<reason>.*))?'
        m = re.search(pattern, ctx.message.content)
        reason = m.group('reason')
        hours, minutes, seconds = m.group('hours'), m.group('minutes'), m.group('seconds')
        if hours == None: hours = 0
        if minutes == None: minutes = 0
        totalSeconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)

        if totalSeconds < 1:
            await ctx.send("Quantity must not be 0 or negative.")
            return
        if len(reason) > 1960:
            await ctx.send("Text is too long.")
            return

        future = int(time.time()+totalSeconds)
        reminder = {
            'FUTURE': future,
            'TEXT': reason
        }
        user_group = self.config.user(ctx.author)
        async with user_group.reminders() as reminders:
            reminders.append(reminder)

        m, s = divmod(totalSeconds, 60)
        h, m = divmod(m, 60)

        embed = discord.Embed(title='⏰ Private messaging in %d:%02d:%02d' % (h, m, s), description=reason)
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text='I will remind you on', icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcfromtimestamp(future)

        #todo: implement warning if bot has no permission to direct message user

        await ctx.send(content=None, embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def forgetme(self, ctx):
        """Removes all your upcoming notifications."""
        await ctx.trigger_typing()
        user_group = self.config.user(ctx.author)
        async with user_group.reminders() as reminders:
            reminders.clear()

        embed = discord.Embed(title='⏰ Reminders cleared')
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)

        await ctx.send(content=None, embed=embed)



    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def showreminders(self, ctx):
        """Show all your reminders."""
        await ctx.trigger_typing()
        user_group = self.config.user(ctx.author)
        reminderEmpty = True
        embed = discord.Embed()
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text='This message was created on', icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcnow()

        async with user_group.reminders() as reminders:
            for reminder in reminders:
                reminderEmpty = False
                timedelta = datetime.utcfromtimestamp(reminder["FUTURE"]) - datetime.utcnow()
                totalSeconds = timedelta.total_seconds()
                m, s = divmod(totalSeconds, 60)
                h, m = divmod(m, 60)
                text = '⏰ Reminder in %d:%02d:%02d' % (h, m, s)
                embed.add_field(name=text, value=reminder["TEXT"], inline=False)
        if reminderEmpty:
            embed.add_field(name="Error", value="You don't have any reminders")
        await ctx.send(content=None, embed=embed)

    async def check_reminders(self):
        while self is self.bot.get_cog("RemindMe"):
            users = self.bot.users
            for user in users:
                user_group = self.config.user(user)
                async with user_group.reminders() as reminders:
                    removeThese = []
                    for reminder in reminders:
                        if reminder["FUTURE"] <= int(time.time()):
                            removeThese.append(reminder)    #removing an element from an array while iterating over an array is a bad idea
                            embed = discord.Embed(title='⏰ Reminder',
                                                  description=reminder["TEXT"])
                            embed.set_author(icon_url=user.avatar_url_as(), name=user.name)
                            embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')
                            await user.send(content=None, embed=embed)
                    for removeThis in removeThese:
                        if removeThis in reminders:
                            reminders.remove(removeThis)
            await asyncio.sleep(5)

    async def handle_exception(self):
        while self is self.bot.get_cog("RemindMe"):
            try:
                await self.check_reminders()
            except:
                #print(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), " Exception consumed in remindme")
                await asyncio.sleep(10)