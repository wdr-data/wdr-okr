.. _backend:

OKR Data Warehouse Backend
==========================

Das OKR Data Warehouse nutzt ein Django-basiertes Backend.

Dieses Backend erfüllt im Wesentlichen zwei Funktionen:

* **Anlegen und Verwalten von Datenquellen**: Zum Beispiel das Hinzufügen einer neuen
  Podcast-Reihe oder eines neuen Instagram-Kanals. Dazu zählt auch das
  :ref:`manuelle Anlegen und Zuweisen von Kategorien für Podcasts<backend_categories>`.

* **Manuelles Einpflegen von zusätzlichen Daten**: Für manche
  :ref:`YouTube-Daten <backend_youtube>` müssen Daten noch manuell
  angelegt werden. Darüber hinaus ist es möglich, mit dem Data Warehouse Backend
  :ref:`manuelle Kennzahlen anzulegen und zu pflegen <backend_custom_key_results>`.

.. seealso::
   Details zu den einzelnen Formularen des Backends befinden sich in der
   :ref:`modules` im Abschnitten :class:`okr.admin`.

.. toctree::
    :maxdepth: 2
    :hidden:

    backend/backend_custom_key_results
    backend/backend_categories
    backend/backend_youtube
