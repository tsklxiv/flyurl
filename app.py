from flask import Flask, request, redirect, flash, get_flashed_messages
from mako.lookup import TemplateLookup
from hashlib import sha256
from forms import URLShortenerForm
from sqlite3 import connect, Row
from urllib.parse import urlparse

def get_db_conn():
    conn = connect("database.db")
    conn.row_factory = Row
    return conn

blacklisted_domains = open("static/general_blacklist.txt", "r").read().split("\n") + open("static/url_shorteners_blacklist.txt", "r").read().split("\n")[3:]
app = Flask(__name__)
app.config["SECRET_KEY"] = "8bd9bcd109b0d5315f88dc9e32079807475ac01523b9cfa9191c412ba36a2c6e"

templates = TemplateLookup(directories=["./templates"], module_directory="/tmp/mako_modules")
def serve_template(name, **kwargs):
    template = templates.get_template(name)
    return template.render(**kwargs, messages=get_flashed_messages())

@app.route("/", methods=("GET", "POST"))
def index():
    conn = get_db_conn()
    form = URLShortenerForm()

    if form.validate_on_submit():
        url = form.url.data
        hostname = urlparse(url).hostname # For checking if blacklisted or not
        custom_key = form.custom_key.data
        unique_id = (sha256(url.encode("ascii")).hexdigest()[:7] if custom_key == "" else custom_key)
        shortened_url = f"http://{request.host}/{unique_id}"
        preview_url = f"http://{request.host}/p/{unique_id}"
        if (hostname is not None and hostname in blacklisted_domains):
            return serve_template(
                "error.html",
                msg="This URL is in the internal blacklist. It may contain porn or other nasty stuff, or link to another URL redirection service."
            )
        # Make sure that we aren't duplicating the same URL over and over again
        find_url = conn.execute("SELECT * FROM urls WHERE id = (?)", (unique_id,)).fetchone()
        if find_url is not None:
            flash("URL already exists in database!")
            redirect("/")
        else:
            print(f"Original URL: {url}\n"
              f"Unique ID: {unique_id}\n"
              f"Shortened URL: {shortened_url}")
            form.url.data = ""
            form.custom_key.data = ""
            conn.execute(f"INSERT INTO urls (id, original_url) VALUES (?, ?)", (unique_id, url))
            conn.commit()
            conn.close()

        return serve_template("index.html",
                              form=form,
                              shortened_url=shortened_url,
                              preview_url=preview_url)
    return serve_template("index.html", form=form)

@app.route("/<id>")
def redirect_to(id):
    conn = get_db_conn()

    url_data = conn.execute("SELECT original_url, clicks FROM urls "
                            "WHERE id = (?)", (id,)).fetchone()
    if url_data is None:
        return serve_template("error.html", msg="Unable to redirect to URL.")
    else:
        original_url = url_data["original_url"]
        clicks = url_data["clicks"]

        conn.execute(f"UPDATE urls SET clicks = ? WHERE id = ?", (clicks + 1, id))
        conn.commit()
        conn.close()

    return redirect(original_url)

@app.route("/p/<id>")
def preview(id):
    conn = get_db_conn()
    url_data = conn.execute("SELECT original_url FROM urls WHERE id = (?)", (id,)).fetchone()
    conn.commit()
    conn.close()
    if url_data is None:
        return serve_template("error.html", msg="This ID doesn't exist in the database.")
    else:
        original_url = url_data["original_url"]
        return serve_template("preview.html", original_url=original_url, id=id)

@app.route("/s/<id>")
def stat(id):
    conn = get_db_conn()
    url_data = conn.execute("SELECT clicks, time, original_url FROM urls WHERE id = (?)", (id,)).fetchone()
    conn.commit()
    conn.close()
    if url_data is None:
        return serve_template("error.html", msg="This ID doesn't exist in the database.")
    else:
        clicks = url_data["clicks"]
        original_url = url_data["original_url"]
        created_date = url_data["time"]
        shortened_url = f"http://{request.host}/{id}"
        return serve_template("stat.html",
                              clicks=clicks,
                              original_url=original_url,
                              shortened_url=shortened_url,
                              created_date=created_date)
