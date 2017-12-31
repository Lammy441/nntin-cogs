from discord.ext import commands
from time import gmtime, strftime
import asyncio

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