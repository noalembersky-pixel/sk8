#!/usr/bin/env python3
"""Turn a game file from Guy (his Claude artifact, one big HTML) into the web build.

Usage:  python3 tools/merge_guy_build.py GUY_FILE.html OUT_DIR

Writes OUT_DIR/index.html and OUT_DIR/cut.mp4. Every change below is a small,
exact text replacement; if Guy's code changed so that one no longer matches,
the script stops and says which one, instead of guessing.

What it adds on top of Guy's game:
  - page title, description, link previews, icon, home-screen manifest
  - LOADING... screen while the 12 MB of art loads
  - PostHog analytics (cookieless) with the level on every event
  - title screen: level select (1 STREET / 2 DOWNTOWN / 3 HELL, locked until earned,
    best score under each), FEEDBACK link, CREDITS card
  - SHARE on win and game-over cards, MENU on the game-over card
  - the cutscene video moved to its own file (cut.mp4), loaded only near level 3
  - debug hook window.__sk8 removed
  - level 2 (Downtown): unlimited tries instead of "5 tries, then back to level 1"
"""
import base64, re, sys, pathlib

src_path, out_dir = sys.argv[1], pathlib.Path(sys.argv[2])
s = open(src_path, encoding='utf-8').read()
out_dir.mkdir(parents=True, exist_ok=True)


def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'STOP: expected {count} match(es), found {n}, for:\n  {old[:140]!r}')
    s = s.replace(old, new)


FEEDBACK = 'https://docs.google.com/forms/d/1rqOcjfHyTOeX9mM_i9ZZ_TgRlVdkYwGYjRxxUn7pfC8/viewform'
PH_KEY = 'phc_qo4wiAUHZxUNwLi2nGGmHVEUX4cZxUcMNEMy5vxG6jBW'

# ---------- 1. cutscene video -> its own file ----------
m = re.search(r'const CUT_SRC="data:video/mp4;base64,([A-Za-z0-9+/=]+)";', s)
if not m:
    sys.exit('STOP: cutscene video (CUT_SRC) not found')
(out_dir / 'cut.mp4').write_bytes(base64.b64decode(m.group(1)))
s = s[:m.start()] + 'const CUT_SRC="cut.mp4";' + s[m.end():]
# both places that turned the embedded video into a playable address now use the file directly
blob = "const bin = atob(CUT_SRC.slice(CUT_SRC.indexOf(',') + 1)), u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); cutURL = URL.createObjectURL(new Blob([u8], { type: 'video/mp4' }));"
sub(blob, 'cutURL = new URL(CUT_SRC, location.href).href;', count=2)

# ---------- 2. page head ----------
sub('<title>SK8</title>', '''<title>SK8 — a tiny skateboarding game</title>
<meta name="description" content="Kick, ollie, flip and grind through three levels: the street, downtown, and hell. Free to play in your browser, made for phones.">
<meta property="og:title" content="SK8 — a tiny skateboarding game">
<meta property="og:description" content="Kick, ollie, flip and grind through three levels. Free, plays in your browser.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://sk8.oatmealmorning.com/">
<meta property="og:image" content="https://sk8.oatmealmorning.com/preview.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="SK8">''')

# ---------- 3. loading screen ----------
sub('<div id="app">', '<div id="loading" style="position:fixed;inset:0;display:grid;place-items:center;background:#1d1530;color:#b9b2ff;font:700 14px/1.4 system-ui,sans-serif;letter-spacing:.1em;z-index:60">LOADING…</div>\n<div id="app">')

# ---------- 4. extra styles ----------
sub('</style>', '''
/* web build additions: level select, links, credits */
.lvls { display: flex; gap: 10px; flex-wrap: wrap; }
#title .lvls .cta { font-size: 17px; padding: 8px 14px; display: flex; flex-direction: column; align-items: center; line-height: 1.05; }
.lvls .cta small { font: 800 10px var(--ui); letter-spacing: 0.08em; margin-top: 3px; opacity: 0.8; }
.lvls .cta.locked { background: #4a4360; color: #b9b2ff; box-shadow: 0 6px 0 var(--ink); }
.links { font-size: 12px; letter-spacing: 0.08em; display: flex; gap: 16px; }
.links a, .links button { color: var(--mint); background: none; border: 0; padding: 0; font: inherit; letter-spacing: inherit; cursor: pointer; text-decoration: none; border-bottom: 1px solid currentColor; }
#credits .how { grid-template-columns: auto 1fr; }
#over .row .cta, #win .row .cta { font-size: 17px; padding: 10px 18px; } #over .row .ghost, #win .row .ghost { font-size: 14px; padding: 10px 14px; }
@media (max-height: 400px) { #title .lvls .cta { font-size: 14px; padding: 6px 10px; } }
</style>''', count=1)

# ---------- 5. title screen: level select + links ----------
sub('<div class="row"><button class="cta" id="btnStart">START</button><button class="cta" id="btnLevel2" type="button" hidden>LEVEL 2</button><button class="cta ghost snd" id="btnSound" type="button">SOUND ON</button></div>',
    '<div class="row lvls"><button class="cta" id="btnStart" type="button">1 STREET<small id="lb1">START HERE</small></button><button class="cta" id="btnL2" type="button">2 DOWNTOWN<small id="lb2"></small></button><button class="cta" id="btnL3" type="button">3 HELL<small id="lb3"></small></button></div>'
    '<button class="cta" id="btnLevel2" type="button" hidden>LEVEL 2</button><button class="cta ghost snd" id="btnSound" type="button">SOUND ON</button>'
    f'<div class="links"><a id="fbLink" href="{FEEDBACK}" target="_blank" rel="noopener">FEEDBACK</a><button id="btnCredits" type="button">CREDITS</button></div>')

# ---------- 6. share / menu buttons ----------
sub('<button class="cta" id="btnAgain">RIDE AGAIN</button>',
    '<div class="row"><button class="cta" id="btnAgain">RIDE AGAIN</button><button class="cta ghost" type="button" id="btnShareOver">SHARE</button><button class="cta ghost" type="button" id="btnMenuOver">MENU</button></div>')
sub('<button class="cta" id="btnNext" type="button">LEVEL 2 ▶</button></div>',
    '<button class="cta" id="btnNext" type="button">LEVEL 2 ▶</button><button class="cta ghost" type="button" id="btnShareWin">SHARE</button></div>')

# ---------- 7. credits card ----------
sub('<section class="ov" id="pause" hidden>', '''<section class="ov" id="credits" hidden>
    <div class="card">
      <h1>SK<span>8</span></h1>
      <div class="how">
        <b>GAME + ART</b><span>Guy</span>
        <b>PUBLISHED BY</b><span>Oatmeal Morning</span>
        <b>FONTS</b><span>Rubik, Rubik Wet Paint (SIL Open Font License)</span>
        <b>HELP</b><span>sk8.oatmealmorning.com/support</span>
      </div>
      <div class="row"><button class="cta ghost" id="btnCreditsBack" type="button">BACK</button></div>
    </div>
  </section>

  <section class="ov" id="pause" hidden>''')
sub("['title', 'over', 'pause', 'win', 'how2', 'how3', 'how4', 'cut']", "['title', 'over', 'pause', 'win', 'how2', 'how3', 'how4', 'cut', 'credits']")

# ---------- 8. analytics ----------
sub('<script>\nconst ASSET_SRC=', '''<script>
/* ---- analytics (PostHog, cookieless, no autocapture, no recordings) ---- */
const PH_KEY = '%s';
window.track = function(){};
if (PH_KEY) {
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group identify setPersonProperties alias".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
  posthog.init(PH_KEY, { api_host: 'https://us.i.posthog.com', persistence: 'memory', capture_pageview: true, autocapture: false, disable_session_recording: true }); posthog.register({ app: 'sk8', build: '3-levels' });try{if(location.search.indexOf('tester=1')>-1)localStorage.setItem('om-tester','1');if(localStorage.getItem('om-tester')==='1')posthog.register({is_internal:true})}catch(e){};
  window.track = (ev, props) => { try { posthog.capture(ev, props); } catch (e) {} };
}
</script>
<script>
const ASSET_SRC=''' % PH_KEY)

# internal level numbers: 1 street, 4 downtown (shown as level 2), 3 hell, 2 = archived vert level
sub("function startGame(lvl) {", "const pubLevel = l => l === 4 ? 2 : l === 3 ? 3 : l === 2 ? 'vert' : 1;\nfunction startGame(lvl) {")
sub("zoom.x = 1; zoom.v = 0; slowmo = 0; mode = 'play'; paused = false; show(null); setMusic(false, true); setMusic(true);\n}",
    "zoom.x = 1; zoom.v = 0; slowmo = 0; mode = 'play'; paused = false; show(null); setMusic(false, true); setMusic(true);\n  track('game_start', { level: pubLevel(lvl), muted, touch: 'ontouchstart' in window });\n}")
# level 1 and 3 win / game over
sub("  if (L3) { $('wTitle').innerHTML = 'HELL<br>ESCAPED!';",
    "  track('level_win', { level: L3 ? 3 : 1, score, seconds: sec, stomps: stats.kids, best_trick: stats.best || '' });\n  if (L3) { $('wTitle').innerHTML = 'HELL<br>ESCAPED!';")
sub("  $('oHead').textContent = L3 ? 'EATEN!' : 'SMOKED!';",
    "  $('oHead').textContent = L3 ? 'EATEN!' : 'SMOKED!';\n  track('game_over', { level: L3 ? 3 : 1, score, distance_m: Math.floor(dist()), seconds: Math.round(tPlay), stomps: stats.kids, best_trick: stats.best || '' });")
# level 2 (downtown) win / fail
sub("  $('wTitle').innerHTML = 'LEVEL 2<br>CLEARED!';",
    "  $('wTitle').innerHTML = 'LEVEL 2<br>CLEARED!';\n  track('level_win', { level: 2, score, seconds: Math.round(tPlay), manholes: D4.holes, stair_sets: D4.sets, best_trick: stats.best || '' });")
sub("  $('oScore').textContent = D4.holes + ' / ' + V4.TARGET; $('oBest').textContent = 'MANHOLES';",
    "  $('oScore').textContent = D4.holes + ' / ' + V4.TARGET; $('oBest').textContent = 'MANHOLES';\n  track('game_over', { level: 2, score, seconds: Math.round(tPlay), manholes: D4.holes, stair_sets: D4.sets, tries_used: l2Fails, best_trick: stats.best || '' });")
sub("function playCut() {", "function playCut() {\n  track('cutscene_start', {});")
sub("$('btnSkip').onclick = done;", "$('btnSkip').onclick = () => { track('cutscene_skip', { at_s: Math.round(v.currentTime || 0) }); done(); };")

# ---------- 8b. level 2: unlimited tries (Noa, 28 Oct) ----------
# Guy's rule sent you back to level 1 after 5 failed tries, but with the level select
# level 2 stays unlocked, so the penalty looked like a bug. Only showFail4 (Downtown) changes.
a = s.find('function showFail4() {'); z = s.find('\n}\n', a)
if a < 0 or z < 0:
    sys.exit('STOP: showFail4 not found')
body = s[a:z]
for old, new in [("const out = l2Fails >= 5;", "const out = false;   // web build: unlimited tries"),
                 ("$('oTitle').textContent = out ? 'OUT OF TRIES' : \"TIME'S UP · \" + (5 - l2Fails) + (5 - l2Fails === 1 ? ' TRY LEFT' : ' TRIES LEFT');",
                  "$('oTitle').textContent = \"TIME'S UP\";")]:
    if body.count(old) != 1:
        sys.exit(f'STOP: level 2 tries rule changed in showFail4: {old[:60]!r}')
    body = body.replace(old, new)
s = s[:a] + body + s[z:]

# ---------- 9. level select, share, menu, credits wiring; remove debug hook ----------
m = re.search(r"window\.__sk8 = \{.*?\};\n", s)
if not m:
    sys.exit('STOP: debug hook window.__sk8 not found')
s = s[:m.start()] + s[m.end():]

sub("$('tBest').textContent = getBest() ? 'BEST ' + getBest().toLocaleString('en-US') : '';", r"""$('tBest').textContent = '';
// ---- level select (web build) ----
const unlocked = n => { try { return localStorage.getItem('sk8-l' + n) === '1'; } catch (e) { return false; } };
const bestOf = k => { try { return +localStorage.getItem(k) || 0; } catch (e) { return 0; } };
function paintLevels() {
  const b1 = getBest(), b2 = bestOf('sk8-best-l2b'), b3 = getBest3();
  $('lb1').textContent = b1 ? 'BEST ' + b1.toLocaleString('en-US') : 'START HERE';
  [[2, 'btnL2', 'lb2', b2], [3, 'btnL3', 'lb3', b3]].forEach(([n, id, lb, b]) => {
    const open = unlocked(n); $(id).classList.toggle('locked', !open);
    $(lb).textContent = !open ? '🔒 LOCKED' : b ? 'BEST ' + b.toLocaleString('en-US') : 'UNLOCKED';
  });
  $('tBest').textContent = '';
}
function lockedTap(n) {
  $('tBest').textContent = 'FINISH LEVEL ' + (n - 1) + ' TO UNLOCK LEVEL ' + n;
  track('locked_level_tap', { level: n });
}
$('btnL2').addEventListener('click', () => { if (!unlocked(2)) return lockedTap(2); initAudio(); newGame(4); mode = 'win'; show('how4'); });
$('btnL3').addEventListener('click', () => { if (!unlocked(3)) return lockedTap(3); initAudio(); newGame(3); mode = 'win'; setTimeout(prepCut, 50); show('how3'); });
const _show = show; show = id => { _show(id); if (id === 'title') paintLevels(); };
$('btnMenuOver').addEventListener('click', () => { delete $('btnAgain').dataset.lvl; $('btnAgain').textContent = 'RIDE AGAIN'; l2Fails = 0; level = 1; newGame(); mode = 'title'; quietLoops(); setMusic(false, true); show('title'); });
$('btnCredits').addEventListener('click', () => { show('credits'); track('credits_open', {}); });
$('btnCreditsBack').addEventListener('click', () => show('title'));
$('fbLink').addEventListener('click', () => track('feedback_click', {}));
async function shareScore(where) {
  const won = where === 'win', n = pubLevel(level), pts = score.toLocaleString('en-US');
  const text = won ? (n === 3 ? `I escaped hell in SK8 with ${pts} points. Beat me:` : `I shredded Level ${n} of SK8 with ${pts} points. Beat me:`)
                   : `I got ${pts} points on Level ${n} of SK8. Beat me:`;
  const url = 'https://sk8.oatmealmorning.com/';
  const btn = $(won ? 'btnShareWin' : 'btnShareOver');
  track('share_click', { where, level: n, score });
  try {
    if (navigator.share) { await navigator.share({ title: 'SK8', text, url }); return; }
    await navigator.clipboard.writeText(text + ' ' + url);
    const old = btn.textContent; btn.textContent = 'LINK COPIED'; setTimeout(() => { btn.textContent = old; }, 1600);
  } catch (e) {}
}
$('btnShareWin').addEventListener('click', () => shareScore('win'));
$('btnShareOver').addEventListener('click', () => shareScore('over'));
paintLevels();""")
# show is declared with `function show`, so it can be reassigned above; remove the loading screen once art is ready
sub("  requestAnimationFrame(frame);\n});\n})();", "  const ld = document.getElementById('loading'); if (ld) ld.remove();\n  requestAnimationFrame(frame);\n});\n})();")

(out_dir / 'index.html').write_text(s, encoding='utf-8')
print('ok:', out_dir / 'index.html', round(len(s.encode()) / 1e6, 2), 'MB;', out_dir / 'cut.mp4', round((out_dir / 'cut.mp4').stat().st_size / 1e6, 2), 'MB')
