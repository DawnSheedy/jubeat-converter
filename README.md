## What is this

This is a script for converting game files from jubeat to a format that my [Unity application](https://github.com/DawnSheedy/unity-rhythm) can understand.

## How does it work:

Put jubeat `data/ifs_pack` contents in `input`
Put jubeat `data/d3/model/*id*.tex` files in `imagein`

Run `textureConverter.py` to extract textures.
Run `converter.py` to extract songs and create Metadata, reformat song files, and associate album art.

Import files into `unity-rhythm/Assets/Resources/SongFiles`

Select a song in-game (soon), or by setting the song on the `GameplayController` GameObject in the `GameplayScene`