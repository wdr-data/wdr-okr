.. _backend_youtube:

YouTube-Daten anlegen
=====================

[TBD]
Advance Analytics

Custom-Date = 1Tag

Export als csv

Zip File hochladen (mehrere auf einmal - müssen alle vom gleichen Kanal stammen)
Dateinamenn nicht verändern, muss genau so heißen, wie es von YouTube kommt


Weil YouTube im Moment noch keine Daten zu Impressions und Clicks zum
automatisierten Abruf zur Verfügung stellt, lassen sich diese Daten über einen
manuellen Upload im Backend zur Datenbank hinzufügen.

Dazu muss für jeden Tag eine separate CSV-Datei bei YouTube heruntergeladen
und dann im Backend wieder hochgeladen werden.

Voraussetzungen
---------------

- Zugangsdaten für `studio.youtube.com <https://studio.youtube.com/>`_ mit den
  gewünschten YouTube-Kanälen
- Zugang zum Backend des OKR Data Warehouse (Django)

Vorgehen
--------

Das Hinzufügen der Daten zur Datenbank besteht aus zwei Schritten:

1. :ref:`Herunterladen der Daten bei YouTube <backend_youtube_herunterladen>`
2. :ref:`Einfügen der Daten in das Backend des OKR Data Warehouse <backend_youtube_hochladen>`

.. _backend_youtube_herunterladen:

Herunterladen der Daten bei YouTube
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Melde dich als erstes im `YouTube Creator Studio <https://studio.youtube.com/>`_
an und wechsle in den gewünschten Account. Anschließend wähle den Analytics
Advanced Mode aus:

    1. Wähle den Punkt *Analytics* in der linken Menüleiste.
    2. Klicke oben rechts auf *ADVANCED MODE*.

       .. image:: ../_static/advanced_mode.png

    3. Stelle sicher, dass der Reiter *Video* aktiviert ist.
    4. Stelle rechts oben das jeweilige Datum ein. Dabei ist es wichtig, dass
       du nur einen Tag auswählst, nicht mehrere Tage. Es sollte dort also
       *1 day selected* stehen.

       .. image:: ../_static/datum.png

    5. Wähle *Export Current View* aus und speichere die Daten als *.csv*-Datei
       ab.

       .. image:: ../_static/csv-export.png

.. _backend_youtube_hochladen:

Einfügen der Daten in das Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Melde dich im Backend des OKR Data Warehouse (Django) an.
2. Wähle in der Liste *OKR - Objectives and Key Results* den Link *YouTube
   Video Analytics Extra* aus.

   .. image:: ../_static/backend1.png

3. Wähle den Button `DATEI HOCHLADEN`.

   .. image:: ../_static/backend2.png

4. Nutze das *Choose Files* Feld um eine oder mehrere CSV-Dateien auszuwählen.
5. Wähle den Button *HOCHLADEN* (bitte nur einmal anklicken, der Upload kann ein
   paar Sekunden dauern).

Falls die Daten nicht korrekt eingelesen werden konnten, erscheint eine
entsprechende Fehlermeldung.
