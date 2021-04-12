.. _backend_youtube:

YouTube-Daten anlegen
=====================

Weil momentan noch nicht alle Daten von YouTube zum automatisierten Abruf zur Verfügung
stehen, lassen sich diese Daten über eine Eingabemaske im Backend zur Datenbank
hinzufügen.

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

Bei YouTube musst du zwei Datenpakete herunterladen: eines mit
:ref:`Zielgruppen-Daten <backend_youtube_herunterladen_zielgruppen>` und eines
mit :ref:`Impressions-Daten <backend_youtube_herunterladen_impressions>`.

Melde dich als erstes im `YouTube Creator Studio <https://studio.youtube.com/>`_ an und wechsle in
den gewünschten Account. Anschließend wähle den Analytics Advanced Mode aus:

    1. Wähle den Punkt *Analytics* in der linken Menüleiste
    2. Klicke oben rechts auf *ADVANCED MODE*

.. _backend_youtube_herunterladen_zielgruppen:

Herunterladen der Zielgruppen-Daten:
    1. Den Reiter *Viewer age* aktivieren
    2. Zeitraum auswählen
    3. Start- und Enddaten für *wöchentlich* oder *monatlich* auswählen:

        - wöchentlich IMMER Montag bis Sonntag
        - monatlich nur abgeschlossene Monate (Erhebung frühestens am 04. des
          Folgemonats durchführen, da Daten bis zu 72h Verzug haben!)

    4. *Export Current View* auswählen und als *.csv*-Datei nach dem Schema
       *Viewer age YYYY-MM-DD_YYYY-MM-DD.zip* abspeichern.

    .. image:: ../_static/youtube1.png

.. _backend_youtube_herunterladen_impressions:

Herunterladen der Impressions-Daten:
    1. Den Reiter *Traffic source* aktivieren
    2. *Impressions by Traffic Source* auswählen
    3. *Browse features* auswählen
    4. Zeitraum einstellen: kann beliebig gewählt werden (z.B. letzte 90 Tage), da die
       Daten auf täglicher Basis exportiert und beim Upload ggf.
       überschrieben/aktualisiert werden
    5. *Export Current View* auswählen und als *.csv*-Datei nach dem Schema
       `Traffic source YYYY-MM-DD_YYYY-MM-DD.zip``

    .. image:: ../_static/youtube2.png

.. _backend_youtube_hochladen:

Einfügen der Daten in das Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Melde dich im Backend des OKR Data Warehouse (Django) an.
2. Wähle in der Liste *OKR - Objectives and Key Results* die entsprechende Kennzahl aus,
   entweder *YouTube Age-Ranges (Watch Time - Hours)* oder *YouTube-TrafficSources*
   (WICHTIG: Nutze den Link zur Liste!)

   .. image:: ../_static/youtube3.png

3. Wähle `Datei hochladen`

   .. image:: ../_static/youtube4.png

4. YouTube-Kanal auswählen
5. Entsprechende Datei auswählen und hochladen

Falls die Analytics nicht korrekt exportiert wurden, erscheint eine entsprechende
Fehlermeldung.
