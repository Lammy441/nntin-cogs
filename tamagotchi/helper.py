from string import Formatter
from discord import Embed


class ExtendedFormatter(Formatter):
    """An extended format string formatter

    Formatter with extended conversion symbol"""
    def convert_field(self, value, conversion) -> str:
        # do any conversion on the resulting object
        if conversion == 'u':
            return value.upper()
        elif conversion == 'l':
            return value.lower()
        elif conversion == 'c':
            return value.capitalize()
        elif conversion == 'i':
            return str(int(value))
        else:
            return super(ExtendedFormatter, self).convert_field(value, conversion)


class ExtendedEmbed(Embed):
    """An extended discord.Embed class"""
    def populate_fields(self, _temp):
        if isinstance(_temp, dict):
            self.add_field(**_temp)
        elif isinstance(_temp, list):
            for element in _temp:
                self.populate_fields(element)
        else:
            raise NotImplementedError
