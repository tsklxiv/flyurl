# FlyURL - Let your URL fly!

FlyURL is a simple, self-hosted URL shortener.

# Getting started

Clone this repository, then run:

```sh
cd flyurl
source venv/bin/Activate      # Bash
source venv/bin/Activate.csh  # csh
source venv/bin/Activate.fish # fish
source venv/bin/Activate.ps1  # Powershell
python init_db.py
flask run
```

# Tech stack
- [Flask](https://flask.palletsprojects.com/en/2.1.x/) (Web framework)
- [Mako](https://www.makotemplates.org/) (Template engine)
- [SQLite](https://sqlite.org) (Database)
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/) (Handling forms)
- [Bahunya](https://hakanalpay.com/bahunya/) (CSS styling)
