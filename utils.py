from DB import client
from Auth import db, request_user

ALLOWED_EXTENSIONS = set(list(['png', 'jpg']))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_users_list():
    all_users = db.child("users").get()

    users_list = []
    for user in all_users.each():
        if request_user.get('uid') != user.item[0]:
            users_list.append({
                "user_id": user.item[0],
                "user_name": user.item[1].get("name", "")
            })

    return users_list


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
            return obj.get("following")
        
        
def get_followers(user_id):
    data = get_entities(user_id)

    for obj in data:
        if obj.get("profile") == True:
            return obj.get("followers")