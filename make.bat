pyinstaller -w -F --add-data "img;img" --add-data "moves;moves" --add-data "arlrdbd.ttf;." main.py
move dist\main.exe .
ren "main.exe" "AmongYsRewrite.exe"
