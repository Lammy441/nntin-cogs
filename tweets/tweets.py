from discord.ext import commands
from time import gmtime, strftime
from datetime import datetime
from .discordtwitterwebhook import StdOutListener
from .streamasync import StreamAsync
from .embedmenu import EmbedMenu
from .langtoflag import LangToFlag
import asyncio, re, discord, json

try:
    import tweepy
    from tweepy.api import API
    from tweepy import OAuthHandler
except:
    tweepy = None

from redbot.core import Config, checks

#todo:limit commands (e.g. follow only in text channels)
#todo: bug in followlist (repro: try it in a text channel without webhook)


class Tweets(EmbedMenu):
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
                "twitter_ids": []
            }
    default_channel = {
            "IncludeReplyToUser" : True,
            "IncludeRetweet" : True,
            "IncludeUserReply" : True,
            "twitter_ids" : [],
            "webhook_urls" : [] #This will only contain one value. Using an array however since another project of mine can accept multiple webhooks.
        }

    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_global(**self.default_global)
        self.config.register_channel(**self.default_channel)
        self.client = None
        self.stream = None
        self.ltf = LangToFlag()
        loop = asyncio.get_event_loop()
        loop.create_task(self.checkcreds(ctx=None))

    def __unload(self):
        #ending stream so the stream.filter() Thread can properly close on his own.
        if self.stream:
            self.stream.disconnect()


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def getcreds(self, ctx):
        """Gets your tweets API credentials"""
        await ctx.send(await self.config.Twitter())

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
        await ctx.send('Twitter credentials have been set. Testing the Twitter credentials...')
        await ctx.trigger_typing()
        await self.checkcreds(ctx)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def followlist(self, ctx, userIDs):
        """Subscribe to a Twitter List
        Example:
        [p]followlist https://twitter.com/rokxx/lists/dota-2"""
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

        channel_group = self.config.channel(ctx.channel)
        async with channel_group.twitter_ids() as twitter_ids:
            for twitterid in twitterids:
                if twitterid not in twitter_ids:
                    twitter_ids.append(twitterid)
                    added.append(twitterid)
                else:
                    alreadyadded.append(twitterid)
            await ctx.send('added {} twitter users, already added {} twitter users'.format(len(added), len(alreadyadded)))



    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def follow(self, ctx, userIDs):
        """Follows a Twitter user. Get the Twitter ID from http://gettwitterid.com
        Example:
        [p]follow 3065618342"""
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

        embed = discord.Embed()
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text='This message was created on', icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcnow()

        if user_objs:
            for user in user_objs:
                embed.add_field(name='Twitter User added', value='twitter id: {} -> screen name: {}'.format(user.id, user.screen_name), inline=False)
                validtwitterids.append(str(user.id))
        else:
            embed.add_field(name='Error', value='None of the twitter ids were valid.')

        channel_group = self.config.channel(ctx.channel)
        async with channel_group.twitter_ids() as twitter_ids:
            for validtwitterid in validtwitterids:
                if validtwitterid not in twitter_ids:
                    twitter_ids.append(validtwitterid)

        await ctx.send(content=None, embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def getfollow(self, ctx):
        """Displays the followed Twitter users in this channel."""
        await ctx.trigger_typing()
        field_list = []
        channel_group = self.config.channel(ctx.channel)
        async with channel_group.twitter_ids() as twitter_ids:
            user_objs = await self.lookup_users(twitter_ids)
            if user_objs:
                for user in user_objs:
                    field_list.append({'name': '{}'.format(user.screen_name),
                                       'value':
                                           '{} id: {}\nverified'.format(self.ltf.ltf(user.lang), user.id)
                                           if user.verified
                                           else '{} id: {}'.format(self.ltf.ltf(user.lang), user.id),
                                       'inline': True})
            else:
                await ctx.send('You are not following anyone in this channel.')

        embed = discord.Embed(description='This channel tracks the following twitter users:',
                              colour=discord.Colour(value=0x00ff00))
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        await self.embed_menu(ctx=ctx, field_list=field_list, start_at=0, embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def unfollow(self, ctx, twitter_ids):
        """Unfollow Twitter IDs"""
        pattern = '((?P<id>\d+)( |,|)+)'
        twitterids = []
        for m in re.finditer(pattern, ctx.message.content):
            twitterids.append(str(m.group('id')))

        unfollowed = []
        notfound = []
        channel_group = self.config.channel(ctx.channel)
        async with channel_group.twitter_ids() as twitter_ids:
            for twitterid in twitterids:
                if twitterid in twitter_ids:
                    twitter_ids.remove(twitterid)
                    unfollowed.append(twitterid)
                else:
                    notfound.append(twitterid)

        await ctx.send('unfollowed: {}, not found: {}'.format(unfollowed, notfound))

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def unfollowall(self, ctx):
        """Clears the Twitter list in the channel"""
        channel_group = self.config.channel(ctx.channel)
        async with channel_group.twitter_ids() as twitter_ids:
            await ctx.send('Deleted {} twitter ids.'.format(len(twitter_ids)))
            twitter_ids.clear()


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def createwh(self, ctx, createNew=True):
        """Creates a webhook for the text channel if it doesn't exist"""
        await self.checkwh(ctx, createNew=True)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def disconnect(self, ctx):
        """Disconnects the twitter stream"""
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

        if self.stream:
            self.stream.disconnect()

        await ctx.send('building')
        await ctx.trigger_typing()

        async with self.config.twitter_ids() as twitter_ids:
            async with self.config.Discord() as Discord:
                Discord.clear()


                #todo: fix bug. it's the exact same channel_config multiple times
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

            await ctx.send('You are currently tracking {} twitter users'.format(len(twitter_ids)))

        async with self.config.Discord() as Discord:
            l = StdOutListener(dataD=Discord)
        async with self.config.Twitter() as Twitter:
            auth = OAuthHandler(Twitter['consumer_key'], Twitter['consumer_secret'])
            auth.set_access_token(Twitter['access_token'], Twitter['access_token_secret'])


        self.stream = StreamAsync(auth, l)  #overwriting tweepy.Stream since it does not allow manual setting async to True

        async with self.config.twitter_ids() as twitter_ids:
            self.stream.filter(follow=twitter_ids)

        await ctx.send('Twitter stream is now active!')

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
        async with channel_group.webhook_urls() as webhook_urls:
            if not webhook_urls:
                webhook = await ctx.channel.create_webhook(name='tweets')
                webhook_urls.append(webhook.url)
            else:
                if createNew:
                    webhook_urls[0] = (await ctx.channel.create_webhook(name='tweets')).url
            if createNew:
                await ctx.send('Webhook created: {}'.format(webhook_urls[0]))


    async def checkcreds(self, ctx):
        if tweepy == None:
            if ctx:
                await ctx.send('Tweepy is not installed. Install tweepy and reload the cog.')
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
            if ctx:
                await ctx.send('Twitter credentials are invalid.')
            self.client = None
            return
        else:
            if ctx:
                await ctx.send('Twitter credentials are valid.')