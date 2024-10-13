# Fusion Alu Profil Generator
(for english text see below)

Das ist ein Addin für Autodesk Fusion (früher Fusion360) um Alu-Profile generisch zu behandeln. Ein Alu-Profil wird als CustomFeature behandelt, damit man es später einfach editieren kann.

Die Oberfläche soll unabhängig von der konstuktiven Seite sein. Die Oberfläche wie auch die konstruktiven Elemente bekommen die mehrsprachige Unterstützung.

## 

## Mehrsprachige Unterstützung für das Modell und die Dialoge
Das Modul "model_language" bietet eine Möglichkeit der mehrsprachigen Unterstützung.
Damit das Model die Komponenten wieder findet, muss das Modell selber die Sprache in der es erstellt wurde speichern (Komponent.Attribute).
Die Übersetzung funktioniert wie eine Buchsammlung.
Man wählt eine Sprache wie folgt aus: _dic = translation.Language('english')
Nun kann man mit < _dic.getTranslation('Zu_Übersetzendes_Element', 'zuWelchenBereichGehörtDasElement') > die Übersetzung erhalten.
Sollte es keine Übersetzung in der Sprache geben, liefert die Funktion ein "unknown word xxx"  zurück. Wobei xxx ein Zähler ist.
Das 'Zu_Übersetzendes_Element' muss exakt dem Dictionary Key entsprechen. Wobei der Dictionary Name, also 'zuWelchenBereichGehörtDasElement' nicht Case sensitiv ist. Wird kein Dictionary ausgewählt, so wird im Standard Dictonary gesucht.

Aktuell wird die Sprache noch hardcodiert ausgewählt. Ich nutze noch nicht die "User-Language" von Fusion360. Meine in der Entwicklung ausgewählte Sprache ist Englisch. Das englische Wörterbuch ist auch das Referenzwörterbuch und so sind die 'Zu_Übersetzendes_Element'-Begriffe alle in Englisch.

### XML Wörterbuch
Ich möchte das Wörterbuch in XML realisieren. Es soll ein Standardwörterbuch und dann spezialisierte Wörterbücher für die jeweiligen Bereiche geben.


---------------------------------------------------
# English Readme

This is a Addin for Autodesk Fusion (formerly Fusion360) to work with aluminum profiles. The profiles are handled as CustomFeature. So it is possible to edit or switch from a profile to a different profile.




# C:\Users\ [...USER...] \AppData\Local\Autodesk\webdeploy\production\b0c303e70bd97cfdc195adab65922cfeffcb363a\Fusion\UI\FusionUI\Resources\Modeling