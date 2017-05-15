import os
import sys
import json
import time
import math
import numpy as np
import pandas as pd

from tweepy import Cursor
from twitter_client import get_twitter_client
from dotenv import load_dotenv, find_dotenv

MAX_FRIENDS = 15000

headers = [
    'id', 'name', 'screen_name', 'location', 'description', 'url',
    'followers_count', 'friends_count', 'listed_count', 'created_at',
    'favourites_count', 'profile_image_url', 'statuses_count'
]


def usage():
    print("Usage:")
    print("python {} <username>".format(sys.argv[0]))

def paginate(items, n):
    """Generate n-sized chunks from items"""
    for i in range(0, len(items), n):
        yield items[i:i + n]

def extract(screen_name):
    client = get_twitter_client()
    dirname = "outputs/users/{}".format(screen_name)
    max_pages = math.ceil(MAX_FRIENDS / 5000)
    print(screen_name)
    try:
        os.makedirs(dirname, mode=0o755, exist_ok=True)
    except OSError:
        print("Directory {} already exists".format(dirname))
    except Exception as e:
        print("Error while creating directory {}".format(dirname))
        print(e)
        sys.exit(1)
        
    # get followers for a given user
    followers_fname = "outputs/users/{}/followers.jsonl".format(screen_name)
    with open(followers_fname, 'w') as f:
        for followers in Cursor(client.followers_ids, screen_name=screen_name).pages(max_pages):
            for chunk in paginate(followers, 100):
                users = client.lookup_users(user_ids=chunk)
                for user in users:
                    f.write(json.dumps(user._json)+"\n")
            if len(followers) == 5000:
                print("More results available. Sleeping for 60 seconds to avoid rate limit")
                time.sleep(60)

    # get friends for a given user
    friends_fname = "outputs/users/{}/friends.jsonl".format(screen_name)
    with open(friends_fname, 'w') as f:
        for friends in Cursor(client.friends_ids, screen_name=screen_name).pages(max_pages):
            for chunk in paginate(friends, 100):
                users = client.lookup_users(user_ids=chunk)
                for user in users:
                    f.write(json.dumps(user._json)+"\n")
            if len(friends) == 5000:
                print("More results available. Sleeping for 60 seconds to avoid rate limit")
                time.sleep(60)

    # get user's profile
    user_profile_fname = "outputs/users/{}/user_profile.json".format(screen_name)
    with open(user_profile_fname, 'w') as f:
        profile = client.get_user(screen_name=screen_name)
        f.write(json.dumps(profile._json, indent=4))

def follower_stats(screen_name):
    followers_file = 'outputs/users/{}/followers.jsonl'.format(screen_name)
    friends_file = 'outputs/users/{}/friends.jsonl'.format(screen_name)
    with open(followers_file) as f1, open(friends_file) as f2:
        t0 = time.time()
        followers = []
        friends = []
        for line in f1:
            profile = json.loads(line)
            followers.append(profile['screen_name'])
        for line in f2:
            profile = json.loads(line)
            friends.append(profile['screen_name'])
        followers = np.array(followers)
        friends = np.array(friends)
        t1 = time.time()
        mutual_friends = np.intersect1d(friends, followers, assume_unique=True)
        followers_not_following = np.setdiff1d(followers, friends, assume_unique=True)
        friends_not_following = np.setdiff1d(friends, followers, assume_unique=True)
        t2 = time.time()
        print("----- Timing -----")
        print("Initialize data: {}".format(t1-t0))
        print("Set-based operations: {}".format(t2-t1))
        print("Total time: {}".format(t2-t0))
        print("----- Stats -----")
        print("{} has {} followers".format(screen_name, len(followers)))
        print("{} has {} friends".format(screen_name, len(friends)))
        print("{} has {} mutual friends".format(screen_name, len(mutual_friends)))
        print("{} friends are not following {} back".format(len(friends_not_following), screen_name))
        print("{} followers are not followed back by {}".format(len(followers_not_following), screen_name))
        return friends, followers


def generate_friends_df(screen_name):
    friends_file = 'outputs/users/{}/friends.jsonl'.format(screen_name)
    with open(friends_file) as f:
        t0 = time.time()
        data = []
        for ix, line in enumerate(f):
            profile = json.loads(line)
            friend = {}
#             print(profile)
            for key in headers:
                value = profile[key]
                if value == "":
                    value = 'NA'
                friend[key] = value
            friend['relationship'] = 'friend'
            friend['source'] = screen_name
            data.append(friend)
        return pd.DataFrame(data)
    
def generate_followers_df(screen_name):
    followers_file = 'outputs/users/{}/followers.jsonl'.format(screen_name)
    with open(followers_file) as f:
        t0 = time.time()
        data = []
        for ix, line in enumerate(f):
            profile = json.loads(line)
            follower = {}
            for key in headers:
                follower[key] = profile[key]
            follower['relationship'] = 'follower'
            follower['source'] = screen_name
            data.append(follower)
        return pd.DataFrame(data)



