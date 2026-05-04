# PROJECT_RULES

## Oberstes Projektgesetz

Diese Datei ist die Hauptregel-Datei fuer das Projekt und gilt als oberstes Projektgesetz.
Sie darf spaeter nicht still umgeschrieben, gekuerzt oder ersetzt werden.
Neue Regeln duerfen nur ergaenzt werden; bestehende Regeln duerfen nicht still entfernt werden.

## 1. Projektname

Alice Wonder Nails

## 2. Erlaubter Arbeitsbereich

`C:\Users\mickh\Desktop\alice-wondernails`

## 3. Harte Ordnerregel

Alles muss innerhalb dieses Ordners stattfinden.

- Keine Arbeiten ausserhalb.
- Keine Dateiablage ausserhalb.
- Keine Scans ausserhalb.
- Keine Tests ausserhalb.
- Keine Aenderungen ausserhalb.

## 4. Arbeitsweise

- Vor jedem Arbeitsschritt zuerst `docs/PROJECT_RULES.md` lesen.
- Danach `docs/PROGRESS.md` lesen.
- Danach nur den ausdruecklich beauftragten Bereich bearbeiten.
- Nach jedem Arbeitsschritt `docs/PROGRESS.md` aktualisieren.
- Keine fertigen Bereiche beschaedigen.
- Keine stillen Architekturwechsel.
- Keine unnoetigen Frameworks einfuehren.
- Keine erfundenen Inhalte als echte Inhalte ausgeben.
- Keine rechtlichen Texte frei erfinden.
- Keine Shop-/Login-/Admin-Funktionen bauen, wenn sie nicht ausdruecklich beauftragt sind.

## 5. Dokumentationspflicht

Jeder Arbeitsschritt braucht einen Eintrag in `docs/PROGRESS.md` mit:

- Datum
- Auftrag
- Betroffene Dateien
- Was geaendert wurde
- Was getestet wurde
- Ergebnisstatus
- Offene Punkte
- Was ausdruecklich nicht geaendert wurde

## 6. Statuslogik

Jeder Arbeitsschritt endet mit einem Status:

- ROT: Nicht lauffaehig, ungeklaert oder kritischer Fehler.
- GELB: Teilweise erledigt, aber noch offen oder nicht vollstaendig getestet.
- GRUEN: Erledigt, geprueft, dokumentiert, keine bekannten Blocker.

Wenn kein GRUEN erreicht wird, muss klar dokumentiert werden, warum nicht.

## 7. Uebergaberegel

Die Dokumentation muss so geschrieben sein, dass ein Nachfolger sofort weiterarbeiten kann.

## 8. Modulregel

Jedes Modul bekommt spaeter:

- Klaren Zweck
- Eigenen Arbeitsbereich
- Klare Grenzen
- Nicht-Ziele
- Testpunkte
- Dokumentation

## 9. Sprechende Platzhalter-Regel

Generische Blindtexte wie "Lorem Ipsum" sind verboten.
Jeder Platzhalter muss klar erklaeren:

- Welcher Inhalt spaeter eingefuegt wird
- Wer den Inhalt liefern soll
- Welche Laenge/Art erwartet wird
- Ob rechtliche Pruefung noetig ist
- Ob Bildrechte/Freigabe noetig sind
- Ob der Bereich spaeter durch ein Modul ersetzt wird

Beispielformat:

`[PLATZHALTER: Kurzer Vorstellungstext fuer Alice Wonder Nails. Inhalt spaeter durch Frau/Tochter. Ton: kreativ, hochwertig, freundlich, leicht maerchenhaft. Laenge: ca. 3-5 Saetze.]`
