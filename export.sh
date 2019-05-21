#!/bin/sh
# set -x
VERSION=`cat VERSION`
DIR="/data/www/html/software/downloads/Galaxy/$VERSION/WinPulsar"
FORCE=0
if [ "$1" = "-F" ]; then
  FORCE=1
fi
if [ -d "$DIR" -a "$FORCE" = "0" ]; then
  echo "Version $VERSION already exported, please increment version..."
  exit 1
fi
if [ -d "$DIR" ]; then
  rm -rf "$DIR"
fi

mkdir -p "$DIR"
ZF="$DIR/WinPulsar.zip"
BS="$DIR/bootstrap.exe"
BS2="/tmp/bootstrap.zip"
find . -name "*~" -exec rm -f "{}" \;
rm -f "$BS" "$BS2" "$ZF"
zip -r "$BS2" bootstrap
cat etc/unzipsfx.exe "$BS2" > "$BS"
zip -A "$BS"
rm -f "$BS2"
rm -f WinPulsar/extra.zip
( cd extra; zip -r ../WinPulsar/extra.zip * .venv )
( cd WinPulsar; zip -r "$ZF" * )
cp pulsar-0.7.3-patched.zip python-2.7.13.amd64.msi "$DIR"
chmod +r "$DIR"/*

echo "Folder: $DIR"
ls -l "$DIR"
