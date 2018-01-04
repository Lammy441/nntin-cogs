from discord.ext import commands
from time import gmtime, strftime
from datetime import datetime
from .discordtwitterwebhook import StdOutListener
from .streamasync import StreamAsync
from .embedfieldmenu import EmbedFieldMenu
from .langtoflag import LangToFlag
import asyncio, re, discord, json
from random import choice

try:
    import tweepy
    from tweepy.api import API
    from tweepy import OAuthHandler
except:
    tweepy = None

from redbot.core import Config, checks

#todo: config for owner, allow/disallow bot to be used by others
#todo: set webhook avatar as owner avatar

class Tweets():
    """Cog for displaying info from Twitter's API"""
    conf_id = 800858686
    default_global = {
            "Twitter": {
                "consumer_key": "",
                "consumer_secret": "",
                "access_token": "",
                "access_token_secret": ""
            },
            "Discord": [],
            "twitter_ids": [],
            "autorestart": False    #todo: set to True in build, set to False in disconnect, write function
        }
    default_channel = {
            "IncludeReplyToUser" : True,
            "IncludeRetweet" : True,
            "IncludeUserReply" : True,
            "twitter_ids" : [],
            "webhook_urls" : [] #This will only contain one value. Using an array however since another project of mine can accept multiple webhooks.
        }

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_global(**self.default_global)
        self.config.register_channel(**self.default_channel)
        self.client = None
        self.stream = None
        self.ltf = LangToFlag()
        self.fieldmenu = EmbedFieldMenu(self.bot)
        self.isbuilding = False
        loop_checkcreds = asyncio.get_event_loop()
        loop_checkcreds.create_task(self.checkcreds(message=None))

        loop_checkautorestart = asyncio.get_event_loop()
        loop_checkautorestart.create_task(self.checkautorestart())

    def __unload(self):
        """ending stream so the stream.filter() Thread can properly close on his own."""
        if self.stream:
            self.stream.disconnect()


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def getcreds(self, ctx):
        """Gets your tweets API credentials"""
        async with self.config.Twitter() as Twitter:
            embed = discord.Embed()
            embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
            embed.set_footer(text='Tweets', icon_url='https://i.imgur.com/6LfN4cd.png')
            embed.timestamp = datetime.utcnow()

            embed.add_field(name='consumer_key', value=Twitter['consumer_key'], inline=False)
            embed.add_field(name='consumer_secret', value=Twitter['consumer_secret'], inline=False)
            embed.add_field(name='access_token', value=Twitter['access_token'], inline=False)
            embed.add_field(name='access_token_secret', value=Twitter['access_token_secret'], inline=False)

            await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def setcreds(self, ctx, consumer_key, consumer_secret, access_token, access_token_secret):
        """Sets your tweets API credentials"""
        await self.config.Twitter.set({
                    "consumer_key": consumer_key,
                    "consumer_secret": consumer_secret,
                    "access_token": access_token,
                    "access_token_secret": access_token_secret
                })
        message = await ctx.send('Twitter credentials have been set. Testing the Twitter credentials...')
        await self.checkcreds(message)

    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    async def followlist(self, ctx, userIDs):
        """Subscribe to a Twitter List
        Example:
        [p]followlist https://twitter.com/rokxx/lists/dota-2"""

        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "twitter_ids" not in (await channel_group()).keys():
            await channel_group.twitter_ids.set([])


        if self.client == None:
            await ctx.send("You need to set your Twitter credentials")
            return

        await ctx.trigger_typing()
        await self.checkwh(ctx, createNew=False)

        twitterids = []
        pattern = 'https?:\/\/(?:www\.)?twitter\.com\/(?P<twittername>[a-zA-Z0-9]+)\/lists\/(?P<listname>[a-zA-Z0-9-]+)'
        for m in re.finditer(pattern, ctx.message.content, re.I):
            for member in tweepy.Cursor(self.client.list_members, m.group('twittername'), m.group('listname')).items():
                twitterID = member._json['id_str']
                if twitterID not in twitterids:
                    twitterids.append(twitterID)

        added = []
        alreadyadded = []

        async with channel_group.twitter_ids() as twitter_ids_config:
            for twitterid in twitterids:
                if twitterid not in twitter_ids_config:
                    twitter_ids_config.append(twitterid)
                    added.append(twitterid)
                else:
                    alreadyadded.append(twitterid)
            await ctx.send('{} twitter users have been to this channel added.\n{} twitter users were already added to this channel.'.format(len(added), len(alreadyadded)))

        field_list = await self.twitter_ids_in_field(twitterids)

        if field_list:
            embed = discord.Embed(description='The URL you provided contained {} Twitter users:'.format(len(added)+len(alreadyadded)),
                                  colour=discord.Colour(value=0x00ff00))
            embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
            await self.fieldmenu.field_menu(ctx=ctx, field_list=field_list, start_at=0, embed=embed, autodelete=True)

    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    async def follow(self, ctx, userIDs):
        """Follows a Twitter user. Get the Twitter ID from http://gettwitterid.com
        Example:
        [p]follow 3065618342"""

        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "twitter_ids" not in (await channel_group()).keys():
            await channel_group.twitter_ids.set([])


        if self.client == None:
            await ctx.send("You need to set your Twitter credentials")
            return

        await ctx.trigger_typing()
        await self.checkwh(ctx, createNew=False)
        pattern = '((?P<id>\d+)( |,|)+)'
        twitterids = []
        for m in re.finditer(pattern, ctx.message.content):
            twitterids.append(str(m.group('id')))



        validtwitterids = []
        user_objs = await self.lookup_users(twitterids)
        if user_objs:
            for user in user_objs:
                validtwitterids.append(str(user.id))

        field_list = await self.twitter_ids_in_field(validtwitterids)

        if field_list:
            embed = discord.Embed(
                description='{} of {} Twitter users were valid:'.format(len(validtwitterids), len(twitterids)),
                colour=discord.Colour(value=0x00ff00))
            embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
            await self.fieldmenu.field_menu(ctx=ctx, field_list=field_list, start_at=0, embed=embed, autodelete=True)
        else:
            await ctx.send('None of the Twitter IDs were valid.')

        async with channel_group.twitter_ids() as twitter_ids_config:
            for validtwitterid in validtwitterids:
                if validtwitterid not in twitter_ids_config:
                    twitter_ids_config.append(validtwitterid)


    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    async def getfollow(self, ctx):
        """Displays the followed Twitter users in this channel."""
        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "twitter_ids" not in (await channel_group()).keys():
            await channel_group.twitter_ids.set([])

        await ctx.trigger_typing()

        twitterids = []
        async with channel_group.twitter_ids() as twitter_ids:
            for twitter_id in twitter_ids: twitterids.append(twitter_id)

        field_list = await self.twitter_ids_in_field(twitter_ids)

        if field_list:
            embed = discord.Embed(description='This channel tracks the following twitter users:',
                                  colour=discord.Colour(value=0x00ff00))
            embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
            await self.fieldmenu.field_menu(ctx=ctx, field_list=field_list, start_at=0, embed=embed)
        else:
            await ctx.send('You are not following anyone in this channel.')

    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    async def unfollow(self, ctx, twitter_ids):
        """Unfollow Twitter IDs"""
        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "twitter_ids" not in (await channel_group()).keys():
            await channel_group.twitter_ids.set([])
        pattern = '((?P<id>\d+)( |,|)+)'
        twitterids = []
        for m in re.finditer(pattern, ctx.message.content):
            twitterids.append(str(m.group('id')))

        removed = []
        notfound = []

        async with channel_group.twitter_ids() as twitter_ids:
            for twitterid in twitterids:
                if twitterid in twitter_ids:
                    twitter_ids.remove(twitterid)
                    removed.append(twitterid)
                else:
                    notfound.append(twitterid)

        await ctx.send('removed: {}, not found: {}'.format(removed, notfound))

    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    async def unfollowall(self, ctx):
        """Clears the Twitter list in the channel"""
        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "twitter_ids" not in (await channel_group()).keys():
            await channel_group.twitter_ids.set([])
        async with channel_group.twitter_ids() as twitter_ids:
            await ctx.send('Twitter List was cleared on this channel. RIP {} Twitter users.'.format(len(twitter_ids)))
            twitter_ids.clear()


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def clearall(self, ctx):
        """clears the entire config"""
        #for guild in self.bot.guilds:  # go through every server
        #    for channel in guild.channels:  # go through every text channel
        #        channel_group = self.config.channel(channel)
        #        async with channel_group() as channel_config:
        #            channel_config.clear()

        #await self.config.clear_all()
        await self.config.clear_all_channels()
        await ctx.send('cleared')

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def getcount(self, ctx):
        """gets # followed twitter user"""
        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "twitter_ids" not in (await channel_group()).keys():
            await channel_group.twitter_ids.set([])
        async with channel_group.twitter_ids() as twitter_ids:
            await ctx.send(len(twitter_ids))


    @commands.command()
    @commands.bot_has_permissions(manage_webhooks=True)
    async def createwh(self, ctx, createNew=True):
        """Creates a webhook for the text channel"""
        await self.checkwh(ctx, createNew=True)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def disconnect(self, ctx):
        """Disconnects the twitter stream"""
        await self.config.autorestart.set(False)
        if self.stream:
            await ctx.send('Calling disconnect')
            self.stream.disconnect()
            self.stream = None
        else:
            await ctx.send('Disconnect could not be called.')

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def build(self, ctx):
        """Builds and starts the twitter stream. This may take a while."""
        await self.config.autorestart.set(True)
        await self.build_(ctx)

    async def checkautorestart(self):
        if await self.config.autorestart():
            await self.build_()

    async def build_(self, ctx=None):
        if self.isbuilding:
            if ctx:
                await ctx.send('It is already building.')
            return
        self.isbuilding = True

        if self.stream:
            self.stream.disconnect()

        if ctx:
            await ctx.send('building')
            await ctx.trigger_typing()

        async with self.config.twitter_ids() as twitter_ids:
            twitter_ids.clear()
            async with self.config.Discord() as Discord:
                Discord.clear()
                for guild in self.bot.guilds:   #go through every server
                    for channel in guild.channels:  #go through every text channel
                        channel_group = self.config.channel(channel)
                        async with channel_group() as channel_config:
                            if 'twitter_ids' in channel_config and 'webhook_urls' in channel_config:
                                if channel_config['twitter_ids'] and channel_config['webhook_urls']:
                                    Discord.append(channel_config)
            for instance in Discord:
                for twitter_id in instance['twitter_ids']:
                    if twitter_id not in twitter_ids:
                        twitter_ids.append(twitter_id)
            if ctx:
                await ctx.send('You are currently tracking {} twitter users'.format(len(twitter_ids)))

        async with self.config.Discord() as Discord:
            l = StdOutListener(dataD=Discord)
        async with self.config.Twitter() as Twitter:
            auth = OAuthHandler(Twitter['consumer_key'], Twitter['consumer_secret'])
            auth.set_access_token(Twitter['access_token'], Twitter['access_token_secret'])


        self.stream = StreamAsync(auth, l)  #overwriting tweepy.Stream since it does not allow manual setting async to True

        async with self.config.twitter_ids() as twitter_ids:
            if twitter_ids:
                self.stream.filter(follow=twitter_ids)

        self.isbuilding = False

        if ctx:
            await ctx.send('Twitter stream is now active!')

    async def twitter_ids_in_field(self, twitter_ids):
        field_list = []
        user_objs = await self.lookup_users(twitter_ids)

        for user in user_objs:
            field_list.append({'name': '{}'.format(user.screen_name),
                               'value':
                                   '{} id: {}\nverified'.format(self.ltf.ltf(user.lang), user.id)
                                   if user.verified
                                   else '{} id: {}'.format(self.ltf.ltf(user.lang), user.id),
                               'inline': True})
        return field_list

    async def lookup_users(self, twitterids):
        user_objs = []
        user_count = len(twitterids)

        for i in range(0, int((user_count // 100)) + 1):
            try:
                user_objs.extend(
                    self.client.lookup_users(user_ids=twitterids[i * 100:min((i + 1) * 100, user_count)]))
            except:
                print(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), " Error while looking up twitter ids (possibly non are valid)")
        return user_objs

    async def checkwh(self, ctx, createNew):
        channel_group = self.config.channel(ctx.channel)
        # weird bug where default keys are not generated so I have to do it.
        if "webhook_urls" not in (await channel_group()).keys():
            await channel_group.webhook_urls.set([])

        async with channel_group.webhook_urls() as webhook_urls:
            if not webhook_urls:
                webhook = await ctx.channel.create_webhook(name='tweets')
                webhook_urls.append(webhook.url)
            else:
                if createNew:
                    webhook_urls[0] = (await ctx.channel.create_webhook(name='tweets')).url
            if createNew:
                await ctx.send('Webhook created: {}'.format(webhook_urls[0]))


    async def checkcreds(self, message):
        if tweepy == None:
            if message:
                await message.edit(content=message.content + '\nTweepy is not installed. Install tweepy and reload the cog.')
            return

        twittercreds = await self.config.Twitter()

        auth = tweepy.OAuthHandler(twittercreds['consumer_key'],
                                   twittercreds['consumer_secret'])
        auth.set_access_token(twittercreds['access_token'],
                              twittercreds['access_token_secret'])
        self.client = tweepy.API(auth)

        try:
            self.client.verify_credentials()
        except:
            if message:
                await message.edit(content=message.content + '\nTwitter credentials are invalid.')
            self.client = None
            return
        else:
            if message:
                await message.edit(content=message.content + '\nTwitter credentials are valid.')