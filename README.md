# Simple Ableton Music Lister
This is a simple music lister for Ableton program.

This program takes as parameter the path to the folder where all your Ableton compositions are.
It will then generate an HTML file in this folder, called _index.html_, containing all your compositions.

You can open the _index.html_ file with your favourite browser (tested for Chrome type browser only).

Keep in mind that:
- Folder path must be set inside `music_lister.py`, top of the file
- Each _.als_ file must have a _.txt_ file with the same name next to it
  - Example: _Compo1.als_ --> _Compo1.txt_
- The text file must have the following content:
```
artist: Me
name: The Flower
album:
status:
Voice needs to be recorded again
Guitar is not loud enough
lyrics:
extra_info:
chords: (barred) G C Am F
```
  - If status is set to Finished or Complete, it will be considered Finished. Any other text will be considered in "To Rework" state
- If a wav file is exported next to txt and als files, with same name, it will be listenable directly on the HTML page

Happy composing!
