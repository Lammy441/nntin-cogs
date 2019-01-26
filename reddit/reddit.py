from discord import Member, Role, Status, Embed, Message
from redbot.core import Config, commands
from redbot.core import checks
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify
from redbot.core.commands import Context
from datetime import datetime


# todo: convert color from "#00ff00" to int.


class Reddit(commands.Cog):
    """
    Display the front page (of a subreddit) in a text channel.
    """

    default_global = {
        "refresh_rate": 7,  # in seconds, gets the data off reddit every x seconds and updates the message
        "future": 0,        # time in future
        "reddit": {         # required for Reddit API authentication
            "client_id": None,
            "client_secret": None,
            "username": None,
            "password": None,
            "user_agent": None
        }
    }

    default_channel = {
        "is_active": False,               # before becoming active
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
            'author': {
                'name': '{display_name_prefixed} front page',
                'url': 'https://old.reddit.com/{display_name_prefixed}',
                'icon_url': '{header_img}'
            },
            'title': '',
            'description': '{subscribers} Dota Auto Chess Players\n'
                           '{accounts_active} days until Mars',
            'color': '{key_color}',       # careful, this has to be int!
            'timestamp': None,
            'type': 'rich',
            'url': '',
            'fields': [{
                'inline': False,
                'name': '[{score}] {author_name} submitted {ago} ({timestamp})',
                'value': '[{title}]({permalink})\n'
                         '{text}'
            }],
            'image': {
                'url': '{header_img}'
            },
            'thumbnail': {
                'url': '{banner_img}'
            },
            'footer': {
                'text': 'last refresh time',
                'icon_url': '{header_img}'
            }
        }
    }
    conf_id = 800858686

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, self.conf_id)
        self.config.register_channel(**self.default_channel)
        self.config.register_global(**self.default_global)

        self.format_global = {
            "subscribers": 9000,
            "accounts_active": 1337,
            "display_name_prefixed": "r/dota2",
            "banner_img": "https://b.thumbs.redditmedia.com/z2pliN1DfDEamcmJaDYbxvzJV8hUG1MhwQa03ejtpUk.png",
            "banner_background_image": "https://styles.redditmedia.com/t5_2s580/styles/bannerBackgroundImage_8z5pscm0f5l11.png",
            "header_img": "https://b.thumbs.redditmedia.com/F82n9T2HtoYxNmxbe1CL0RKxBdeUEw-HVyd-F-Lb91o.png",
            "icon_img": "https://a.thumbs.redditmedia.com/0bQOxAs6XMJhixOFLmta78SXPXaDxzp8jw915k7NLI4.png",
            "primary_color": "#349e48",
            "banner_background_color": "#251916",
            "key_color": "#ea0027"
        }
        self.format_submission = {
            "subreddit": "DotA2",
            "selftext": "Riftshadow Ruins Resident",
            "gilded": 3,
            "title": "RRR",
            "domain": "self.DotA2",
            "link_flair_text": "Fluff",
            "score": 9000,
            "thumbnail": "https://i.imgur.com/11zvdoc.png",
            "edited": "1548399888",
            "created": "154839465",
            "created_utc": "516161",
            "is_self": True,
            "pinned": False,
            "distinguished": False,
            "spoiler": False,
            "stickied": False,
            "permalink": "/r/DotA2",
            "author": "Meepo",
            "created_ago": "5 hours and 10 minutes",    # this has to be manually created
            "edited_ago":  "6 minutes"                  # this has to be manually created
        }



    @commands.group()
    async def reddit(self, ctx):
        """
        Display the front page (of a subreddit) in a text channel.
        """
        pass

    @reddit.command()
    async def set(self, ctx):
        """
        """
        async with self.config.channel(ctx.channel)() as channel_group:
            pass
