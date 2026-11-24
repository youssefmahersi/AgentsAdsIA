#!/bin/zsh
# Crée l'appli « Lecteur AgentsAds » sur le Bureau, avec son icône.
emulate -L zsh
DOSSIER="${0:A:h}"
APP="$HOME/Desktop/Lecteur AgentsAds.app"
TMP=$(mktemp -d)
LANCEUR="$DOSSIER/lancer.sh"
cat > "$TMP/script.applescript" <<OSA
set lanceur to quoted form of "$LANCEUR"
set etat to do shell script "zsh " & lanceur & " tourne"
if etat is "oui" then
	set r to button returned of (display dialog "Le lecteur est déjà ouvert." buttons {"Arrêter", "Ouvrir"} default button "Ouvrir" with title "Lecteur AgentsAds")
	if r is "Arrêter" then
		do shell script "zsh " & lanceur & " arreter"
		display notification "Le lecteur est arrêté." with title "Lecteur AgentsAds"
		return
	end if
end if
try
	do shell script "zsh " & lanceur & " ouvrir"
on error msg
	display dialog "Le lecteur n'a pas démarré : " & msg buttons {"OK"} default button "OK" with title "Lecteur AgentsAds"
end try
OSA
rm -rf "$APP"
osacompile -o "$APP" "$TMP/script.applescript" || exit 1
set="$TMP/icone.iconset"; mkdir -p "$set"
for t in 16 32 128 256 512; do
  sips -z $t $t "$DOSSIER/icone-1024.png" --out "$set/icon_${t}x${t}.png" >/dev/null
  sips -z $((t*2)) $((t*2)) "$DOSSIER/icone-1024.png" --out "$set/icon_${t}x${t}@2x.png" >/dev/null
done
iconutil -c icns "$set" -o "$APP/Contents/Resources/applet.icns"
rm -f "$APP/Contents/Resources/Assets.car"
plutil -remove CFBundleIconName "$APP/Contents/Info.plist" 2>/dev/null
plutil -replace CFBundleIconFile -string applet "$APP/Contents/Info.plist"
codesign --force --deep -s - "$APP" 2>/dev/null
touch "$APP"
rm -rf "$TMP"
echo "Créée : $APP"
