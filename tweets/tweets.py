from discord.ext import commands
from time import gmtime, strftime
from datetime import datetime
import asyncio, re, discord

try:
    import tweepy
    from tweepy.api import API
    from tweepy.streaming import StreamListener
except:
    tweepy = None

from redbot.core import Config, checks

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
                "twitter_ids": []
            }
    default_channel = {
            "IncludeReplyToUser" : False,
            "IncludeRetweet" : False,
            "IncludeUserReply" : False,
            "twitter_ids" : [],
            "webhook_urls" : [] #This will only contain one value. Using an array however since another project of mine can accept multiple webhooks.
        }

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_global(**self.default_global)
        self.config.register_channel(**self.default_channel)
        self.client = None
        loop = asyncio.get_event_loop()
        loop.create_task(self.checkcreds(ctx=None))




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
    async def follow(self, ctx, userIDs):
        """Follows a Twitter user. Get the Twitter ID from http://gettwitterid.com
        Example:
        [p]follow 3065618342"""
        if self.client == None:
            await ctx.send("You need to set your Twitter credentials")
            return

        #await self.checkwh(ctx, createNew=False) #todo:enable it later
        pattern = '((?P<id>\d+)( |,|)+)'
        twitterids = []
        for m in re.finditer(pattern, ctx.message.content):
            twitterids.append(str(m.group('id')))

        validtwitterids = []
        user_objs = []
        user_count = len(twitterids)

        for i in range(0, int((user_count // 100)) + 1):
            try:
                user_objs.extend(
                    self.client.lookup_users(user_ids=twitterids[i * 100:min((i + 1) * 100, user_count)]))
            except:
                print(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), " Error while looking up twitter ids (possibly non are valid)")

        embed = discord.Embed()
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text='This message was created on', icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcnow()


        for user in user_objs:
            embed.add_field(name='Twitter User added', value='twitter id: {} -> screen name: {}'.format(user.id, user.screen_name), inline=False)
            validtwitterids.append(str(user.id))

        channel_group = self.config.channel(ctx.channel)
        async with channel_group.twitter_ids() as twitter_ids:
            twitter_ids.extend(validtwitterids)

        await ctx.send(content=None, embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @checks.is_owner()
    async def createwh(self, ctx, createNew=True):
        """Creates a webhook for the text channel if it doesn't exist"""
        await self.checkwh(ctx, createNew=True)

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
            await ctx.send('Webhook created.')


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


    async def handle_exception(self):
        while self is self.bot.get_cog("Tweets"):
            try:
                await asyncio.sleep(10)
                #await self.check_reminders()
            except:
                print(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), " Exception consumed in remindme")
                await asyncio.sleep(10)