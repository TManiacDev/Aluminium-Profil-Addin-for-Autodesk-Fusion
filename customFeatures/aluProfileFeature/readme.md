# Alu Profile CustomFeature
(my language is German for English text see below)

Das [CustomFeature](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-FA7EF128-1DE0-4115-89A3-795551E2DEF2) benötigt zwei Command-Dialoge, einen für die Generierung des Features und einen zum Editieren. Von der Oberfläche sollten beide gleich sein.

Das CustomFeature wird einige Daten als Parameter speichern. Gerade bei den Abmaßen sollte man dann schauen wie gut da auf eine Änderung reagiert werden kann. In der Regel ändert sich bei den Abmaßen auch die Form.

Es gibt neben der generischen Form auch eine dxf-Unterstützung. Hier wird man später einen Profile Manager benötigen um Profile zu laden.

## Aktueller Stand und so
Der Create Dialog funktioniert und man kann ein einfaches Profil erzeugen.

'One Side' und 'Symetric' sind ok. Es fehlt noch die Umsetzung für 'Two Sides" und negative Eingaben bei Distance.

Bei jedem Refresh des Previews wird das dxf neu geladen. Das Laden der dxf kostet viel Zeit. 
Hier muss ich unbedingt etwas Ändern, dass das dxf nur beim Profilwechsel geladen wird.

Noch braucht es für die Skizze eine leer Ebene. Fusion erkennt als Profil auch Kanten welche auf der darunter liegenen Fläche sind. Damit wird die Profilkontur unterbrochen und es braucht etwas besseres um die Extrusion auszuführen.

## Commands
Mit 'Select Plane' und 'Select Pivot Point' wird der Ausgangspunkt des Profiles ausgewählt. Erst wenn beide ausgewählt sind wird ein Preview erzeugt.

Die Typen "Generic" und "None" machen aktuell das Gleiche. Sie erzeugen ein einfaches Profil bei dem man die Größe auswählen kann.
Die generische Form ist noch recht unflexibel. Der Slot ist in einer "config"-Klasse fest verankert. Hier darf gerne eine komplett generische Formklasse geschaffen werden. Die Abmaße der Form lassen sich schon frei variieren.

Die Herstellerbibliothek enthält ein paar Beispiele der Hersteller [Motedis](https://www.motedis.com) und [Minitec](https://www.minitec.de) um zu zeigen wie der SVG Support funktioniert. Die SVGs welche enthalten sind, habe ich aus den öffentlich zugänglichen Step-Dateien erzeugt. Das Copyright der Formen obliegt den jeweiligen Herstellern.

Die Profillänge (Distance) lässt sich wie von der Extrusion gewohnt per Eingabe oder Griff einstellen. Es gibt noch keine "bis zu.." Funktion.


Neuer Körper und Neue Komponente funktionieren wie auch bei den sonstigen Operationen in Fusion. Die erzeugten Objekte sind ganz normale Solids. Man hat unmittelbaren Zugriff auf die Skizze und die Extrusion.

Neues Feature erzeugt das Profil als Profil-Feature (customFeature). 
Damit erhält man die Möglichkeit das Aluminiumprofil als Einheit zu editieren. Man kann einfach ein Profil gegen ein anderes austauschen.
Auch spätere gerenerierte Verbinder lassen sich nur über dieses Feature handhaben.
## manageFeature.py


--------------------------
# English Text

This is the [CustomFeature](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-FA7EF128-1DE0-4115-89A3-795551E2DEF2) thats managed all construction things around a profile.

## At Starting the CustomFeature

The CustomFeature needs two commands, one to create the feature and one to edit the feature