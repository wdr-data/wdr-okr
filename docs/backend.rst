.. _backend:

Intelligence Layer Backend
==========================

Der Intelligence Layer nutzt ein Django-basiertes Backend.

Dieses Backend erfüllt im Wesentlichen zwei Funktionen:

* **Anlegen und Verwalten von Datenquellen**: Zum Beispiel das Hinzufügen einer neuen
  Podcast-Reihe oder eines neuen Instagram-Kanals.

* **Manuelles Einpflegen von zusätzlichen Daten**: Für manche
  :ref:`Youtube-Daten <backend_youtube>` sowie für
  Daten zu :ref:`Instagram Collaborations <backend_instagram>` müssen Daten noch manuell
  angelegt werden.

Details zu den einzelnen Formularen des Backends befinden sich in der
:ref:`modules` im Abschnitten :class:`okr.admin`.

.. toctree::
    :maxdepth: 2
    :hidden:

    backend/backend_youtube
    backend/backend_instagram_collaborations
