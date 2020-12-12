.. _scraper:

Scraper
=======

Die Scraper des Intelligence Layer machen externe Datenquellen für die weitere Analyse
nutzbar. Für jede Datenquelle existiert ein individuell angepasstes Scraping-Modul.

Der Intelligence Layer nutzt sowohl automatisiert abgerufene Daten von diversen APIS als
auch manuell hochgeladene Daten aus statischen Dateien.

Daten-Quellen
-------------

Im Moment nutzt der Intelligence Layer die folgenden Daten-Quellen:

* Instagram-Accounts (automatisiert über die Quintly-API)
* Youtube-Accounts (manuell aus YouTube Analytics exportiert)
* Webseiten (automatisiert über die APIs der Google Search Console und von Sophora)
* Podcasts (automatisiert über öffentlich zugängliche RSS-Feeds sowie die APIs von
  Spotify, Podstat, Mediatrend und Webtrekk)

Struktur der Scraping Skripte
-----------------------------

Die Scripte für das Erfassen und Aufbereiten der Daten befinden sich im Verzeichnis
``okr/scrapers/``. Es existieren unterschiedliche Module für die unterschiedlichen Arten
von digitalen Angeboten: ``insta``, ``pages``, ``podcasts`` und ``youtube``.

Jeds Modul entählt eine ``__init.py__`` Datei. Diese Datei enthält jeweils die
grundlegenden Funktionen zum Speichern und Aufbereiten der Daten. Das Abrufen der
Rohdaten geschieht in den jeweiligen Submodulen.

Details zu den einzelnen Scraping-Modulen befinden sich in der :ref:`modules` im
Abschnitt :class:`okr.scrapers`.
