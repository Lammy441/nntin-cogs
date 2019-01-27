import praw
import datetime
import json
import random


class Reddit:
    submission_keys = [
        "subreddit", "selftext", "url", "gilded", "title", "domain", "link_flair_text", "score", "thumbnail", "edited",
        "created", "created_utc", "is_self", "pinned", "stickied", "distinguished", "spoiler", "permalink", "author",
        "over_18", "spoiler"
    ]  # created_ago, edited_ago

    subreddit_keys = [
        "subscribers", "accounts_active", "display_name_prefixed", "banner_img", "banner_background_image", "header_img",
        "icon_img", "primary_color", "banner_background_color", "key_color"
    ]

    def __init__(self, **kwargs):
        self.r = praw.Reddit(**kwargs)

    def get_hot_submissions(self, subreddit, show_stickied=True, show_spoiler=True, show_pinned=True, amount=10):
        submissions = self.r.subreddit(subreddit).hot()
        counter = 0
        for submission in submissions:
            if (not show_pinned and submission.pinned) or \
                    (not show_spoiler and submission.spoiler) or \
                    (not show_stickied and submission.stickied):
                continue

            counter += 1
            if counter > amount:
                break

            current = datetime.datetime.utcnow().timestamp()
            res = {k: v for k, v in submission.__dict__.items() if k in self.submission_keys}

            res["created_ago"] = "{:0>8}".format(str(datetime.timedelta(seconds=int(current - res["created_utc"]))))

            if res["edited"]:
                res["edited_utc"] = res["edited"] + res["created_utc"] - res["created"]
                res["edited_ago"] = "{:0>8}".format(str(datetime.timedelta(seconds=int(current - res["edited_utc"]))))
            else:
                res["edited_ago"] = False
                res["edited_utc"] = False
            yield res

    def get_info(self, subreddit):
        sub = self.r.subreddit(subreddit)
        res = {k: getattr(sub, k) for k in self.subreddit_keys}

        for k, v in res.items():
            if "_color" in k:
                try:
                    res[k] = int(v[1:], 16)
                except ValueError:
                    res[k] = random.randint(0, 16777215)
        return res
