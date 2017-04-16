from random import choice as randchoice
from discord.ext import commands
from queue import Queue
import threading, discord, asyncio, random, re
from .utils.dataIO import dataIO
from .utils import checks
try:
    import tweepy as tw
    from tweepy.api import API
    from tweepy.streaming import StreamListener
    twInstalled = True
except:
    twInstalled = False
import os

#todo: handle http timeout error. Stream will stop working once temporary connection failure occurs.
#todo: implement restart


class TweetListener(StreamListener):
    def __init__(self, api=None, interrupt=False, queue=None):
        self.api = api or API()             #api access to Twitter
        self.interrupt = interrupt          #interrupt signal for ending stream.filter
        self.queue = queue                  #place the tweets in a queue

    def on_status(self, status):

        #retrieve the basic information
        message = {
            "name": status.user.name,
            "created_at": status.created_at,
            "screen_name": status.user.screen_name,
            "user_id": status.user.id_str,
            "status_id": status.id,
            "media_url": '',
            "avatar_url": status.user.profile_image_url
        }

        #if there is a full status text take that instead
        message['status'] = status.text
        if hasattr(status, "extended_tweet"):
            message['status'] = status.extended_tweet['full_text']

        #replace the twitter URL shortened URLs with their unshortened URL
        for url in status.entities['urls']:
            if url['expanded_url'] != None:
                message['status'] = message['status'].replace(url['url'], "[%s](%s)" % (url['display_url'], url['expanded_url']))

        #if twitter users have been mentioned, add a link to their twitter handle
        for userMention in status.entities['user_mentions']:
            message['status'] = message['status'].replace('@%s' % userMention['screen_name'], '[@%s](http://twitter.com/%s)' % (
            userMention['screen_name'], userMention['screen_name']))

        #if there is a photo, save it
        message['media_url'] = ''
        if hasattr(status, 'extended_tweet'):
            if 'media' in status.extended_tweet['entities']:
                for media in status.extended_tweet['entities']['media']:
                    if media['type'] == 'photo':
                        message['media_url'] = media['media_url']

        #see above
        if 'media' in status.entities:
            for media in status.entities['media']:
                if media['type'] == 'photo':
                    message['media_url'] = media['media_url']

        #put the result to a queue. It will be handled later.
        self.queue.put(message)

        #if there is an interrupt signal end the stream
        if self.interrupt == False:
            return True         #stream filter continue
        else:
            return False        #stream filter shutdown



class Tweets():
    """Cog for displaying info from Twitter's API"""
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/tweets/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        self.api = None                                             #required for getuser (tw.Cursor, ...)
        self.auth = None                                            #required for stream.filter (StreamListener, ...)
        self.twitterStreamActive = False
        self.l = None                                               #StreamListener
        self.colours = ['7f0000', '535900', '40d9ff', '8c7399', 'd97b6c', 'f2ff40', '8fb6bf', '502d59', '66504d',
                       '89b359', '00aaff', 'd600e6', '401100', '44ff00', '1a2b33', 'ff00aa', 'ff8c40', '17330d',
                       '0066bf', '33001b', 'b39886', 'bfffd0', '163a59', '8c235b', '8c5e00', '00733d', '000c59',
                       'ffbfd9', '4c3300', '36d98d', '3d3df2', '590018', 'f2c200', '264d40', 'c8bfff', 'f23d6d',
                       'd9c36c', '2db3aa', 'b380ff', 'ff0022', '333226', '005c73', '7c29a6']
        if 'consumer_key' in list(self.settings.keys()):
            self.consumer_key = self.settings['consumer_key']
        if 'consumer_secret' in list(self.settings.keys()):
            self.consumer_secret = self.settings['consumer_secret']
        if 'access_token' in list(self.settings.keys()):
            self.access_token = self.settings['access_token']
        if 'access_secret' in list(self.settings.keys()):
            self.access_secret = self.settings['access_secret']
        if              'consumer_key' in list(self.settings.keys()) and \
                        'consumer_secret' in list(self.settings.keys()) and \
                        'access_token' in list(self.settings.keys()) and \
                        'access_secret' in list(self.settings.keys()):
            self.api = self.authenticate()

    def __unload(self):
        """Ends the stream.filter thread and ends user_loop"""
        if self.l != None:
            self.l.interrupt = True
        self.twitterStreamActive = False


    def authenticate(self):
        """Authenticate with Twitter's API"""
        if self.api == None:        #if not authenticated, do it now.
            if self.consumer_key and self.consumer_secret and self.access_token and self.access_secret:
                auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
                auth.set_access_token(self.access_token, self.access_secret)
                self.api = API(auth)
                self.auth = auth
        return self.api

    @commands.group(pass_context=True, no_pm=True, name='tweets')
    async def _tweets(self, ctx):
        """Gets information from Twitter's API"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_tweets.command(pass_context=True, no_pm=True, name='getuser')
    async def get_user(self, ctx, username: str):
        """Get info about the specified user"""
        message = ""
        if username is not None:
            api = self.authenticate()
            user = api.get_user(username)


            colour = int(random.choice(self.colours), 16)
            url = "https://twitter.com/" + user.screen_name
            emb = discord.Embed(colour=discord.Colour(value=colour),
                                url=url,
                                description=user.description,
                                timestamp=user.created_at)
            emb.set_footer(icon_url='https://cdn1.iconfinder.com/data/icons/iconza-circle-social/64/697029-twitter-512.png',text='Account created on')
            emb.set_author(icon_url=user.profile_image_url, name=user.screen_name)

            emb.add_field(name="Followers", value=user.followers_count)
            emb.add_field(name="Friends", value=user.friends_count)
            emb.add_field(name="Statuses", value=user.statuses_count)
            emb.add_field(name="Verified", value="Yes" if user.verified else "No")

            await self.bot.send_message(ctx.message.channel, embed=emb)
        else:
            message = "Uh oh, an error occurred somewhere!"
            await self.bot.say(message)

    @_tweets.command(pass_context=True, name="add")
    @checks.is_owner()
    async def _add(self, ctx, user_or_list_to_track: str):
        """Adds the twitter user to the list of followed twitter users.
        Provide a Twitter list (e.g. http://twitter.com/rokxx/lists/dota-2/members) to track multiple twitter users at once. Changes apply once the stream is restarted."""
        if user_or_list_to_track is None:
            await self.bot.say("I can't do that, silly!")
        else:
            isList = False

            api = self.authenticate()

            twitter_accounts = []
            pattern = 'twitter.[A-Za-z]+\/(?P<twittername>[A-Za-z]+)\/lists\/(?P<listname>[A-Za-z-0-9_]+)'
            m = re.search(pattern, user_or_list_to_track, re.I)
            if m != None:
                isList = True
                await self.bot.say("Received list. This may take a while.")
                for member in tw.Cursor(api.list_members, m.group('twittername'), m.group('listname')).items():
                    twitterID = member._json['id_str']
                    twitterName = member._json['name']
                    if twitterID not in twitter_accounts:
                        twitter_accounts.append({
                            "user_id": twitterID,
                            "user_name": twitterName
                        })
            else:
                for twt in tw.Cursor(api.user_timeline, id=user_or_list_to_track).items(1):
                    twitter_accounts.append({
                        "user_id": twt.user.id_str,
                        "user_name": twt.user.name
                    })

            for twitter_account in twitter_accounts:
                if ctx.message.server.id not in self.settings["servers"].keys():
                    self.settings["servers"][ctx.message.server.id] = {'channels': {}}
                if ctx.message.channel.id not in self.settings['servers'][ctx.message.server.id]['channels'].keys():
                    self.settings["servers"][ctx.message.server.id]['channels'][ctx.message.channel.id] = {'users': {}}
                if twitter_account['user_id'] not in \
                        self.settings["servers"][ctx.message.server.id]['channels'][ctx.message.channel.id]['users']:
                    self.settings["servers"][ctx.message.server.id]['channels'][ctx.message.channel.id]['users'][
                        twitter_account['user_id']] = twitter_account

                    dataIO.save_json(self.settings_file, self.settings)
                    if not isList:
                        await self.bot.say("Added %s to the twitter list!" % twitter_account['user_name'])
                else:
                    if not isList:
                        await self.bot.say("Twitter user %s is already added" % twitter_account['user_name'])
            if isList:
                await self.bot.say("Finished adding twitter users to list. Count: %s" %len(twitter_accounts))

    @_tweets.command(pass_context=True, name="remove")
    @checks.is_owner()
    async def _remove(self, ctx, user_to_remove: str):
        """Removes the twitter user from the list of followed twitter users.
        Write all after to remove the entire list."""
        if user_to_remove is None:
            await self.bot.say("You didn't specify a user to remove!")
        elif user_to_remove == "all":
            if ctx.message.server.id not in self.settings['servers']:
                await self.bot.say('This server does not follow any twitter users.')
            elif ctx.message.channel.id not in self.settings['servers'][ctx.message.server.id]['channels']:
                await self.bot.say('This text channel does not follow any twitter users.')
            else:
                self.settings["servers"][ctx.message.server.id]['channels'][ctx.message.channel.id]['users'] = {}
                dataIO.save_json(self.settings_file, self.settings)
                await self.bot.say("Cleared the tracking list!")
        else:
            api = self.authenticate()
            tweet = None
            for twt in tw.Cursor(api.user_timeline, id=user_to_remove).items(1):
                tweet = twt

            if ctx.message.server.id not in self.settings['servers']:
                await self.bot.say('This server does not follow any twitter users.')
            elif ctx.message.channel.id not in self.settings['servers'][ctx.message.server.id]['channels']:
                await self.bot.say('This text channel does not follow any twitter users.')
            elif tweet.user.id_str not in \
                    self.settings['servers'][ctx.message.server.id]['channels'][ctx.message.channel.id]['users']:
                await self.bot.say('Could not find twitter user')
            else:
                removed = self.settings["servers"][ctx.message.server.id]['channels'][ctx.message.channel.id][
                    "users"].pop(tweet.user.id_str)
                dataIO.save_json(self.settings_file, self.settings)
                await self.bot.say("Removed %s from list" % removed['user_name'])

    @_tweets.command(pass_context=True, no_pm=True, name='start')
    @checks.is_owner()
    async def start(self):
        """Owner only: Starts the twitter stream"""
        if self.twitterStreamActive:
            await self.bot.say("twitter stream already active")
        else:
            await self.bot.say("starting tweets")
            await self.user_loop()
            self.twitterStreamActive = True

    @_tweets.command(pass_context=True, no_pm=True, name='stop')
    @checks.is_owner()
    async def stop(self):
        """Owner only: Stops the twitter stream"""
        if self.twitterStreamActive:
            await self.bot.say("stopping tweets")
            self.l.interrupt = True
            self.twitterStreamActive = False
        else:
            await self.bot.say("can't stop, twitter stream not active")

    @commands.group(pass_context=True, name='tweetset')
    @checks.admin_or_permissions(manage_server=True)
    async def _tweetset(self, ctx):
        """Command for setting required access information for the API.
        To get this info, visit https://apps.twitter.com and create a new application.
        Once the application is created, click Keys and Access Tokens then find the
        button that says Create my access token and click that. Once that is done,
        use the subcommands of this command to set the access details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_tweetset.command(name='creds')
    @checks.is_owner()
    async def set_creds(self, consumer_key: str, consumer_secret: str, access_token: str, access_secret: str):
        """Sets the access credentials. See [p]help tweetset for instructions on getting these"""
        if consumer_key is not None:
            self.settings["consumer_key"] = consumer_key
            self.consumer_key = consumer_key
        else:
            await self.bot.say("No consumer key provided!")
            return
        if consumer_secret is not None:
            self.settings["consumer_secret"] = consumer_secret
            self.consumer_secret = consumer_secret
        else:
            await self.bot.say("No consumer secret provided!")
            return
        if access_token is not None:
            self.settings["access_token"] = access_token
            self.access_token = access_token
        else:
            await self.bot.say("No access token provided!")
            return
        if access_secret is not None:
            self.settings["access_secret"] = access_secret
            self.access_secret = access_secret
        else:
            await self.bot.say("No access secret provided!")
            return
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say('Set the access credentials!')
        self.api = self.authenticate()

    async def user_loop(self):

        await self.bot.wait_until_ready()
        await self.bot.on_ready()

        self.authenticate()

        #queue containing tweets
        q = Queue()
        self.l = TweetListener(api=self.api, interrupt=False, queue=q)      #queue is passed to TweetListener
        stream = tw.Stream(self.auth, self.l)                               #stream for streaming tweets

        #get all the twitter IDs
        userIDs = []
        for serverID in self.settings["servers"]:
            for channelID in self.settings['servers'][serverID]['channels']:
                for user in self.settings["servers"][serverID]['channels'][channelID]['users']:
                    if user not in userIDs: userIDs.append(user)

        #start stream.filter. Put it into a thread.
        tstream = threading.Thread(target=stream.filter, args=(), kwargs={'follow': userIDs})
        tstream.daemon = True
        tstream.start()

        self.twitterStreamActive = True

        while self.twitterStreamActive:
            await asyncio.sleep(1)
            while not q.empty():
                tweet = q.get()
                #todo: set level, retrieve the information from settings.json
                #todo: add a command for setting the level
                #stream.filter provide all tweets by default
                #1: all tweets (followed-user tweets and tweets replying to followed-user
                #2: only tweets from followed user
                #3: only tweets from followed user, not replying to someone else
                for serverID in self.settings["servers"]:
                    for channelID in self.settings['servers'][serverID]['channels'].keys():
                        channel = discord.utils.get(self.bot.get_all_channels(), id=channelID)
                        if channel != None:
                            #currently: only take tweets from followed user.
                            if tweet['user_id'] in self.settings["servers"][serverID]['channels'][channelID]['users']:


                                em = discord.Embed(url="https://twitter.com/" + tweet['screen_name'] + "/status/" + str(tweet['status_id']),
                                                   description=tweet['status'],
                                                   timestamp=tweet['created_at'],
                                                   colour=int(random.choice(self.colours), 16))

                                if tweet['media_url'] != '':
                                    em.set_image(url=tweet['media_url'])

                                em.set_author(icon_url=tweet['avatar_url'],name=tweet['screen_name']) #,url='http://google.com')
                                em.set_footer(icon_url='https://cdn1.iconfinder.com/data/icons/iconza-circle-social/64/697029-twitter-512.png',text='Tweet created on')

                                await self.bot.send_message(channel, embed=em)
                        #else:
                        #    print('%s does not exist' %channelID)

def check_folder():
    if not os.path.exists("data/tweets"):
        print("Creating data/tweets folder")
        os.makedirs("data/tweets")


def check_file():
    data = {'consumer_key': '', 'consumer_secret': '',
            'access_token': '', 'access_secret': '', 'servers': {}}
    f = "data/tweets/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    if not twInstalled:
        bot.pip_install("tweepy")
        import tweepy as tw
        from tweepy.api import API
        from tweepy.streaming import StreamListener
    n = Tweets(bot)

    bot.add_cog(n)

