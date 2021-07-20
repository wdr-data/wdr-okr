.. _installation:

Installation
============

Das OKR Data Warehouse ist in Python geschrieben und basiert auf einem
`Django <https://www.djangoproject.com/>`_-Backend.

.. _installation_voraussetzungen:

Grundlagen
----------

OKR Data Warehouse ist für den Betrieb auf der Plattform
`Heroku <https://www.heroku.com/>`_ vorgesehen und getestet. Daneben ist es auch
möglich, das OKR Data Warehouse auf einem lokalen Testsystem oder einem anderen
System mit den folgenden Mindestvoraussetzungen in Betrieb zu nehmen:

* Mindestens Python Version 3.8.
* `pipenv <https://pipenv.pypa.io/en/latest/>`_ zur Erstellung und Verwaltung einer
  virtuellen Umgebung
* Ein `Redis Server <https://developer.redislabs.com/create>`_ für die Übermittlung
  von Informationen zwischen den Prozessen des OKR Data Warehouse

Das OKR Data Warehouse läuft in zwei parallelen Prozessen (separate Dynos bei Heroku):

.. _installation_voraussetzungen_web:

Web
    Im Web-Prozess (bzw. -Dyno) läuft das :ref:`backend` zum Anlegend und Editieren von
    Datenquellen.

.. _installation_voraussetzungen_worker:

Worker
    Im Worker-Prozess (bzw. -Dyno) laufen die :ref:`Scraper`. Der Worker wird mit dem
    Script ``worker.py`` im Wurzel-Verzeichnis des OKR Data Warehouse gesteuert.

Die beiden Prozesse tauschen über `Redis Queue (RQ) <https://python-rq.org/>`_
Informationen aus. Beide Prozesse nutzen außerdem das
`Django ORM <https://docs.djangoproject.com/en/3.2/topics/db/queries/>`_ zum Zugriff auf
die :ref:`installation_datenbank`.

.. _installation_datenbank:

Datenbank
---------

Eine server-basierte SQL-Datenbank ist nicht zwingend erforderlich. Wenn keine
Datenbank-URL zur Verfügung gestellt wird, nutzt das OKR Data Warehouse automatisch
eine lokale SQLite-Datenbank.

Um das OKR Data Warehouse mit einer server-basierten SQL-Datenbank zu nutzen, muss die
Datenbank-URL in der Umgebungsvariable ``DATABASE_URL`` gespeichert sein. Ist
``DATABASE_URL`` nicht gesetzt, nutzt das OKR Data Warehouse die lokale SQLite
Datenbank.

.. _installation_zugangsdaten:

API-Zugangsdaten
----------------

Das OKR Data Warehouse nutzt zahlreiche APIs. Die Zugangsdaten der APIs müssen als
Umgebungsvariablen zur Verfügung stehen:

.. code-block:: bash

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

    # Spotify Podcast API
    EXPERIMENTAL_SPOTIFY_BASE_URL=
    EXPERIMENTAL_SPOTIFY_AUTH_URL=
    EXPERIMENTAL_SPOTIFY_CLIENT_ID=
    EXPERIMENTAL_SPOTIFY_SP_AC=
    EXPERIMENTAL_SPOTIFY_SP_DC=
    EXPERIMENTAL_SPOTIFY_SP_KEY=

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

Die Variable ``SECRET_KEY`` muss nur angegeben werden, wenn ``DEBUG=False`` gesetzt ist.

Um das OKR Data Warehouse lokal auszuführen, sollten die Umgebungsvariablen in eine
Datei namens ``.env`` im Root-Verzeichnis abgelegt werden. Auf diese Weise kann die
Umgebung automatisch von ``pipenv`` eingerichtet werden.

Download und Inbetriebnahme
---------------------------

Zunächst das GitHub Repository `wdr-data/wdr-okr <https://github.com/wdr-data/wdr-okr>`_
mit ``clone`` in ein lokales Verzeichnis herunterladen.

Anschließend sicherstellen, dass die Umgebungsvariablen für die
:ref:`installation_zugangsdaten` und ggf. die :ref:`installation_datenbank` korrekt
gesetzt sind.

Zunächst sicher stellen, dass die oben beschriebenen :ref:`installation_voraussetzungen`
erfüllt sind. Anschließend die benötigten Pakete mit Hilfe von ``pipenv`` herunterladen
und installieren:

.. code-block:: bash

    $ pipenv sync

Anschließend die Datenbank-Migration für Django ausführen:

.. code-block:: bash

    $ pipenv run manage migrate

Zum Schluss noch einen Admin-Nutzers für das Django-Backend anlegen:

.. code-block:: bash

    $ pipenv run manage createsuperuser

Nun können die beiden Prozesse :ref:`web <installation_voraussetzungen_web>` und
:ref:`worker <installation_voraussetzungen_worker>` gestartet werden. Dazu zunächst den
Worker-Prozess starten:

.. code-block:: bash

    $ pipenv run worker

Anschließend den Web-Prozess mit Django-Server starten:

.. code-block:: bash

    $ pipenv run manage runserver

Sobald das OKR Data Warehouse gestartet ist, ruft das System
:ref:`zeitgesteuert <scraper_scheduler>` Daten über die
:ref:`diversen APIs <scraper_datenquellen>` ab.
