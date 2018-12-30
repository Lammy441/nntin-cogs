import random
from string import Formatter
from datetime import datetime

class ExtendedFormatter(Formatter):
    """An extended format string formatter

    Formatter with extended conversion symbol"""
    def convert_field(self, value, conversion):
        # do any conversion on the resulting object
        if conversion == 'u':
            return value.upper()
        elif conversion == 'l':
            return value.lower()
        elif conversion == 'c':
            return value.capitalize()
        else:
            return super(ExtendedFormatter, self).convert_field(value, conversion)


class Pet:
    """The actual tamagotchi pet instance."""
    def __init__(self, info, seed: int):
        # for now determines the gender of your pet
        self.seed = seed + len(info["dead_tamagotchis"])
        random.seed(seed)

        self.name = info["tama_name"]
        self.points = info["tama_points"]
        self.birthdate = info["tama_birthdate"]
        self.timestamp = info["tama_timestamp"]
        self.happiness = info["tama_happiness"]
        self.health = info["tama_health"]
        self.hunger = info["tama_hunger"]
        self.next_random_event = info["tama_next_random_event"]
        self.next_event = info["tama_next_event"]
        self.owner_id = str(info["owner_id"])

        gen = random.randint(0, 2)
        if gen == 0:
            self.s = "he"
            self.o = "him"
            self.a = "his"
            self.p = "his"
        elif gen == 1:
            self.s = "she"
            self.o = "her"
            self.a = "her"
            self.p = "hers"
        elif gen == 2:
            self.s = "it"
            self.o = "it"
            self.a = "its"
            self.p = "its"

    def get_next_event(self):
        """
        Calculate the next event based on health, hunger and happiness.
        """
        return 1561

    if True:
        """
        Anything string related goes here.
        """
        def cformat(self, template_str):
            f = ExtendedFormatter()
            output = f.format(template_str, s=self.s, o=self.o, a=self.a, p=self.p, name=self.name)
            return output

        def hatch_fail(self):
            t = "The farm is out of eggs. {name!c} looks at you with watery eyes. You have " \
                "a feeling {s}'s disappointed. Is {s} not good enough?"
            return self.cformat(t)

        def hatch_success_1(self):
            t = "A tamagotchi just hatched from its egg. {s!c} looks around and starts " \
                "following you. Oh no... {s!c} thinks you are {a} mother."
            return self.cformat(t)

        def hatch_success_2(self):
            t = "You can take care of {o} or abandon {o}. Either way {s} will follow you around.\n" \
                "Write `[p]tama` to see what else you can do. You decide to name {o} **{name!u}**."
            return self.cformat(t)


if __name__ == '__main__':
    info = {
        "dead_tamagotchis": [],
        "tama_name": "fhdksj",
        "tama_points": 0,
        "tama_birthdate": 1546177882.234719,
        "tama_timestamp": 1546177882.234719,
        "tama_happiness": 1000,
        "tama_health": 923,
        "tama_hunger": 951,
        "tama_next_random_event": 1546206861.234719,
        "tama_next_event": 1546213286.234719,
        "owner_id": 4564654
    }
    p = Pet(info=info, seed=7)
    print(p.hatch_success_2())

    print(datetime.utcnow().timestamp())
