.. _scraper:

Scraper
=======

Die Scraper des Intelligence Layer machen externe Datenquellen für die weitere Analyse
nutzbar. Für jede Datenquelle existiert ein individuell angepasstes Scraping-Modul.

Der Intelligence Layer nutzt sowohl automatisiert abgerufene Daten von diversen APIs als
auch manuell hochgeladene Daten aus statischen Dateien.

.. _scraper_datenquellen:

Daten-Quellen
-------------

Im Moment nutzt der Intelligence Layer die folgenden Daten-Quellen:

Für Daten zu Online-Artikeln:
  * Webtrekk API (`Webtrekk Dokumentation`_)
  * Google Search Console (`GSC Dokumentation`_)
  * Sophora API ("App-API")

Für Daten zu Instagram:
  * Quintly API (`Quintly Dokumentation`_)
  * Manuelle Dateneingabe für Instagram Collaborations

Für Daten zu Podcasts:
  * Webtrekk API (`Webtrekk Dokumentation`_)
  * Podstat-Datenbank
  * Spotify for Podcasters Data API
  * Spotify Web API (`Web-API Dokumentation`_)
  * Spotify Analytics

Für Daten zu Youtube:
  * Quintly API (`Quintly Dokumentation`_)
  * Manueller Daten-Import aus YouTube Studio

.. _scraper_scheduler:

Scheduler für den Daten-Abruf
-----------------------------

Die Daten werden nach einem festgelegten Zeitplan aus den unterschiedlichen Datenquellen
abgerufen. Die individuellen Zeitintervalle für die unterschiedlichen Methoden sind wie
folgt definiert:

.. schedule_table::

Die einzelnen Zeitpunkte sind innerhalb der Funktion
:func:`okr.scrapers.scheduler.start` im Modul ``okr/scrapers/scheduler.py`` definiert.

.. seealso::
   Mehr Informationen zu den Methoden in dieser Tabelle sind im Bereich
   :class:`okr.scrapers` in der :ref:`modules` zu finden.

Struktur der Scraping Skripte
-----------------------------

Die Scripte für das Erfassen und Aufbereiten der Daten befinden sich im Verzeichnis
``okr/scrapers/``. Es existieren unterschiedliche Module für die unterschiedlichen Arten
von digitalen Angeboten: :class:`~okr.scrapers.insta`, :class:`~okr.scrapers.pages`,
:class:`~okr.scrapers.podcasts` und :class:`~okr.scrapers.youtube`.

Jedes Modul enthält eine ``__init.py__`` Datei. Diese Datei enthält jeweils die
grundlegenden Funktionen zum Speichern und Aufbereiten der Daten. Das Abrufen der
Rohdaten geschieht in den jeweiligen Submodulen.

.. seealso::
   Details zu den einzelnen Scraping-Modulen befinden sich in der :ref:`modules` im
   Abschnitt :class:`okr.scrapers`.

.. _`GSC Dokumentation`: https://developers.google.com/webmaster-tools
.. _`Quintly Dokumentation`: https://api.quintly.com/
.. _`Web-API Dokumentation`: https://developer.spotify.com/documentation/web-api/
.. _`Webtrekk Dokumentation`: https://docs.mapp.com/download/attachments/33784075/Webtrekk-JSON-RPC_API_Manual-EN.pdf?version=1&modificationDate=1589549566000&api=v2
