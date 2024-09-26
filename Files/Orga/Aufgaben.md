# music_cog.py

## Ziel
Der Bot soll Musik von YouTube, Spotify und anderen Plattformen abspielen können. Zunächst nur YouTube, aber die anderen Plattformen sollen einfach zu implementieren sein.

**Wichtig:** Es darf nichts heruntergeladen werden.

## Funktionen
- Der Nutzer soll einzelne Videos von YouTube mit der URL oder dem normalen YouTube-Link eingeben können.
- Der Nutzer kann auch eine ganze Playlist mit dem Link zur Playlist einfügen.

## App-Commands
### Wichtig (unbedingt erstellen)
- `/play` 
  - Setzt das angegebene Lied auf die Playlist. Wenn es eine Playlist ist, sollen alle darin befindlichen Songs ausgelesen und in die Playlist gesetzt werden.
- `/playlist` 
  - Zeigt die gesamte Playlist als Discord Embed an.
- `/pause` 
  - Pausiert die Wiedergabe.
- `/resume` 
  - Setzt die Wiedergabe fort.
- `/stop` 
  - Der Bot verlässt den Voice-Channel und löscht die Playlist sowie alle dazugehörigen Daten.

### Zusatz (kann auch später implementiert werden)
- `/skip` 
  - Skipt den aktuellen Song.
- `/remove` 
  - `/remove [user]` 
    - Skipt alle Songs, die von diesem Nutzer hinzugefügt wurden, und löscht sie aus der Playlist.
  - `/remove [int]` 
    - Löscht so viele Songs aus der Playlist, wie angegeben wurden.
  - `/remove [all]` 
    - Löscht alle Songs aus der Playlist.
- `/loop` 
  - Der Nutzer darf auswählen, ob die gesamte Playlist oder nur der aktuelle Song geloopt wird.

### Zusatz (später implementieren)
- `/volume` 
  - Ändert die Lautstärke des Bots zwischen 0-200.
- `/bassboost` 
  - Erhöht den Bass zwischen 0-100.
- `/nodupe` 
  - Entfernt alle Duplikate.
- `/resetPLsets` 
  - Setzt alle Einstellungen wie Volume, Bassboost und Duplikate auf Standard zurück.
- `/shuffle` 
  - Spielt alle Songs in der Playlist in zufälliger Reihenfolge ab.
- `/invert` 
  - Spielt die Playlist rückwärts ab.
- `/back` 
  - Springt zurück und spielt den letzten Song ab.
- `/skipto` 
  - Springt zum angegebenen Song.
- `/QC` 
  - Erzeugt ein Discord Embed, mit dem man die Playlist steuern kann.
