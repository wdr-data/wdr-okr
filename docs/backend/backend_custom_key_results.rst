.. _backend_custom_key_results:

Manuelle Kennzahlen
===================

Zusätzlich zu den automatisiert abgerufenen Daten ist es im Intelligence Layer auch
möglich, eigene Kennzahlen manuell anzulegen und Ergebnisse für die Kennzahlen zu
speichern.

Diese Kennzahlen sind jeweils einem der Produkte des Newsroom zugeordnet und können
entweder ein Zahlenwert oder ein Text sein.

.. _backend_custom_key_results_kennzahlen_definieren:

Manuelle Kennzahlen definieren
------------------------------

Bevor für eine Kennzahl im Intelligence Layer Daten gespeichert werden können, muss die
Kennzahl zunächst definiert werden:

1. Melde dich im Backend des OKR Intelligence Layer (Django) an.
2. Wähle in der Liste *OKR - Objectives and Key Results* den Eintrag
   *Manuelle Kennzahl-Definitionen* aus.
3. Klicke rechts oben auf *Manuelle Kennzahl-Definition hinzufügen*.
4. Wähle im Dropdown-Feld *Produkt-Typ* eines der angebotenen Produkte aus
   (z.B. "Podcast")
5. Gib im Feld *Produkt-Name* einen Namen für das Produkt ein, für das du eine Kennzahl
   definieren möchtest (z.B. "0630 by WDR aktuell").
6. Gib im Feld *Kennzahl* eine Bezeichnung für die Kennzahl ein, die du definieren
   möchtest (z.B. "Anzahl Nachrichten pro Woche").
7. Im Feld *Beschreibung* kannst du eine Beschreibung für die Kennzahl eingeben. (z.B.
   "Anzahl der Zuschriften von Hörer*innen, die uns in einer Woche erreicht haben").
   Dieses Feld ist optional, kann also auch leer bleiben.
8. Lege im Feld *Kennzahlen-Typ* fest, ob du für diese Kennzahl einen Zahlenwert oder
   einen Text erfassen möchtest.
9. Klicke zum Abschluss auf *Sichern*.

Daten für manuelle Kennzahlen erfassen
--------------------------------------

Nachdem du eine
:ref:`Kennzahl definiert hast <backend_custom_key_results_kennzahlen_definieren>`,
kannst du Daten für diese Kennzahl erfassen:

1. Melde dich im Backend des OKR Intelligence Layer (Django) an.
2. Wähle in der Liste *OKR - Objectives and Key Results* den Eintrag
   *Manuelle Kennzahlen* aus.
3. Klicke rechts oben auf *Manuelle Kennzahl hinzufügen*.
4. Wähle in der Liste *Kennzahl* die manuell angelegte Kennzahl an, für die du Daten
   erfassen möchtest.
5. Gib im Feld *Datum des Eintrags* das Datum an, für das du Daten erfassen möchtest.
   Klicke auf das Wort "Heute", um automatisch das aktuelle Datum einzutragen.
6. Trage den Wert der Kennzahl in das Feld *Wert* ein. Dieses Feld erwartet je nach
   ausgewählter Kennzahl entweder eine Zahl oder einen Text.
7. Bei Bedarf kannst du zusätzlich einen Text in das Feld *Notiz* eintragen.
8. Klicke zum Abschluss auf *Sichern*.
