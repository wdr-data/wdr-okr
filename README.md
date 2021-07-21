# WDR-OKR

## About the project

This _Django_-Project is part of a process to establish the
[OKR Framework](https://de.wikipedia.org/wiki/Objectives_and_Key_Results) in
the organizational structure of the WDR.
After identifying the correct KPI for each product, this library collects and
processes the corresponding data to visualize the data in form of a dashboard.
## Local development

This project requires Python > 3.8, [pipenv](https://pipenv.pypa.io/en/latest/),
and a [Redis server](https://developer.redislabs.com/create) installed and
working on your system.

### Environment variables

To run the Django framework for this project, you need to set the following
environment variables:

```env
# Django
DEBUG=True
SECRET_KEY=
LOG_SQL=

# Quintly
QUINTLY_CLIENT_ID=
QUINTLY_CLIENT_SECRET=

# MySQL Podstat/Spotify
MYSQL_PODCAST_HOST=
MYSQL_PODCAST_USER=
MYSQL_PODCAST_PASSWORD=
MYSQL_PODCAST_DATABASE_PODSTAT=

# Spotify
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
SPOTIFY_LICENSOR_ID=

# Webtrekk/Mapp
WEBTREKK_LOGIN=
WEBTREKK_PASSWORD=
WEBTREKK_ACCOUNT_LIVE_ID=

# Sophora API
SOPHORA_API_BASE=

# SEO bot
TEAMS_WEBHOOK_SEO_BOT=
SEO_BOT_TODO_MORE_URL=
SEO_BOT_TOP_ARTICLES_THRESHOLD=
```

The `SECRET_KEY` is only required if you have set `DEBUG=False`.

To run the project locally, store these variables in an `.env` file in the root
folder.

### First time setup

Install requirements:

```bash=bash
$ pipenv sync
```

Migrate the database:

```bash=bash
$ pipenv run manage migrate
```

Create initial admin user:

```bash=bash
$ pipenv run manage createsuperuser
```

### Running

This project consists of two processes that communicate through
[Redis Queue (RQ)](<https://python-rq.org/>).

The `worker` process runs the various scrapers while the `web` process runs the
Django server and backend.

First, start the `worker` process:

```bash=bash
$ pipenv run worker
```

Then, start the `web` process:

```bash=bash
$ pipenv run manage runserver
```

### Collecting data

Scrapers are located in `okr/scrapers/` with one module for each product type.

The `__init__.py` of each scraper module contains the functions to fill the
database. If cleaning or restructuring is required, it is done here.
There are other submodules for collecting the raw data, one for each source.

We use [RQ (Redis Queue)](https://python-rq.org/) and
[APScheduler](https://apscheduler.readthedocs.io/en/stable/) for queuing
and scheduling. `okr/scrapers/scheduler.py` contains the setup and cron-based
rules to run scrapers periodically at specified times.

Some data that can't be scraped automatically (yet) is manually entered or
uploaded as files in the Django admin backend. The relevant files for this
are located in `okr/admin`.

The data warehouse component is managed via the Django ORM. Models are defined
in `okr/models/` with generally self-contained submodules for each product type.

### Contributing

Install the `black` code formatter:

```bash=bash
$ pipenv run pip install black
```

Set up git pre-commit hook:
```bash=bash
$ cp git-hooks/pre-commit .git/hooks
```

## License

This project is licensed under the _MIT License_.

> Unsere Inhalte, unser Wissen und unsere Entwicklungen gehören allen.
> [WDR Geschäftsbericht 2016](https://www1.wdr.de/unternehmen/der-wdr/serviceangebot/services/infomaterial/geschaeftsbericht-122.pdf), S.23
