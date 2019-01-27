from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.commands import Context
from datetime import datetime
from .api import Reddit as RedditLogin
from .helper import Embed
import asyncio


class Reddit(commands.Cog):
    """
    Display the front page (of a subreddit) in a text channel.
    """

    default_global = {
        "refresh_rate": 5,  # in seconds, gets the data off reddit every x seconds and updates the message
        "future": 0,        # time in future
        "reddit": {         # required for Reddit API authentication
            "client_id": "",
            "client_secret": "",
            "username": "",
            "password": "",
            "user_agent": "discord front page visualizer v0.0.1"
        }
    }

    default_channel = {
        "is_active": False,
        "message": {
            "id": None,                   # discord message ID that is being repeatedly edited
            "subreddit": None,            # the subreddit that is being displayed, + separate multiple
            "show_stickied": True,        # whether stickied submissions should be displayed
            "show_pinned": True,          # whether pinned   submissions should be displayed
            "show_spoiler": True,         # whether spoiler  submissions should be displayed
            "reversed": False,            # reverse the order in which the submissions are displayed
            "amount": 10,                 # amount of submissions being displayed
            "display_timestamp": True,    # whether the bot should update the timestamp (bot is alive indicator)
        },
        "embed": {
            "author": {
                "name": "{display_name_prefixed} front page",
                "url": "https://old.reddit.com/{display_name_prefixed}",
                "icon_url": "{header_img}"
            },
            "title": "",
            "description": "{subscribers} Dota Auto Chess Players\n{accounts_active} days until Mars",
            "color": "{key_color}",
            "url": "",
            "fields": [],
            "image": {
                "url": "{banner_img}"
            },
            "thumbnail": {
                "url": "{header_img}"
            },
            "footer": {
                "text": "last refresh time",
                "icon_url": "{header_img}"
            }
        },
        "field": {
            "inline": False,
            "name": "<:upvote:539091866797342720>{score} /u/{author} {gilded!g}",
            "value": "[{title}]({url})\n*{created_ago} ago* {spoiler!x} {over_18!n}"
        }
    }
    conf_id = 800858686

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.running = True
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_channel(**self.default_channel)
        self.config.register_global(**self.default_global)
        self.r = None
        self.bot.loop.create_task(self._login())

    def __unload(self):
        self.running = False

    async def _login(self):
        async with self.config.reddit() as reddit_creds:
            self.r = RedditLogin(**reddit_creds)

        self.bot.loop.create_task(self._check())

    async def _check(self):
        while self.running:
            await self._check_future()
            await asyncio.sleep(1)

    async def _check_future(self):
        future = await self.config.future()
        now = datetime.utcnow().timestamp()
        if future < now:
            await self.config.future.set(now + await self.config.refresh_rate())
            await self._update()

    async def _update(self):
        channel_configs = (await self.config.all_channels())

        for channel_id in channel_configs.keys():
            channel_group = channel_configs[channel_id]

            if not channel_group["is_active"]:
                print("skipping")
                continue
            channel = self.bot.get_channel(channel_id)
            message = await channel.get_message(channel_group["message"]["id"])

            embed = Embed.create_embed(
                _data=channel_group["embed"],
                **self.r.get_info(channel_group["message"]["subreddit"])
            )
            for submission in self.r.get_hot_submissions(
                    subreddit=channel_group["message"]["subreddit"],
                    amount=channel_group["message"]["amount"]):
                embed.add_field(
                    **channel_group["field"],
                    **submission
                )
            embed = Embed.from_data(embed.to_dict())
            embed.timestamp = datetime.utcnow()
            await message.edit(embed=embed, content="")

    @commands.group()
    async def reddit(self, ctx):
        """
        Display the front page (of a subreddit) in a text channel.
        """
        pass

    @reddit.command()
    async def set(self, ctx: Context, message_id: int, subreddit: str):
        """
        configure your shit
        """
        async with self.config.channel(ctx.channel)() as channel_group:
            channel_group["message"]["id"] = message_id
            channel_group["message"]["subreddit"] = subreddit
            channel_group["is_active"] = True
            pass
