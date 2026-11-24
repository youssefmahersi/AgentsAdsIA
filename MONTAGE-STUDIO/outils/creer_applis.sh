#!/bin/zsh
# Crée les deux applis à double-cliquer sur le Bureau : « Studio Ads » et « Studio Ads – Téléphone ».
emulate -L zsh
DOSSIER="${0:A:h:h}"
BUREAU="$HOME/Desktop"
TMP=$(mktemp -d)
LANCEUR="$DOSSIER/lancer.sh"

icns() {  # $1 = png 1024, $2 = sortie .icns
  local set="$TMP/icone.iconset"; rm -rf "$set"; mkdir -p "$set"
  for t in 16 32 128 256 512; do
    sips -z $t $t "$1" --out "$set/icon_${t}x${t}.png" >/dev/null
    sips -z $((t*2)) $((t*2)) "$1" --out "$set/icon_${t}x${t}@2x.png" >/dev/null
  done
  iconutil -c icns "$set" -o "$2"
}

appli() {  # $1 = nom, $2 = script AppleScript, $3 = png
  local app="$BUREAU/$1.app"
  rm -rf "$app"
  print -r -- "$2" > "$TMP/script.applescript"
  osacompile -o "$app" "$TMP/script.applescript" || return 1
  icns "$3" "$app/Contents/Resources/applet.icns"
  rm -f "$app/Contents/Resources/Assets.car"
  plutil -remove CFBundleIconName "$app/Contents/Info.plist" 2>/dev/null
  plutil -replace CFBundleIconFile -string applet "$app/Contents/Info.plist"
  codesign --force --deep -s - "$app" 2>/dev/null
  touch "$app"
  echo "Créée : $app"
}

Q="quoted form of \"$LANCEUR\""

appli "Studio Ads" "
set lanceur to $Q
set etat to do shell script \"zsh \" & lanceur & \" tourne\"
if etat is \"oui\" then
	set r to button returned of (display dialog \"Studio Ads est déjà ouvert.\" buttons {\"Arrêter\", \"Ouvrir\"} default button \"Ouvrir\" with title \"Studio Ads\")
	if r is \"Arrêter\" then
		try
			do shell script \"zsh \" & lanceur & \" arreter\"
			display notification \"Studio Ads est arrêté.\" with title \"Studio Ads\"
		on error msg
			display dialog msg buttons {\"OK\"} default button \"OK\" with title \"Studio Ads\"
		end try
	else
		open location \"http://127.0.0.1:7880/\"
	end if
else
	try
		do shell script \"zsh \" & lanceur & \" mac\"
	on error msg
		display dialog \"Le studio n'a pas démarré : \" & msg buttons {\"OK\"} default button \"OK\" with title \"Studio Ads\"
	end try
end if
" "$DOSSIER/web/icones/icone-1024.png"

appli "Studio Ads – Téléphone" "
set lanceur to $Q
set etat to do shell script \"zsh \" & lanceur & \" etat\"
if etat contains \"mode iphone\" then
	set r to button returned of (display dialog \"Studio Ads tourne déjà en mode téléphone.\" buttons {\"Arrêter\", \"Voir l'adresse\", \"Ouvrir\"} default button \"Voir l'adresse\" with title \"Studio Ads – Téléphone\")
	if r is \"Arrêter\" then
		try
			do shell script \"zsh \" & lanceur & \" arreter\"
			display notification \"Studio Ads est arrêté.\" with title \"Studio Ads\"
		on error msg
			display dialog msg buttons {\"OK\"} default button \"OK\" with title \"Studio Ads\"
		end try
		return
	else if r is \"Ouvrir\" then
		open location \"http://127.0.0.1:7880/\"
		return
	end if
else
	try
		do shell script \"zsh \" & lanceur & \" iphone\"
	on error msg
		display dialog \"Le studio n'a pas démarré : \" & msg buttons {\"OK\"} default button \"OK\" with title \"Studio Ads\"
		return
	end try
end if
set infos to do shell script \"zsh \" & lanceur & \" adresse\"
set AppleScript's text item delimiters to \"|\"
set adresse to text item 1 of infos
set code to text item 2 of infos
set AppleScript's text item delimiters to \"\"
display dialog \"Sur ton téléphone, connecté au même Wi-Fi, ouvre :\" & return & return & adresse & return & return & \"Code d'accès : \" & code buttons {\"OK\"} default button \"OK\" with title \"Studio Ads – Téléphone\"
" "$DOSSIER/web/icones/icone-telephone-1024.png"

rm -rf "$TMP"
