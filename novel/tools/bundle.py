# Makes story/fallback.js so the game also runs when index.html is double clicked (file://, where fetch() is blocked).
# Normal use (server / GitHub Pages / the XP desktop) reads story/*.txt and story/choices.json directly. Re-run after editing the story.
import glob, json, os
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "story")
files = {"story/" + os.path.basename(f): open(f, encoding="utf-8").read() for f in sorted(glob.glob(d + "/*.txt") + glob.glob(d + "/*.json"))}
open(d + "/fallback.js", "w", encoding="utf-8").write("window.STORY_FALLBACK=" + json.dumps(files, ensure_ascii=False) + ";")
