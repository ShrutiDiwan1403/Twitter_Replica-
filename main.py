import uuid
from datetime import date
from flask import Flask, redirect, render_template, request, url_for
from DB import client, datastore
from Auth import auth, db, request_user
from utils import get_profile_details, get_post_details, get_followers, get_followings, get_users_list

app = Flask(__name__)
today = date.today()


# Login
@app.route("/")
def login():
    if request_user["is_logged_in"] == True:
        return render_template("dashboard.html", email=request_user["email"], name=request_user["name"])
    else:
        return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    auth.current_user = None
    request_user["is_logged_in"] = False
    return render_template("login.html")


# Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    if request_user["is_logged_in"]:
        users_data = get_users_list()
        return render_template("dashboard.html", user_id=request_user["uid"], email=request_user["email"],
                               name=request_user["name"], users_data=users_data)


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        result = request.form  # Get the data
        email = result["email"]
        password = result["pass"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            global request_user
            request_user["is_logged_in"] = True
            request_user["email"] = user["email"]
            request_user["uid"] = user["localId"]
            data = db.child("users").get()
            request_user["name"] = data.val()[request_user["uid"]]["name"]
            # Redirect to welcome page
            return redirect(url_for('dashboard'))
        except Exception as e:
            # If there is any error, redirect back to login
            print(e)
            return redirect(url_for('login'))
    else:
        if request_user["is_logged_in"]:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))


# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        result = request.form  # Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            # Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            # Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            request_user["is_logged_in"] = True
            request_user["email"] = user["email"]
            request_user["uid"] = user["localId"]
            request_user["name"] = name
            # Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(request_user["uid"]).set(data)

            # Create User entity in datastore
            key = client.key(request_user["uid"], request_user["name"])
            entity = datastore.Entity(key=key)
            client.put(entity)

            # Create profile details
            key2 = client.key(request_user["uid"], "profile")
            entity2 = datastore.Entity(key=key2)
            entity2.update({
                "user_id": request_user["uid"],
                "profile": True,
                "user_name": request_user["name"],
                "email": request_user["email"],
                "description": "",
                "followers": [],
                "following": []
            })
            client.put(entity2)

            # Go to login page
            return redirect(url_for('login'))
        except:
            # If there is any error, redirect to register
            return redirect(url_for('register'))
    else:
        return redirect(url_for('login'))


@app.route("/edit-profile", methods=["POST", "GET"])
def edit_profile():
    if request_user["is_logged_in"]:
        if request.method == "POST":
            result = request.form
            user_name = result.get("user_name")  # HiddenInput
            email = result.get("email", "")
            description = result.get("description", "")
            followers = result.get("followers")  # HiddenInput
            following = result.get("following")  # HiddenInput
            
            # Update profile
            post_id = uuid.uuid4()
            key = client.key(request_user["uid"], post_id)
            entity = datastore.Entity(key=key)
            entity.update({
                "user_id": request_user["uid"],
                "profile": True,
                "user_name": user_name,
                "email": email,
                "description": description,
                "followers": followers,
                "following": following
            })
            client.put(entity)
        else:
            profile_details = get_profile_details(request_user["uid"])
            return render_template("create_post.html", profile_detail=profile_details)
    else:
        return redirect(url_for('login'))
    
    
@app.route("/create-post", methods=["POST", "GET"])
def create_post():
    if request_user["is_logged_in"]:
        if request.method == "POST":
            result = request.form
            description = result.get("description", "")
            image = result.get("image", "")

            post_id = uuid.uuid4()
            key = client.key(request_user["name"], post_id)
            entity = datastore.Entity(key=key)
            entity.update({
                "user_name": request_user["name"],
                "user_id": request_user["uid"],
                "post_id": post_id,
                "description": description,
                "image": image,
                "created_on": str(today)
            })
            client.put(entity)
        else:
            return render_template("create_post.html")
    else:
        return redirect(url_for('login'))


@app.route("/<user_id>/edit-post/<post_id>", methods=["POST", "GET"])
def edit_post(user_id, post_id):
    if request_user["is_logged_in"]:
        if request.method == "POST":
            result = request.form
            description = result.get("description", "")
            image = result.get("image", "")
            user_name = result.get("user_name")  # HiddenInput
            created_on = result.get("created_on")  # HiddenInput

            key = client.key(user_id, post_id)
            entity = datastore.Entity(key=key)
            entity.update({
                "user_name": user_name,
                "user_id": user_id,
                "post_id": post_id,
                "description": description,
                "image": image,
                "created_on": created_on
            })
            client.put(entity)
        else:
            post_details = get_post_details(post_id)
            return render_template("edit_post.html", post_detail=post_details)
    else:
        return redirect(url_for('login'))


@app.route("/<follow_id>/follow-user", methods=["POST", "GET"])
def follow_user(follow_id):
    if request_user["is_logged_in"]:
        request_user_details = get_profile_details(request_user["uid"])
        follow_user_details = get_profile_details(follow_id)
        
        request_user_following = request_user_details.get("following")
        list(set(request_user_following.append({
            "user_id": follow_user_details.get("user_id"),
            "user_name": follow_user_details.get("user_name")
        })))
        
        follow_user_followers = follow_user_details.get("followers")
        list(set(follow_user_followers.append({
            "user_id": request_user_details.get("user_id"),
            "user_name": request_user_details.get("user_name")
        })))
        
        request_user_key = client.key(request_user["uid"], "profile")
        request_user_entity = datastore.Entity(key=request_user_key)
        request_user_entity.update(request_user_details)
        client.put(request_user_entity)

        follow_user_key = client.key(request_user["uid"], "profile")
        follow_user_entity = datastore.Entity(key=follow_user_key)
        follow_user_entity.update(follow_user_details)
        client.put(follow_user_entity)
    else:
        return redirect(url_for('login'))


@app.route("/<follow_id>/unfollow-user", methods=["POST", "GET"])
def unfollow_user(follow_id):
    if request_user["is_logged_in"]:
        request_user_details = get_profile_details(request_user["uid"])
        follow_user_details = get_profile_details(follow_id)

        request_user_following = request_user_details.get("following")
        list(set(request_user_following.remove({
            "user_id": follow_user_details.get("user_id"),
            "user_name": follow_user_details.get("user_name")
        })))

        follow_user_followers = follow_user_details.get("followers")
        list(set(follow_user_followers.remove({
            "user_id": request_user_details.get("user_id"),
            "user_name": request_user_details.get("user_name")
        })))

        request_user_key = client.key(request_user["uid"], "profile")
        request_user_entity = datastore.Entity(key=request_user_key)
        request_user_entity.update(request_user_details)
        client.put(request_user_entity)

        follow_user_key = client.key(request_user["uid"], "profile")
        follow_user_entity = datastore.Entity(key=follow_user_key)
        follow_user_entity.update(follow_user_details)
        client.put(follow_user_entity)
    else:
        return redirect(url_for('login'))


@app.route("/<post_id>/delete-post", methods=["POST", "GET"])
def delete_post(post_id):
    if request_user["is_logged_in"]:
        key = client.key(request_user["uid"], post_id)
        entity = datastore.Entity(key=key)
        client.put(entity)
        # return redirect as per need
    else:
        return redirect(url_for('login'))


@app.route("/show-followings", methods=["GET"])
def show_followings():
    if request_user["is_logged_in"]:
        data = get_followings(request_user["uid"])
        return render_template("show_followings.html", data=data)
    else:
        return redirect(url_for('login'))


@app.route("/show-followers", methods=["GET"])
def show_followers():
    if request_user["is_logged_in"]:
        data = get_followers(request_user["uid"])
        return render_template("show_followers.html", data=data)
    else:
        return redirect(url_for('login'))


@app.route("/<user_id>/show-user-profile", methods=["GET"])
def show_user_profile(user_id):
    if request_user["is_logged_in"]:
        data = get_profile_details(user_id)
        return render_template("show_user_profile.html", user_detail=data)
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)