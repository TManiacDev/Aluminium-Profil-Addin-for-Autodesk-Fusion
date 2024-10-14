# Multi Language Support


## Mehrsprachige Unterstützung für das Modell und die Dialoge
Das Modul "multiLanguage" bietet eine Möglichkeit der mehrsprachigen Unterstützung.

Man wählt eine Sprache wie folgt aus: _dic = translation.Language('english')
Als zweiten Parameter kann man dem Wörterbuch noch einen Pfad zu einen spezifischen Wörterbuch mit geben.
Nun kann man mit < _dic.getTranslation('Zu_Übersetzendes_Element') > die Übersetzung erhalten.
Sollte es keine Übersetzung in der Sprache geben, liefert die Funktion ein den 'Zu_Übersetzendes_Element' Text zurück. 

Aktuell wird die Sprache noch hardcodiert ausgewählt. Ich nutze noch nicht die "User-Language" von Fusion360. Meine in der Entwicklung ausgewählte Sprache ist Englisch. Das englische Wörterbuch ist auch das Referenzwörterbuch und so sind die 'Zu_Übersetzendes_Element'-Begriffe alle in Englisch.

### XML Wörterbuch
Das Wörterbuch ist in XML verfasst.
