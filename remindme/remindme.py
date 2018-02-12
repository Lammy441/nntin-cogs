from discord.ext import commands
import asyncio
import re
import discord
from time import gmtime, strftime
from datetime import datetime
from redbot.core import Config, checks
from discord import Client


class RemindMe:
    """Never forget anything anymore."""
    default_user = {
        "reminders": []
    }
    # default_reminder is not used. It merely shows you the structure.
    default_reminder = {
        'FUTURE': None,
        'TEXT': None
    }
    conf_id = 800858686

    def __init__(self, bot:Client):
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_user(**self.default_user)
        self.bot.loop.create_task(self.handle_exception())

    @checks.is_owner()
    @commands.command()
    async def clearreminders(self, ctx):
        """Owner only. Drops all reminders - including reminders from other users."""
        await ctx.trigger_typing()
        await self.config.clear_all_users()
        await ctx.send('Dropped all reminders.')

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
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)

        if total_seconds < 1:
            await ctx.send("Quantity must not be 0 or negative.")
            return
        if len(reason) > 1960:
            await ctx.send("Text is too long.")
            return

        future = datetime.utcnow().timestamp() + total_seconds

        reminder = {
            'FUTURE': future,
            'TEXT': reason
        }
        user_group = self.config.user(ctx.author)
        async with user_group.reminders() as reminders:
            reminders.append(reminder)

        m, s = divmod(total_seconds, 60)
        h, m = divmod(m, 60)

        embed = discord.Embed(title='⏰ Private messaging in %d:%02d:%02d' % (h, m, s), description=reason)
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text='I will remind you on', icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcfromtimestamp(future)

        # todo: implement warning if bot has no permission to direct message user

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
        reminder_empty = True
        embed = discord.Embed()
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text='This message was created on', icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcnow()

        async with user_group.reminders() as reminders:
            for reminder in reminders:
                reminder_empty = False
                time_delta = reminder["FUTURE"] - datetime.utcnow().timestamp()
                total_seconds = int(time_delta)
                m, s = divmod(total_seconds, 60)
                h, m = divmod(m, 60)
                text = '⏰ Reminder in %d:%02d:%02d' % (h, m, s)
                embed.add_field(name=text, value=reminder["TEXT"], inline=False)
        if reminder_empty:
            embed.add_field(name="Error", value="You don't have any reminders")
        await ctx.send(content=None, embed=embed)

    async def check_reminders(self):
        reminders_dict = await self.config.all_users()
        remove_user_ids = []
        for user_id, value in reminders_dict.items():
            remove_reminders = []
            reminders = value['reminders']
            for reminder in reminders:
                if reminder["FUTURE"] <= datetime.utcnow().timestamp():
                    user = self.bot.get_user(user_id)

                    remove_reminders.append(reminder)
                    embed = discord.Embed(title='⏰ Reminder',
                                          description=reminder["TEXT"])
                    embed.set_author(icon_url=user.avatar_url_as(), name=user.name)
                    embed.set_footer(text='NNTin cogs', icon_url='https://i.imgur.com/6LfN4cd.png')
                    await user.send(content=None, embed=embed)
            for remove_this in remove_reminders:
                if remove_this in reminders:
                    reminders.remove(remove_this)

            if not reminders:  # reminder list is empty
                remove_user_ids.append(user_id)

        for remove_this in remove_user_ids:
            reminders_dict.pop(remove_this, None)   # todo: this does not remove the user, find a solution

        await asyncio.sleep(5)

    async def handle_exception(self):
        while self is self.bot.get_cog("RemindMe"):  # I can't get __unload() to work, so I use this
            try:
                await self.check_reminders()
            except:
                print(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), " Exception consumed in remindme")
                await asyncio.sleep(5)
