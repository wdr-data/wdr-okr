# WDR-OKR

## About the Project

This _DJANGO_-Project is part of a process to establish the [OKR Framework](https://de.wikipedia.org/wiki/Objectives_and_Key_Results) within the organisation of WDR.
After identifying the correct KPI for each product, we seek to collect the corresponding data to visualize the data in form of a dashboard.
Data ist collected by:
* connecting to analytic plattforms APIs
* manual data exports from analytic plattforms
* manual generated entries

## Local development

### Environment Variables
To run the Django framework, you'll need to set the following environment variables:
```env
DEBUG=True
SECRET_KEY=
QUINTLY_CLIENT_ID=
QUINTLY_CLIENT_SECRET=
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
$ pipenv run ./manage.py migrate
```

Create initial admin user:
```bash=bash
$ pipenv run ./manage.py createsuperuser
```

### Running Django
Start Django:
```bash=bash
$ pipenv run ./manage.py runserver
```

### Collecting data
There are several `POST` endpoints that trigger data collection from Quintly:
* `/okr/triggers/insta/insights/daily/`
* `/okr/triggers/insta/insights/weekly/`
* `/okr/triggers/insta/insights/monthly/`
* `/okr/triggers/insta/stories/`
* `/okr/triggers/insta/posts/`
* `/okr/triggers/youtube/analytics/daily/`
* `/okr/triggers/youtube/analytics/weekly/`
* `/okr/triggers/youtube/analytics/monthly/`

## Datasoures

* [Quintly API](https://api.quintly.com/)
* YouTube Analytics .csv export (studio.youtube.com)
* Creators data

## Liscense

This project is licensed under the _MIT Liscence_.

> Unsere Inhalte, unser Wissen und unsere Entwicklungen gehören allen.
> [WDR Geschäftsbericht 2016](https://www1.wdr.de/unternehmen/der-wdr/serviceangebot/services/infomaterial/geschaeftsbericht-122.pdf), S.23
