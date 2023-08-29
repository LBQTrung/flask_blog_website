from . import auth
from flask import render_template, redirect, request, url_for
import json
from flask_login import current_user, login_required, login_user, logout_user
import requests
from oauthlib.oauth2 import WebApplicationClient
from app.models import User
from app import db
import os

# Read from app/client_secret.json
json_path = os.path.join(os.path.dirname(__file__), "..", "client_secret.json")
with open(json_path) as json_file:
    client_config = json.load(json_file)["web"]


# Configuration
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = client_config["client_id"]
GOOGLE_CLIENT_SECRET = client_config["client_secret"]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@auth.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=client_config["redirect_uris"][0],
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)


@auth.route("/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=client_config["redirect_uris"][0],
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        user_email = userinfo_response.json()["email"]
        user_name = userinfo_response.json()["name"]
        user_avatar = userinfo_response.json()["picture"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User.query.filter_by(email=user_email).first()

    # Doesn't exist? Add it to the database.
    if not user:
        user = User(email=user_email, name=user_name, avatar_url=user_avatar)
        db.session.add(user)

    user.avatar_url = user_avatar
    db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("main.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
