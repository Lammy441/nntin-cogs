from discord.ext import commands
from discord import Embed, Colour
from datetime import datetime

from redbot.core import checks

class Announce:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_owner()
    async def announce(self, ctx):

        announce = """In this discord server you get the latest Twitter News.
The source code is public on [*Github*](https://github.com/NNTin/).

This server is home to ***Chirp***.

**Channel Description**

Use the most appropriate text channel!

<#295542451475578882>: Information for new users
<#295528852518731786>: Entrance area for newcomers
Reason for this server's existence:
* <#295529047385964555>
* <#296075216050716682>
* <#296229560981258241>
* <#296424769211858945>
* <#296424854939500544>
* <#296424966159728641>
<#295595536222781451>: Discuss about the bot
<#295603926500376576>: Talk about anything
<#295603956745502721>: My GitHub blog

**Server Rules**

:pushpin:  Please read each of these rules thoroughly.

* If you don't have a solid understanding of Python, use Google before asking questions. ([Help vampire ...](http://www.skidmore.edu/~pdwyer/e/eoc/help_vampire.htm))
* When asking for help, provide as much detail as possible. "it's broken" is not helpful.
* Read the README on GitHub before asking how to run the bot.
* Do not private message. There are more 👀 on the public channel.
* Use the appropriate text channels.
* Don't ask if you can ask."""

        embed = Embed(description=announce)
        embed.set_author(icon_url=ctx.author.avatar_url_as(), name=ctx.message.author.name)
        embed.set_footer(text="Meepo", icon_url='https://i.imgur.com/6LfN4cd.png')
        embed.set_thumbnail(url='https://i.imgur.com/6LfN4cd.png')
        embed.timestamp = datetime.utcnow()
        await ctx.send(content=None, embed=embed)

        embed = Embed(colour=Colour(value=0xffff00))
        embed.add_field(name="<:clockwerk:295657808622256139> Dota 2", value="[Rokxx](https://twitter.com/rokxx/lists/dota-2)", inline=True)
        embed.add_field(name="<:csgo:296082233251332096> CS:GO", value="[JacobNWolf](https://twitter.com/JacobNWolf/lists/)", inline=True)
        embed.add_field(name="<:blitzcrank:296239621543559178> LoL", value="[JacobNWolf](https://twitter.com/JacobNWolf/lists/)", inline=True)
        embed.add_field(name="<:overwatch:338636718410432512> Overwatch",value="[JacobNWolf](https://twitter.com/JacobNWolf/lists/overwatch)", inline=True)
        embed.add_field(name="<:cod:338636808244166656> CoD", value="[JacobNWolf](https://twitter.com/JacobNWolf/lists/)", inline=True)
        embed.add_field(name="<:ssmb:338636908030853150> SSMB", value="[JacobNWolf](https://twitter.com/JacobNWolf/lists/)", inline=True)
        embed.set_thumbnail(url='https://i.imgur.com/oZjPWSa.png')
        await ctx.send(content=None, embed=embed)

        embed = Embed(colour=Colour(value=0x00ffff))
        embed.add_field(name="Webhook Bot", value="[<:github:303455670101868555> Github:](https://github.com/NNTin/discord-twitter-bot) functions purely through webhook (stable, recommended)", inline=True)
        embed.add_field(name="Red-DiscordBot: nntin-cogs/tweets", value="[<:github:303455670101868555> Github:](https://github.com/NNTin/nntin-cogs) re-implemented as a cog (unstable, no support)", inline=True)
        embed.set_thumbnail(url='https://i.imgur.com/LVTy0FY.png')
        await ctx.send(content=None, embed=embed)

        embed = Embed(color=Colour(value=0x00ff00), title='Invite URL', description='coming soon™ (Valve Time™)')
        embed.set_author(icon_url=self.bot.user.avatar_url_as(), name=self.bot.user.name)
        embed.set_image(url='https://i.imgur.com/6LfN4cd.png')
        await ctx.send(content=None, embed=embed)