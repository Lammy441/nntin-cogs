import praw
from datetime import datetime


class Reddit:
    submission_keys = [
        "subreddit", "selftext", "gilded", "title", "domain", "link_flair_text", "score", "thumbnail", "edited",
        "created", "created_utc", "is_self", "pinned", "stickied", "distinguished", "spoiler", "permalink", "author"
    ]  # created_ago, edited_ago

    subreddit_keys = [
        "subscribers", "accounts_active", "display_name_prefixed", "banner_img", "banner_background_image", "header_img",
        "icon_img", "primary_color", "banner_background_color", "key_color"
    ]

    def __init__(self, **kwargs):
        self.r = praw.Reddit(**kwargs)

    def get_hot_submissions(self, subreddit, show_stickied=False, show_spoiler=False, show_pinned=False, amount=10):
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

            current = datetime.utcnow().timestamp()
            res = {k: v for k, v in submission.__dict__.items() if k in self.submission_keys}
            res["created_ago"] = current - res["created_utc"]
            if res["edited"]:
                res["edited_ago"] = current - res["edited"] - res["created"] + res["created_utc"]
            else:
                res["edited_ago"] = res["edited"]

            yield res

    def get_info(self, subreddit):
        sub = self.r.subreddit(subreddit)
        return {k: getattr(sub, k) for k in self.subreddit_keys}


if __name__ == '__main__':
    reddit_creds = {
        "client_id": "x",
        "client_secret": "x",
        "username": "x",
        "password": "x",
        "user_agent": "x"
    }

    r = Reddit(**reddit_creds)
    for hot_submission in r.get_hot_submissions("dota2"):
        print(hot_submission)

    print(r.get_info("dota2"))
