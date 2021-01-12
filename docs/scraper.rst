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

Für Daten zu Online-Artikeln:
  * webtrekk API (`webtrekk Dokumentation`_)
  * Google Search Console (`GSC Dokumentation`_)
  * Sophora API ("App-API")

Für Daten zu Instagram:
  * Quintly API (`Quintly Dokumentation`_)
  * Manueller Daten-Import für Instagram Collaborations

Für Daten zu Podcasts:
  * webtrekk API (`webtrekk Dokumentation`_)
  * Podstat-Datenbank
  * Spotify Podcast API (`Podcast-API Dokumentation`_)
  * Spotify Web API (`Web-API Dokumentation`_)
  * Spotify Analytics

Für Daten zu Youtube:
  * Quintly API (`Quintly Dokumentation`_)
  * Manueller Daten-Import

Scheduler für den Daten-Abruf
-----------------------------

Die Daten werden nach einem festgelegten Zeitplan aus den unterschiedlichen Datenquellen
abgerufen. Die individuellen Zeitintervalle sind innerhalb der Funktion
:func:`okr.scrapers.scheduler.start` im Modul ``okr/scrapers/scheduler.py`` definiert.

Der Intelligence Layer nutzt dafür die Bibliothek
`Advanced Python Scheduler <https://apscheduler.readthedocs.io/en/latest/>`_.

Struktur der Scraping Skripte
-----------------------------

Die Scripte für das Erfassen und Aufbereiten der Daten befinden sich im Verzeichnis
``okr/scrapers/``. Es existieren unterschiedliche Module für die unterschiedlichen Arten
von digitalen Angeboten: :class:`~okr.scrapers.insta`, :class:`~okr.scrapers.pages`,
:class:`~okr.scrapers.podcasts` und :class:`~okr.scrapers.youtube`.

Jedes Modul enthält eine ``__init.py__`` Datei. Diese Datei enthält jeweils die
grundlegenden Funktionen zum Speichern und Aufbereiten der Daten. Das Abrufen der
Rohdaten geschieht in den jeweiligen Submodulen.

Details zu den einzelnen Scraping-Modulen befinden sich in der :ref:`modules` im
Abschnitt :class:`okr.scrapers`.

.. _`GSC Dokumentation`: https://developers.google.com/webmaster-tools
.. _`Podcast-API Dokumentation`: https://developer.spotify.com/community/news/2020/03/20/introducing-podcasts-api/
.. _`Quintly Dokumentation`: https://api.quintly.com/
.. _`Web-API Dokumentation`: https://developer.spotify.com/documentation/web-api/
.. _`webtrekk Dokumentation`: https://docs.mapp.com/download/attachments/33784075/Webtrekk-JSON-RPC_API_Manual-EN.pdf?version=1&modificationDate=1589549566000&api=v2
