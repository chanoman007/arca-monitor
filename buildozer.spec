[app]
title = ARCA Monitor
package.name = arcamonitor
package.domain = com.grinco
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy
orientation = portrait
osx.kivy_version = 2.2.1

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a
