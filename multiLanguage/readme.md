# Multi Language Support

Das Modul "multiLanguage" bietet eine Möglichkeit der mehrsprachigen Unterstützung.

Man erzeugt ein Sprachenobjekt (class Language) und übergibt diesem bei der Konstruktion eine Sprache wie folgt: _dic = translation.Language(fusionUserLanguage)
Als zweiten Parameter kann man dem Wörterbuch noch einen Pfad zu einen spezifischen Wörterbuch mit geben. Das macht zum Beispiel Sinn, wenn man spezifische Wörterbücher für Dialoge (Fusion: Command) hat. Hier können dann ganze "Tooltips" übersetzt sein.
Nun kann man mit < _dic.getTranslation('Zu_Übersetzendes_Element') > die Übersetzung erhalten.
Sollte es keine Übersetzung in der Sprache geben, liefert die Funktion ein den 'Zu_Übersetzendes_Element' Text zurück. So kann das englisce Wörterbuch auf die "Übersetzung" einfacher Wörter verzichten.

Aktuell wird die Sprache noch hardcodiert ausgewählt. Ich nutze noch nicht die "User-Language" von Fusion360. Meine in der Entwicklung ausgewählte Sprache ist Englisch. Das englische Wörterbuch ist auch das Referenzwörterbuch und so sind die 'Zu_Übersetzendes_Element'-Begriffe alle in Englisch.

## XML Wörterbuch
Das Wörterbuch ist in XML verfasst. Die XML Struktur ist noch selbst erklärend.
```
<dictionary name="DictionaryName" language="english" version="1.0">
    <translation name="SearchQuery"> Übersetzter Text </translation>
    <translation name="SearchQuery2">
       Ein Text mit
       mehreren Zeilen
    </translation>
</dictionary>
```

Fusion reagiert auf Multiline je nach Verwendung unterschiedlich. In Tooltips sind Einrückungen wie im Beispiel oben egal. Wird der Text in eine Textbox eingefügt, setzt Fusion die Einrückung um. Hier muss man die Absätze noch umformatieren.