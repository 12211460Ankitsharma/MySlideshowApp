[app]
title = WASlideshow
package.name = slideshowmaker
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Requirements: Is sequence mein likhein
requirements = python3,kivy==2.2.1,libopenssl,opencv,numpy,pyjnius,android

icon.filename = icon.png
orientation = portrait
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = armeabi-v7a, arm64-v8a

# WhatsApp Share filter
android.manifest.intent_filters = [ \
    {"action": "android.intent.action.SEND", "data": {"mimeType": "image/*"}}, \
    {"action": "android.intent.action.SEND_MULTIPLE", "data": {"mimeType": "image/*"}} \
    ]

[buildozer]
log_level = 2
warn_on_root = 1