from tweepy import Stream
from tweepy.error import TweepError

STREAM_VERSION = '1.1'

class StreamAsync(Stream):
    def filter(self, follow=None, track=None, async=True, locations=None,
               stall_warnings=False, languages=None, encoding='utf8', filter_level=None):
        self.body = {}
        self.session.headers['Content-type'] = "application/x-www-form-urlencoded"
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/filter.json' % STREAM_VERSION
        if follow:
            self.body['follow'] = u','.join(follow).encode(encoding)
        if track:
            self.body['track'] = u','.join(track).encode(encoding)
        if locations and len(locations) > 0:
            if len(locations) % 4 != 0:
                raise TweepError("Wrong number of locations points, "
                                 "it has to be a multiple of 4")
            self.body['locations'] = u','.join(['%.4f' % l for l in locations])
        self.session.params = {'delimited': 'length'}
        self.host = 'stream.twitter.com'
        self._start(async)