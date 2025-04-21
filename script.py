import praw
import os
import time
import random
import re

REFRESH_FILE = 'refresh_token.txt'
REPLIED_FILE = 'replied.txt'

refresh_token = None
if os.path.exists(REFRESH_FILE):
    with open(REFRESH_FILE, 'r') as f:
        refresh_token = f.read().strip()

reddit = praw.Reddit(
    client_id='client id',
    client_secret='client secret',
    user_agent='Human Rank v1.2.2 by QuardanterGaming,
    redirect_uri='localhost:8080',
    refresh_token=refresh_token
)

keyword_pattern = re.compile(r"(good human|bad human)", re.IGNORECASE)
already_replied = set()

if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE, 'r') as f:
        already_replied = set(line.strip() for line in f)

max_comments_per_hour = 8
comments_replied_today = 0
start_time = time.time()

def get_random_delay(min_delay=25, max_delay=60):
    return random.randint(min_delay, max_delay)

def check_rate_limit():
    global start_time, comments_replied_today
    elapsed = time.time() - start_time
    if elapsed > 3600:
        comments_replied_today = 0
        start_time = time.time()
    if comments_replied_today >= max_comments_per_hour:
        wait = 3600 - elapsed
        time.sleep(wait)
        comments_replied_today = 0

reply_templates = [
    "Thanks {user}, your vote has been recorded!",
    "Got it, {user}. Vote logged.",
    "Appreciate the input, {user}!",
    "Vote received loud and clear, {user}. Thanks!",
    "{user}, your feedback helps a lot. Cheers!"
]

subreddit = reddit.subreddit("SUBREDDIT_NAME")

for comment in subreddit.stream.comments(skip_existing=True):
    try:
        check_rate_limit()
        if comment.id in already_replied:
            continue
        if keyword_pattern.search(comment.body):
            username = str(comment.author)
            reply_text = random.choice(reply_templates).format(user=username)
            comment.reply(reply_text)
            already_replied.add(comment.id)
            comments_replied_today += 1
            with open(REPLIED_FILE, 'a') as f:
                f.write(f"{comment.id}\n")
            time.sleep(get_random_delay())
    except praw.exceptions.APIException:
        time.sleep(60)
    except Exception:
        time.sleep(10)