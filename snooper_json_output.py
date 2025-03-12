"""
This module is used to output the snooper results in JSON format.

Usage:
    python snooper_json_output.py [TARGET_REDDIT_SCREENNAME] [--username REDDIT_USERNAME] [--password REDDIT_PASSWORD] [--client_id REDDIT_CLIENT_ID] [--secret REDDIT_SECRET] [--output OUTPUT_JSON_FILE_PATH]

Options:
    -h --help                       Show this help message and exit.
    --username REDDIT_USERNAME      Required. Your Reddit username.
    --password REDDIT_PASSWORD      Required. Your Reddit password.
    --client_id REDDIT_CLIENT_ID    Required. Your Reddit client id.
    --secret REDDIT_SECRET          Required. Your Reddit secret.
    --output OUTPUT_JSON_FILE_PATH  Output JSON file path.
"""
import argparse
import collections
from curses import mouseinterval
import datetime
import json
import pathlib
import re
import sys
from typing import Any 

import langdetect
import praw


def driver_login(username: str, password: str, client_id: str, secret: str) -> praw.Reddit:
    client = praw.Reddit(
        username=username,
        password=password,
        client_id=client_id,
        client_secret=secret,
        user_agent="snooper json output v1.0"
    )
    return client


def get_day(item: Any) -> int:
    time = item.created
    return datetime.datetime.fromtimestamp(time).weekday()


def int_to_day(day: int) -> str:
    test = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
    return test[day]


def analyze_by_day(data: list) -> dict:
    dataset = {'Sunday': 0, 'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0}
    for item in data:
        dataset[int_to_day(get_day(item))] += 1

    return dataset


def analyze_by_hour(data: list) -> dict:
    dataset = {
        '00:00':0, '01:00':0, '02:00':0, '03:00':0, '04:00':0, '05:00':0, '06:00':0, '07:00':0, '08:00':0,
        '09:00':0, '10:00':0, '11:00':0, '12:00':0, '13:00':0, '14:00':0, '15:00':0, '16:00':0, '17:00':0,
        '18:00':0, '19:00':0, '20:00':0, '21:00':0, '22:00':0, '23:00':0
    }
    
    for item in data:
        time = item.created
        dataset[str(datetime.datetime.fromtimestamp(time))[11:13] + ":00"] += 1
        
    return dataset


def main():
    parser = argparse.ArgumentParser(
        description="Output the snooper results in JSON format.",
        usage="python snooper_json_output.py [TARGET_REDDIT_SCREENNAME] [--username REDDIT_USERNAME] [--password REDDIT_PASSWORD] [--client_id REDDIT_CLIENT_ID] [--secret REDDIT_SECRET] [--output OUTPUT_JSON_FILE_PATH]"
    )
    parser.add_argument(
        "raddit_screen_name",
        help="The target Reddit screen name."
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Your Reddit username."
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Your Reddit password."
    )
    parser.add_argument(
        "--client_id",
        required=True,
        help="Your Reddit client id."
    )
    parser.add_argument(
        "--secret",
        required=True,
        help="Your Reddit secret."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Limit the number of posts to retrieve (default=1000)."
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path."
    )
    args = parser.parse_args()
    target_raddit_screen_name = args.raddit_screen_name
    username = args.username
    password = args.password
    client_id = args.client_id
    secret = args.secret
    output = args.output
    
    total_data = []
    verbose_out = []
    
    driver = driver_login(username, password, client_id, secret)
    target_user = driver.redditor(target_raddit_screen_name)
    
    posts = target_user.submissions.new(limit=args.limit)
    comments = target_user.comments.new(limit=args.limit)
    
    total_data = list(posts) + list(comments)
    verbose_out = total_data
    
    link_karma = target_user.link_karma
    comment_karma = target_user.comment_karma
    total_karma = link_karma + comment_karma
    
    top_use_language = langdetect.detect(str(target_user.comments.top(limit=1)))
    
    account_created = datetime.datetime.fromtimestamp(target_user.created_utc).replace(tzinfo=datetime.timezone.utc).isoformat()
    
    analyze_result_by_hour = analyze_by_hour(total_data)
    analyze_result_by_day = analyze_by_day(total_data)
    
    json_result = {
        "account_created": account_created,
        "link_karma": link_karma,
        "comment_karma": comment_karma,
        "total_karma": total_karma,
        "top_use_language": top_use_language,
        "analyze_result_by_hour": analyze_result_by_hour,
        "analyze_result_by_day": analyze_result_by_day,
        "total_data_count": len(total_data),
        "metadata": {
            "target_screen_name": target_raddit_screen_name,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "limit": args.limit,
        }
    }
    
    # Output the result
    if output:
        with open(output, "w") as f:
            json.dump(json_result, f, indent=4, ensure_ascii=False)
        print(f"{pathlib.Path(output).resolve()}")
    else:
        print(json.dumps(json_result, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
