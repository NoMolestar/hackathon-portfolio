import os

from dotenv import load_dotenv
from flask import Flask, render_template, abort, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from data.load_data import load_posts_info

load_dotenv()
app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UserModel(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"


base_url = os.getenv("URL")
posts_base_url = base_url + "/posts/"

# TODO: This will be deleted since posts will be stored in the database
posts_info = load_posts_info()


@app.route("/")
def index():
    # TODO: Implement pagination
    return render_template(
        "index.html",
        # TODO: query posts info page from db
        posts=posts_info,
        title="Blog",
        url=base_url,
    )


@app.route("/posts/<post_id>")
def get_post(post_id):
    # TODO: query post from db
    if post_id not in posts_info:
        return abort(404)
    title = posts_info[post_id]["title"]
    return render_template(
        "post.html", post=posts_info[post_id], title=title, url=posts_base_url + post_id
    )


@app.route("/posts/<post_id>/edit")
def get_edit_post(post_id):
    # TODO: query post from db
    if post_id not in posts_info:
        return abort(404)
    title = posts_info[post_id]["title"]
    return render_template(
        "edit_post.html", item=posts_info[post_id], title=title, url=posts_base_url + post_id + "/edit"
    )


@app.route("/posts/new")
def get_create_post():
    return render_template(
        "create_post.html", title="Create new post", url=posts_base_url + "new"
    )


# TODO: Implement create and edit post endpoints


@app.route("/health")
def get_health():
    return "", 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page not found"), 404


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    return render_template("register.html", title="Sign up")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418

    return render_template("login.html", title="Login")
