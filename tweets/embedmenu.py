import discord
from random import choice

class EmbedMenu():
    def __init__(self, bot):
        self.bot = bot
        self.emojis = {
            "back": "⬅",
            "exit": "❌",
            "next": "➡"
        }

    async def _embed_menu(self, ctx, field_list: list,
                          message: discord.Message = None,
                          embed: discord.Embed = None,
                          start_at=0, timeout: int=15,
                          fieldamount: int=24):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py and
           https://github.com/palmtree5/palmtree5-cogs/blob/master/tweets/tweets.py"""

        # An embed can only show 25 fields
        # fieldamount default 24 because perfect 2/3 columns
        if fieldamount > 25: fieldamount = 25

        fields = field_list[start_at:start_at+fieldamount]

        if not embed:
            colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
            colour = int(colour, 16)
            em = discord.Embed(colour=discord.Colour(value=colour))
        else:
            em = embed

        em.set_footer(text='Showing results {} to {} of {}'
                      .format(start_at+1,
                              start_at+fieldamount if start_at+fieldamount <= len(field_list) else len(field_list),
                              len(field_list)),
                      icon_url='https://i.imgur.com/6LfN4cd.png')

        for field in fields:
            em.add_field(name=field['name'], value=field['value'], inline=field['inline'])

        if not message:
            message = await ctx.send(embed=em)
            for emoji in self.emojis:
                await message.add_reaction(str(self.emojis[emoji]))
        else:
            await message.edit(embed=em)

        def check_react(r, u):
            return u == ctx.author and r.emoji in list(self.emojis.values())

        try:
            react, user = await self.bot.wait_for(
                "reaction_add", check=check_react, timeout=timeout
            )
        except:
            return await message.delete()


        if react is None:
            await message.remove_reaction("⬅", ctx.guild.me)
            await message.remove_reaction("❌", ctx.guild.me)
            await message.remove_reaction("➡", ctx.guild.me)
            return None

        reacts = {v: k for k, v in self.emojis.items()}
        react = reacts[react.emoji]

        em.clear_fields()

        if react == "next":
            next_start_at = 0
            if start_at >= len(field_list) - fieldamount:
                next_start_at = 0  # Overflow to the first item
            else:
                next_start_at = start_at + fieldamount
            return await self.embed_menu(ctx, field_list, message=message, embed=embed,
                                         start_at=next_start_at, timeout=timeout)
        elif react == "back":
            next_start_at = 0
            if start_at == 0:
                next_start_at = len(field_list) - fieldamount  # Loop around to the last item
            elif start_at < fieldamount:
                next_start_at = 0
            else:
                next_start_at = start_at - fieldamount
            return await self.embed_menu(ctx, field_list, message=message, embed=embed,
                                         start_at=next_start_at, timeout=timeout)
        else:
            return await message.delete()

    async def embed_menu(self, *args, **kwargs):
        #try:
        await self._embed_menu(*args, **kwargs)
        #except:
        #    print('Error in embed menu')