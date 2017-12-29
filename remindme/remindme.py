from discord.ext import commands
import asyncio
import time
import re

from redbot.core import Config

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

    def __init__(self, bot):
        self.bot = bot
        self.conf_id = 800858686
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_user(**self.default_user)

    @commands.command()
    async def remindme(self, ctx, hms: str, text: str):
        """Sends you <text> when the time (hours:minutes:seconds) is up
        Example:
        [p]remindme 10:00 remind me in 10 minutes"""

        pattern = 'remindme (((?P<hours>\d+):)?(?P<minutes>\d{1,2}):)?(?P<seconds>\d{1,2})( (?P<reason>.*))?'

        m = re.search(pattern, ctx.message.content)
        reason = m.group('reason')
        hours, minutes, seconds = m.group('hours'), m.group('minutes'), m.group('seconds')
        if hours == None: hours = 0
        if minutes == None: minutes = 0
        totalSeconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)

        if totalSeconds < 1:
            await self.bot.say("Quantity must not be 0 or negative.")
            return
        if len(reason) > 1960:
            await self.bot.say("Text is too long.")
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
        await ctx.send('Private messaging <@%s> in %d:%02d:%02d' % (ctx.message.author.id, h, m, s))

    @commands.command()
    async def forgetme(self, ctx):
        """Removes all your upcoming notifications."""
        user_group = self.config.user(ctx.author)
        async with user_group.reminders() as reminders:
            reminders.clear()
        await ctx.send("Reminders are cleared")

    @commands.command()
    async def showreminders(self, ctx):
        """Show all your reminders."""
        user_group = self.config.user(ctx.author)
        async with user_group.reminders() as reminders:
            await ctx.send("Your reminders are: {}".format(reminders))


    async def check_reminders(self):
        while self is self.bot.get_cog("RemindMe"):
            users = self.bot.users
            for user in users:
                user_group = self.config.user(user)
                async with user_group.reminders() as reminders:
                    for reminder in reminders:
                        if reminder["FUTURE"] <= int(time.time()):
                            await user.send("You asked me to remind you this: \n{}".format(reminder["TEXT"]))
                            reminders.remove(reminder)
                            break       #removing multiple times in a loop from an array is dangerous -> break: remove only once from a loop
            await asyncio.sleep(5)
            print('heartbeat')
