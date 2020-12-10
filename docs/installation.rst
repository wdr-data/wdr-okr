.. _installation:

Installation
============

Der Intelligence Layer ist in Python geschrieben und basiert auf einem
`Django <https://www.djangoproject.com/>`_-Backend.

Voraussetzungen
---------------

Der Intelligence Layer benötigt mindestens Python Version 3.6. Zur Erstellung und
Verwaltung einer virtuellen Umgebung muss außerdem `pipenv <http://www.python.org/>`_
installiert sein.

.. _installation_datenbank:

Datenbank
~~~~~~~~~

Eine SQL-Datenbank ist nicht zwingend erfoderlich. Wenn keine Datenbank zur Verfügung
gestellt wird, nutzt der Intelligence Layer automatisch eine lokale SQLite-Datenbank.

Um den Intelligence Layer mit einer SQL-Datenbank zu nutzen, muss die Datenbank-URL in
der Umgebungsvariable ``DATABASE_URL`` abgespeichert sein. Ist ``DATABASE_URL`` nicht
gesetzt, nutzt der Intelligence Layer die lokale SQLite Datenbank.

.. _installation_zugangsdaten:

API-Zugangsdaten
~~~~~~~~~~~~~~~~

Der Intelligence Layer nutzt zahlreiche APIs. Die Zugangsdaten der APIs müssen als
Umgebungsvariablen zur Verfügung stehen:

.. code-block:: bash

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

    # Spotify
    SPOTIPY_CLIENT_ID=
    SPOTIPY_CLIENT_SECRET=
    SPOTIFY_LICENSOR_I

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

Die Variable ``SECRET_KEY`` muss nur angegeben werden, wenn ``DEBUG=False`` gesetzt ist.

Um den Intelligence Layer lokal auszuführen, sollten die Umgebungsvariablen in eine
Datei namens ``.env`` im Root-Verzeichnis abgelegt werden. Auf diese Weise kann die
Umgebung automatisch von ``pipenv`` eingerichtet werden.

Installation und Inbetriebnahme
-------------------------------

Zunächst das GitHub Repository `wdr-data/wdr-okr <https://github.com/wdr-data/wdr-okr>`_
mit ``clone`` in ein lokales Verzeichnis herunterladen.

Anschließend sicherstellen, dass die Umgebungsvariablen für die
:ref:`installation_zugangsdaten` und ggf. die :ref:`installation_datenbank` korrekt
gesetzt sind.

Nun die benötigten Pakete mit Hilfe von ``pipenv`` herunterladen und installieren:

.. code-block:: bash

    $ pipenv sync

Anschließend die Datenbank-Migration für Django ausführen:

.. code-block:: bash

    $ pipenv run manage migrate

Erstellung eines Admin-Nutzers für das Django-Backend:

.. code-block:: bash

    $ pipenv run manage createsuperuser

Nun kann das Django-Backend über den folgenden Befehl gestartet werden:

.. code-block:: bash

    $ pipenv run manage runserver

Sobald der Intelligence Layer gestartet ist, ruft er automatisiert Daten über die
diversen APIs ab. Der Intelligence Layer nutzt dazu den
`APScheduler <https://pypi.org/project/APScheduler/>`_. Die Cron-basierten Regeln sind
in der Datei ``okr/scrapers/scheduler.py`` anpassbar.
