import random
from datetime import datetime
try:
    from .helper import ExtendedFormatter
except ModuleNotFoundError:
    from helper import ExtendedFormatter

# todo: in the far future:
# todo: implement different pet types. You can earn more points with pets that
# todo: grow slower, eat more, poop more. In general requires more attention
# todo: and more time commitment.
# todo: points can be used to unlock pet types. Some guilds may use the points to unlock roles.


class Pet:
    """The actual tamagotchi pet instance."""

    def __init__(self, member_group):
        self.d = member_group

        """
        1000 hunger lasts 48 hours. 1 hunger = 172.8 seconds
        1000 health lasts 16 hours. 1 health =  57.6 seconds

        However health only ticks down when there is poop.

        You can get a maximum of 1000 points per hour. 5 point is the maximum you can achieve per tick.
        1 point tick = 18.0 seconds

        These are not actual ticks. Time progresses when you interact with the bot. And those time
        progression only applies to your Tamagotchi. It's more correct to say that these are your
        conversion factors. I named them tick since it's easier for me to imagine.
        """
        self.HUNGER_TICK = 172.8
        self.HEALTH_TICK = 57.6
        self.POINT_TICK = 18.0
        self.POOP_TICK = random.randint(28800, 36000)
        self.ADULT_WHEN = 12096000

        self.adult = True if datetime.utcnow().timestamp() - self.d["tama"]["birthdate"] > self.ADULT_WHEN else False
        self.f = ExtendedFormatter()

        # seed determines the gender of your pet, extend it in future
        self.seed = member_group["owner_id"] + len(member_group["dead_tamagotchis"]) + len(
            member_group["retired_tamagotchis"]) + len(member_group["abandoned_tamagotchis"])
        random.seed(self.seed + 2)

        self.gender = random.randint(0, 2)

    def get_next_event(self) -> float:
        """
        Calculate the next event based on health and hunger.
        Hunger events are fired at: 500, 300, 100, 0
        Health events are fired at: 800, 500, 300, 0
        """
        hunger = self.d["tama"]["hunger"]
        health = self.d["tama"]["health"]
        hunger_event = hunger - (500 if hunger > 500 else
                                 (300 if hunger > 300 else
                                  (100 if hunger > 100 else 0)))
        health_event = health - (800 if health > 800 else
                                 (500 if health > 500 else
                                  (300 if health > 300 else 0)))
        hunger_event *= self.HUNGER_TICK
        if self.d["tama"]["clean_poop"]:
            health_event *= self.HEALTH_TICK
        else:
            health_event = 172800
        return self.d["tama"]["timestamp"] + min(hunger_event, health_event)

    def get_next_poop_event(self) -> float:
        return datetime.utcnow().timestamp() + self.POOP_TICK

    def get_next_random_event(self) -> float:
        raise NotImplementedError("get_next_random_event() is not implemented.")

    def pet_at_home(self) -> bool:
        """
        You can only interact if your pet is at home. Your pet might leave its home under certain circumstances for
        example if you don't clean its litter box for an extended period it will wander off until it is cleaned.
        """
        return True if self.get_health() < 0 else False

    if True:
        """
        The pet stats is calculated based on the past timestamp, current timestamp and past stats
        """
        def get_update(self) -> dict:
            self.d["tama"]["happiness"] = self.get_happiness()
            self.d["tama"]["health"] = self.get_health()
            self.d["tama"]["hunter"] = self.get_hunger()

            if self.d["tama"]["hunger"] < 0:
                self.d["dead_tamagotchis"].append(self.d.pop("tama"))
            return self.d

        def get_health(self) -> float:
            if not self.d["tama"]["clean_poop"]:     # full health when litter box is cleaned
                return 1000
            else:
                past_seconds = datetime.utcnow().timestamp() \
                               - datetime.utcfromtimestamp(self.d["tama"]["timestamp"]).timestamp()
                past_health_ticks = past_seconds / self.HEALTH_TICK
                assert self.d["tama"]["health"] - past_health_ticks <= 1000, "Health > 1000. Not possible."
                return self.d["tama"]["health"] - past_health_ticks

        def get_hunger(self) -> float:
            past_seconds = datetime.utcnow().timestamp() \
                           - datetime.utcfromtimestamp(self.d["tama"]["timestamp"]).timestamp()
            past_hunger_ticks = past_seconds / self.HUNGER_TICK
            assert self.d["tama"]["hunger"] - past_hunger_ticks <= 1000, "Hunger > 1000. Not possible."
            return self.d["tama"]["hunger"] - past_hunger_ticks

        def get_happiness(self) -> float:
            average_health = (self.d["tama"]["health"] + self.get_health()) / 2
            average_hunger = (self.d["tama"]["hunger"] + self.get_hunger()) / 2
            happiness = (average_health + average_hunger) / 2
            assert happiness <= 1000, "Happiness > 100. Not possible."
            return happiness

        def get_points(self) -> float:
            happiness = self.d["tama"]["happiness"]
            point_mult = (5.0 if happiness > 900 else
                          (4.5 if happiness > 800 else
                           (4.0 if happiness > 700 else
                            (3.0 if happiness > 600 else
                             (1.0 if happiness > 500 else 0.1)))))
            if self.adult:
                point_mult /= 5

            past_seconds = datetime.utcnow().timestamp() - datetime.utcfromtimestamp(
                self.d["tama"]["timestamp"]).timestamp()
            past_point_ticks = past_seconds / self.POINT_TICK
            return self.d["tama"]["points"] + (past_point_ticks * point_mult)

    if True:
        """
        Anything string related goes here.
        """
        def cformat(self, _template):
            if self.gender == 0:
                s = "he"
                o = "him"
                a = "his"
                p = "his"
            elif self.gender == 1:
                s = "she"
                o = "her"
                a = "her"
                p = "hers"
            else:
                s = "it"
                o = "it"
                a = "its"
                p = "its"
            if isinstance(_template, str):
                return self.f.format(_template, s=s, o=o, a=a, p=p, name=self.d["tama"]["name"])
            elif isinstance(_template, list):
                return [self.cformat(element) for element in _template]
            elif isinstance(_template, dict):
                return {key: self.cformat(value) for key, value in _template.items()}
            else:
                raise NotImplementedError

        def help_text(self):
            """Take good care of your Tamagotchi

            Your Tamagotchi's happiness increases when it's healthy and not hungry. The happier your Tamagotchi is the
            more points you will earn.
            You can still your pet's hunger by feeding it. Be careful. Your pet can die if you don't feed it for 2
            entire days. Occasionally your pet will poop. If you don't clean its litter box its health will decrease.
            Although your pet can't die to low health point generation will be slowed down.

            Once you've given your pet enough care he will become an adult. Adult pets cannot die since they've
            developed the skill of hunting their own prey. You can still interact with them. You can also retire them
            by releasing them into the wild. If you ignore your pet he will instead abandon you. Adult pets generate
            points at a much slower rate but they also require minimal care.

            You can only have one active pet at any given time.

            Points can be spent to unlock different pet types. Some require less attention and reach adulthood faster.
            The general twist however is the longer a pet takes to develop and the more attention it needs the more
            points you are going to earn. Some guilds may allow you to unlock roles with those points.
            """
            raise NotImplementedError

        def hatch_fail(self):
            if self.adult:
                res = {
                    "name": "Try another day.",
                    "value": "It was already hard taking care of {name!c}. It would be irresponsible to get "
                             "another pet. However {name!c} has grown up a lot and knows how to survive on {a} "
                             "own. You can release {o} into the wild. Don't worry. {s!c} won't be gone."
                }
            else:
                res = {
                    "name": "Try another day.",
                    "value": "The farm is out of eggs. {name!c} looks at you with watery eyes. You have "
                             "a feeling {s}'s disappointed. Is {s} not good enough?"
                }
            return self.cformat(res)

        def hatch_success(self):
            res = list()
            res.append({
                "name": "It's your lucky day!",
                "value": "A tamagotchi just hatched from {a} egg. {s!c} looks around and starts "
                         "following you. Oh no... {s!c} thinks you are {a} mother."
            })
            res.append({
                "name": "What now?",
                "value": "You can take care of {o} or abandon {o}. Either way {s} will follow you around.\n"
                         "Write `[p]tama` to see what else you can do. You decide to name {o} **{name!u}**."
            })
            return self.cformat(res)

        def hunger_health_event(self):
            res = list()
            happiness = self.get_happiness()
            if happiness > 700:
                res.append(random.choice([
                    {
                        "name": "{name!c} wants something",
                        "value": "{s!c}'s calling you."
                    },
                    {
                        "name": "You have an uneasy feeling...",
                        "value": "... that you are missing something. Whatever. It can't be that bad."
                    }
                ]))
            else:
                res.append(random.choice([
                    {
                        "name": "Did you forget someone?",
                        "value": "It's been quite some time since you looked after {name!c}."
                    },
                    {
                        "name": "You got bitten",
                        "value": "You turn around and see it's your pet. What does {s} want?"
                    }
                ]))

            # 500 300 100 0
            hunger = self.get_hunger()
            if hunger > 800:
                t = "{name!c} is not hungry."
            elif hunger > 400:
                t = "Your tamagotchi {name!c} seems to be hungry. Maybe you should feed {o}."
            elif hunger > 200:
                t = "You should feed {name!c}. {s}'s been starving for quite some time."
            elif hunger > 50:
                t = "{name!c} is about to starve to death."
            else:
                t = "{name!c} starved to death."
            res.append({
                "name": "Hunger",
                "value": t
            })

            # 800 500 300 0
            health = self.get_health()
            if health == 1000:
                t = "The litter box is clean."
            elif health > 650:
                t = "What is this smell..."
            elif health > 400:
                t = "That turd pooped again. Maybe I should clean {a} litter box."
            elif health > 150:
                t = "Flies are flying around the litter box."
            else:
                t = "{name!c} has wandered off. {s!c} has no interest living in a filthy home. Maybe {s} " \
                    "will come back when you clean {a} litter box."
            res.append({
                "name": "Health",
                "value": t
            })
            return self.cformat(res)


if __name__ == '__main__':
    info = {
        "dead_tamagotchis": [],
        "retired_tamagotchis": [],
        "abandoned_tamagotchis": [],
        "tama": {
            "name": "Linley",
            "points": 0,
            "birthdate": 1546277253.084279,
            "timestamp": 1546277253.084279,
            "happiness": 954,
            "health": 921,
            "hunger": 975,
            "adult_event": None,
            "random_event": None,
            "event": 1546359333.084279,
            "poop_event": 1546312653.084342,
            "clean_poop": None
        },
        "owner_id": 77488778255540224,
        "points": 0
    }
    pet = Pet(member_group=info)

    print(pet.hatch_success())


