import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import os
import asyncio
import time
import logging
import re

class RemindMe:
    """Never forget anything anymore."""

    def __init__(self, bot):
        self.bot = bot
        self.reminders = fileIO("data/remindme/reminders.json", "load")

    @commands.command(pass_context=True)
    async def remindme(self, ctx, hms: str, text: str):
        """Sends you <text> when the time (hours:minutes:seconds) is up
        Example:
        [p]remindme 10:00 remind me in 10 minutes"""

        author = ctx.message.author

        pattern = '!remindme (((?P<hours>\d+):)?(?P<minutes>\d{1,2}):)?(?P<seconds>\d{1,2})( (?P<reason>.*))?'

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
        self.reminders.append({"ID" : author.id, "FUTURE" : future, "TEXT" : reason})
        logger.info("{} ({}) set a reminder.".format(author.name, author.id))

        m, s = divmod(totalSeconds, 60)
        h, m = divmod(m, 60)
        await self.bot.say('Private messaging <@%s> in %d:%02d:%02d' % (ctx.message.author.id, h, m, s))

        fileIO("data/remindme/reminders.json", "save", self.reminders)

    @commands.command(pass_context=True)
    async def forgetme(self, ctx):
        """Removes all your upcoming notifications"""
        author = ctx.message.author
        to_remove = []
        for reminder in self.reminders:
            if reminder["ID"] == author.id:
                to_remove.append(reminder)

        if not to_remove == []:
            for reminder in to_remove:
                self.reminders.remove(reminder)
            fileIO("data/remindme/reminders.json", "save", self.reminders)
            await self.bot.say("All your notifications have been removed.")
        else:
            await self.bot.say("You don't have any upcoming notification.")

    async def check_reminders(self):
        while self is self.bot.get_cog("RemindMe"):
            to_remove = []
            for reminder in self.reminders:
                if reminder["FUTURE"] <= int(time.time()):
                    try:
                        await self.bot.send_message(discord.User(id=reminder["ID"]), "You asked me to remind you this:\n{}".format(reminder["TEXT"]))
                    except (discord.errors.Forbidden, discord.errors.NotFound):
                        to_remove.append(reminder)
                    except discord.errors.HTTPException:
                        pass
                    else:
                        to_remove.append(reminder)
            for reminder in to_remove:
                self.reminders.remove(reminder)
            if to_remove:
                fileIO("data/remindme/reminders.json", "save", self.reminders)
            await asyncio.sleep(5)

def check_folders():
    if not os.path.exists("data/remindme"):
        print("Creating data/remindme folder...")
        os.makedirs("data/remindme")

def check_files():
    f = "data/remindme/reminders.json"
    if not fileIO(f, "check"):
        print("Creating empty reminders.json...")
        fileIO(f, "save", [])

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("remindme")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/remindme/reminders.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = RemindMe(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.check_reminders())
    bot.add_cog(n)