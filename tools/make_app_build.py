#!/usr/bin/env python3
"""Make the game file for an app build (Android or iOS) from index.html.

Usage:  python3 tools/make_app_build.py android 1.5 OUT/index.html

The only difference from the web game is one line: SK8_BUILD gets the platform
and the app version. That switches on the random returning-player ID (app builds
only) and tags every analytics event with platform and app_version.
The version must match versionName in android/app/build.gradle.
"""
import hashlib, os, re, sys

WEB_LINE = "const SK8_BUILD = { platform: 'web', version: '' };"

def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ('android', 'ios') or not re.fullmatch(r'\d+\.\d+(\.\d+)?', sys.argv[2]):
        sys.exit(__doc__)
    platform, version, out = sys.argv[1:]
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
    data = open(src, 'rb').read()
    old = WEB_LINE.encode()
    if data.count(old) != 1:
        sys.exit('STOP: expected exactly one SK8_BUILD line in index.html, found %d' % data.count(old))
    new = ("const SK8_BUILD = { platform: '%s', version: '%s' };" % (platform, version)).encode()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'wb').write(data.replace(old, new))
    print('Wrote %s  (%s %s, %d bytes, md5 %s)' % (out, platform, version, len(data) - len(old) + len(new), hashlib.md5(data.replace(old, new)).hexdigest()))

if __name__ == '__main__':
    main()
