import random

from DB import client
from Auth import db, request_user

ALLOWED_EXTENSIONS = set(list(['png', 'jpg', 'jpeg']))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_users_list():
    query = client.query()
    results = list(query.fetch())

    data = list()
    for obj in results:
        data_dict = dict()
        for key, value in obj.items():
            data_dict[key] = value

        data.append(data_dict)

    users_list = list()
    for obj in data:
        if obj.get("profile") == True and obj.get("user_id") and obj.get("user_id") != request_user["uid"]:
            users_list.append(obj)
        else:
            continue

    final = list(filter(None, users_list))
    final_data = list({v['user_id']: v for v in final}.values())
    return final_data


def get_entities(entity_kind):
    query = client.query(kind=entity_kind)
    results = list(query.fetch())

    data = list()
    for obj in results:
        data_dict = dict()
        for key, value in obj.items():
            data_dict[key] = value

        data.append(data_dict)

    return list(filter(None, data))


def get_all_tweets(entity_kind):
    query = client.query(kind=entity_kind)
    results = list(query.fetch())

    data = list()
    for obj in results:
        data_dict = dict()
        for key, value in obj.items():
            data_dict[key] = value

        data.append(data_dict)

    for obj in data:
        if obj.get("post_id"):
            continue
        else:
            data.remove(obj)

    return data


def get_tweets(entity_kind):
    data = list()
    user_tweets = get_all_tweets(entity_kind)
    data.extend(user_tweets)

    user_data = get_profile_details(entity_kind)
    try:
        if user_data:
            for obj in list(filter(None, user_data.get("following", []))):
                following_tweets = get_all_tweets(obj.get('user_id'))
                data.extend(following_tweets)
    except:
        pass

    final_data = list(filter(None, data))
    random.shuffle(final_data)
    return final_data


def get_post_details(post_id):
    data = get_entities(request_user["uid"])

    for obj in data:
        if obj.get("post_id") == post_id:
            return obj


def get_profile_details(user_id):
    data = get_entities(user_id)

    for obj in data:
        if obj.get("profile") == True:
            return obj


def get_followings(user_id):
    data = get_entities(user_id)

    for obj in data:
        if obj.get("profile") == True:
            final_data = list({v['user_id']: v for v in obj.get("following") if type(v) != str}.values())
            return final_data


def get_followers(user_id):
    data = get_entities(user_id)

    for obj in data:
        if obj.get("profile") == True:
            following = obj.get("following")
            followers = list(filter(None, obj.get("followers")))

            for follower in followers:
                if follower in following and type(follower) != str:
                    follower.update({'is_following': True})
                else:
                    continue

            # final_data = list({v['user_id']: v for v in followers if type(v) != str()}.values())
            return followers