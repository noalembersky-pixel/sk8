# sk8.oatmealmorning.com — SK8: Hell Yeah

**Rule (decided 24 Nov 2026): this website does not have the playable game.** It is a store page only:
the home page and `/get/` show the App Store and Google Play links. The game lives only inside the
iPhone and Android apps.

## What is published (the website)
| Address | File | What it is |
|---|---|---|
| `/` | `index.html` | Home page: copy of `/get/` (canonical `/`, PostHog `page: 'home'`) |
| `/get/` | `get/index.html` | Store-links page. **The apps' SHARE buttons point here — never move or delete it.** |
| `/support/` | `support/index.html` | Help page (both stores link to it) |
| `/privacy/` | `privacy/index.html` | Privacy policy (both stores link to it) |

Shared files: `site.css`, `art-skater.png`, `badge-app-store.svg`, `badge-google-play.png`,
`favicon.png`, `apple-touch-icon.png`, `preview.png`, `CNAME`.

Store switches: near the bottom of **both** `index.html` and `get/index.html`,
`const LIVE = { ios: false, android: false };` — set a store to `true` the day it is live (change both files).

## What is NOT published (the game, for the app builds)
- `_game/index.html` + `_game/cut.mp4` — the game. Folders starting with `_` are skipped by GitHub Pages,
  and `_config.yml` excludes `_game`, `tools` and this README as well. **Never add a `.nojekyll` file.**
- Make an app game file: `python3 tools/make_app_build.py android 1.7 OUT/index.html` (or `ios`).
  Copy the result plus `_game/cut.mp4` into the app project (Android: `sk8-app/app-web/`;
  iOS: `sk8-ios/www/` and `sk8-ios/ios/App/App/public/`).
- New game file from Guy: `python3 tools/merge_guy_build.py GUY_FILE.html _game`

**Never build, copy or merge the game into the repo root or any other published folder**
(no `index.html` game at the root, no `/next/`, no `/play/`, no `manifest.webmanifest`).
