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
    def __init__(self, info):
        # for now determines the gender of your pet
        self.seed = info["owner_id"] + len(info["dead_tamagotchis"])
        random.seed(self.seed)

        self.name = info["tama_name"]
        self.points = info["tama_points"]
        self.birthdate = info["tama_birthdate"]
        self.timestamp = info["tama_timestamp"]
        self.happiness = info["tama_happiness"]
        self.health = info["tama_health"]
        self.hunger = info["tama_hunger"]
        self.next_random_event = info["tama_next_random_event"]
        self.next_event = info["tama_next_event"]
        self.next_poop = info["tama_next_poop"]
        self.clean_poop = info["tama_clean_poop"]
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
        Calculate the next event based on health and hunger.
        Hunger events are fired at: 500, 300, 100, 0
        Health events are fired at: 800, 500, 300, 0

        1000 hunger lasts 48 hours. 1 hunger = 172.8 seconds
        1000 health lasts 24 hours. 1 health =  86.4 seconds

        Health only ticks down when there is poop.
        """
        hunger_event = self.hunger - (500 if self.hunger > 500 else
                                      (300 if self.hunger > 300 else
                                       (100 if self.hunger > 100 else 0)))
        health_event = self.health - (800 if self.health > 800 else
                                      (500 if self.health > 500 else
                                       (300 if self.health > 300 else 0)))
        hunger_event *= 172.8      # todo: commented for testing reasons
        if self.clean_poop:
            health_event *= 86.4
        else:
            health_event = 172800
        return self.timestamp + min(hunger_event, health_event)

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

        def hunger_health_event(self):
            t = "It's been some time since you looked after {name!c}."
            return self.cformat(t)

        def hunger_event(self):
            # 500 300 100 0
            t = None
            if self.health > 400:
                t = "Your tamagotchi {name!c} seems to be hungry. Maybe you should feed {o}."
            elif self.health > 200:
                t = "You should feed {name!c}. {s}'s been starving for quite some time."
            elif self.health > 50:
                t = "{name!c} is about to starve to death."
            else:
                t = "{name!c} starved to death."
            return self.cformat(t)

        def health_event(self):
            # todo: write a bunch of different texts
            # 800 500 300 0
            t = "Your pet {name!c} is in top health (cleanliness)."
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
        "tama_next_poop": 1546213286.234719,
        "tama_clean_poop": False,
        "owner_id": 4564654
    }
    p = Pet(info=info)

    print(p.hunger_health_event())
