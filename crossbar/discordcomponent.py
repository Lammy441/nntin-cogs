from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp import auth
from redbot.core.bot import Red


class DiscordComponent(ApplicationSession):
    def __init__(self, bot: Red, component_config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.config = component_config
        print(component_config)
        print(self.bot.guilds)

    def onConnect(self):
        self.join(self.config["realm"], ["wampcra"], self.config["user"])

    def onChallenge(self, challenge):
        assert challenge.method == "wampcra", "don't know how to handle authmethod {}".format(challenge.method)

        signature = auth.compute_wcs(self.config["secret"].encode("utf8"), challenge.extra["challenge"].encode("utf8"))
        return signature.decode("ascii")

    def onJoin(self, details):
        print("hello darkness")


if __name__ == '__main__':
    runner = ApplicationRunner(url="ws://crosku.herokuapp.com/ws", realm="realm1")
    runner.run(DiscordComponent)
