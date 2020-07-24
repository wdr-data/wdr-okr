# WDR-OKR

## About the Project

This _Django_-Project is part of a process to establish the [OKR Framework](https://de.wikipedia.org/wiki/Objectives_and_Key_Results) within the organisation of WDR.
After identifying the correct KPI for each product, we seek to collect the corresponding data to visualize the data in form of a dashboard.

Data ist collected from:

- Analytics platform APIs
- Manual data exports from analytics platforms
- Manually generated entries

## Local development

### Environment Variables

To run the Django framework, you'll need to set the following environment variables:

```env
# Django
DEBUG=True
SECRET_KEY=

# Quintly
QUINTLY_CLIENT_ID=
QUINTLY_CLIENT_SECRET=

# MySQL Podstat/Spotify
MYSQL_PODCAST_HOST=
MYSQL_PODCAST_USER=
MYSQL_PODCAST_PASSWORD=
MYSQL_PODCAST_DATABASE_SPOTIFY=
MYSQL_PODCAST_DATABASE_PODSTAT=
```

The `SECRET_KEY` is only required if you have set `DEBUG=False`.

To run the project locally, store these variables in an `.env` file in the root folder.

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

### Running Django

Start Django:

```bash=bash
$ pipenv run manage runserver
```

### Collecting data

Scrapers are located in `okr/scrapers/` with one module for each product type.

The `__init__.py` of each scraper module contains the functions to fill the intelligence layer. If cleaning or restructuring is required, it is done here. There are other submodules for collecting the raw data, one for each source.

We use APScheduler for scheduling. `okr/scrapers/scheduler.py` contains the setup and cron-based rules to run scrapers periodically at specified times.

Some data that can't be scraped automatically (yet) is manually entered or uploaded as files in the Django admin backend. The relevant files for this are located in `okr/admin`.

Our intelligence layer is managed via the Django ORM. Models are defined in `okr/models/` with generally self-contained submodules for each product type.

## Datasoures

- [Quintly API](https://api.quintly.com/)
- YouTube Analytics .csv export (studio.youtube.com)
- Creators data
- In-house SQL databases

## License

This project is licensed under the _MIT License_.

> Unsere Inhalte, unser Wissen und unsere Entwicklungen gehören allen.
> [WDR Geschäftsbericht 2016](https://www1.wdr.de/unternehmen/der-wdr/serviceangebot/services/infomaterial/geschaeftsbericht-122.pdf), S.23
