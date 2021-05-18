.. WDR OKR - Data Warehouse documentation master file, created by
   sphinx-quickstart on Thu Dec 10 10:37:07 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

WDR OKR Data Warehouse
======================

Das WDR OKR-Projekt
-------------------

Das WDR OKR-Projekt dient der automatisierten Erfassung, Analyse und Visualisierung von
Daten zur Nutzung unterschiedlicher digitaler Angebote.

Das Gesamtprojekt nutzt dazu zwei Komponenten:

* **Data Warehouse**: Ein System, das Daten aus unterschiedlichen Quellen
  (Instagram, Youtube, Spotify, Webserver-Statistiken, etc.) ausliest, in ein nutzbares
  Format bringt und in einer Datenbank bereitstellt.
* **Daten-Visualisierung**: Eine Reihe von Visualisierungen und Auswertungen in chart.io,
  die auf den Daten im Data Warehouse basieren.

Inhalt dieser Dokumentation
---------------------------

Diese Dokumentation bezieht sich auf das OKR Data Warehouse:

* Informationen zur **Installation und Inbetriebnahme** befinden sich im Kapitel
  :ref:`installation`.
* Informationen zu den **Scrapern für die einzelnen Datenquellen** (Instagram, Youtube,
  Facebook, Twitter, Spotify, Sophora, Webserver-Statistiken, etc.) befinden sich im
  Kapitel :ref:`scraper`.
* Informationen zur Benutzung des **Django-basierten Backends** zum Anlegen und
  Editieren von Datenquellen befindet sich im Kapitel :ref:`backend`.
* Informationen zu **Struktur und Inhalt der Datenbank** befinden sich im Kapitel
  :ref:`database`.
* Informationen zu den **einzelnen Python-Modulen** befinden sich im Kapitel
  :ref:`modules`.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents:

   installation
   scraper
   backend
   database
   modules/modules

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
