ミカ.exe (PC-98 style novel + Windows XP puzzle). Opens from the "ミカ.exe" desktop icon in windows-xp.html.
Standalone: novel/index.html works from a server, GitHub Pages, or double click (story/fallback.js), but the XP tasks (Notepad, Task Manager, Network) only exist inside windows-xp.html.
Edit story/*.txt and story/choices.json, then run: python3 novel/tools/bundle.py (only needed for double click use).
Lines: Japanese | English   Commands: @bg dusk|dawn|black  @face default|smile|happy|sad|angry|none  @hot 1|0  @wave  @pause ms
  @fx shake|glitch|hush|takeover|errors|bsod|floppy   @do key | JA hint | EN hint (waits until the player finishes the XP task: notepad, taskmgr, network)
  @choice id  @goto scene  @end | JA title | EN title
Animation: her glasses stay on in every frame. face_<k>_blink / _wave1 / _wave2 / _glint are built by tools/make_anim.py from the base sprites.
Art: sprites are girlB from "VN Sprite Pack by onboroo", converted by tools/make_assets.py. Font: DotGothic16 (SIL OFL).
