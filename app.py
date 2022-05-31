from flask import Flask, request, redirect, flash, get_flashed_messages
from mako.lookup import TemplateLookup
from nanoid import generate
from forms import URLShortenerForm
from sqlite3 import connect, Row

def get_db_conn():
    conn = connect("database.db")
    conn.row_factory = Row
    return conn

app = Flask(__name__)
app.config["SECRET_KEY"] = "8bd9bcd109b0d5315f88dc9e32079807475ac01523b9cfa9191c412ba36a2c6e"
app.config["DEBUG"] = True

templates = TemplateLookup(directories=["./views"], module_directory="/tmp/mako_modules")
def serve_template(name, **kwargs):
    template = templates.get_template(name)
    return template.render(**kwargs, messages=get_flashed_messages())

@app.route("/", methods=("GET", "POST"))
def index():
    conn = get_db_conn()
    form = URLShortenerForm()

    if form.validate_on_submit():
        url = form.url.data
        unique_id = generate(size=13)
        shortened_url = request.host_url + unique_id
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
            conn.execute(f"INSERT INTO urls (id, original_url) VALUES (?, ?)", (unique_id, url))
            conn.commit()
            conn.close()

        return serve_template("index.html", form=form, shortened_url=shortened_url)
    return serve_template("index.html", form=form)

@app.route("/<id>")
def redirect_to(id):
    conn = get_db_conn()

    url_data = conn.execute("SELECT original_url, clicks FROM urls "
                            f"WHERE id = (?)", (id,)).fetchone()
    if url_data is None:
        return serve_template("404.html")
    else:
        original_url = url_data["original_url"]
        clicks = url_data["clicks"]

        conn.execute(f"UPDATE urls SET clicks = ? WHERE id = ?", (clicks + 1, id))
        conn.commit()
        conn.close()

    return redirect(original_url)
