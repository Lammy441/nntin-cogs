from discord import Embed as OEmbed
from string import Formatter


class ExtendedFormatter(Formatter):
    """An extended format string formatter

    Formatter with extended conversion symbol"""
    def convert_field(self, value, conversion) -> str:
        # s: str, r:repl, a:ascii, u:upper, l:lower, c:capitalize, i:int, g:gilded, x:spoiler, n:nsfw
        if conversion == 'u':
            return value.upper()
        elif conversion == 'l':
            return value.lower()
        elif conversion == 'c':
            return value.capitalize()
        elif conversion == 'i':
            return str(int(value))
        elif conversion == 'g':
            if value:
                return f'{value}*<:gold:539099071542198282>'
            else:
                return ''
        elif conversion == 'x':
            if value:
                return '**SPOILER**'
            else:
                return ''
        elif conversion == 'n':
            if value:
                return '**NSFW**'
            else:
                return ''
        else:
            return super(ExtendedFormatter, self).convert_field(value, conversion)


class Embed(OEmbed):
    f = ExtendedFormatter()

    def add_field(self, **kwargs):
        name = self.f.format(kwargs["name"], **kwargs)
        value = self.f.format(kwargs["value"], **kwargs)
        inline = kwargs["inline"]

        super().add_field(name=name, value=value, inline=inline)

    @classmethod
    def create_embed(cls, _data, **kwargs):
        self = cls.__new__(cls)
        data = self._populate(_data, **kwargs)
        data["color"] = int(data["color"])
        return Embed.from_data(data)

    def _populate(self, _data, **kwargs):
        data = {
            k: self.f.format(v, **kwargs)
            for k, v in _data.items()
            if isinstance(_data[k], str)
        }
        for k, v in _data.items():
            if isinstance(v, dict):
                data[k] = self._populate(v, **kwargs)
        return data


if __name__ == '__main__':
    f = ExtendedFormatter()

    template = "{a!g} hello"

    print(f.format(template, a=5))

