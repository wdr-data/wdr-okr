.. _backend:

Intelligence Layer Backend
==========================

Der Intelligence Layer nutzt ein Django-basiertes Backend.

Dieses Backend erfüllt im Wesentlichen zwei Funktionen:

* Das Anlegen und Verwalten von Datenquellen. Zum Beispiel: Das Hinzufügen einer neuen
  Podcast-Reihe oder eines neuen Instagram-Kanals.
* In manchen Fällen ist es noch nicht möglich, alle Daten automatisiert einzulesen. Das
  Backend bietet daher die Möglichkeit, entsprechende Datensätze manuell einzupflegen.

Sobald das System wie im Kapitel :ref:`installation` beschrieben gestartet ist, ist ein
Login über einen Webbrowser möglich (standardmäßig über ``http://127.0.0.1:8000/``).
