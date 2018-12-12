from autobahn.asyncio.wamp import ApplicationRunner,ApplicationSession
import json

topics = ["ON_MESSAGE", "ON_TYPING", "ON_REACTION_ADD", "ON_MEMBER_JOIN", "ON_MEMBER_REMOVE",
          "ON_MEMBER_UPDATE", "ON_VOICE_STATE_UPDATE"]


class Component(ApplicationSession):
    async def onJoin(self, details):
        def on_event(payload):
            print("Got event: {}".format(json.dumps(json.loads(payload))))

        for topic in topics:
            await self.subscribe(on_event, "nntin.github.io.discord." + topic)


if __name__ == '__main__':
    url = "ws://crosku.herokuapp.com/ws"
    realm = "realm1"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)

