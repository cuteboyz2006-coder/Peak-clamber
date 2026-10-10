[app]

title = Layla
package.name = layla
package.domain = com.layla

source.dir = .
source.include_exts = py,json,txt,png,jpg,jpeg,kv,atlas,gguf

version = 1.0

requirements = python3,kivy
14p4a.branch = v2024.01.21
android.sdk_path = /usr/local/lib/android/sdk

orientation = portrait

fullscreen = 0


[buildozer]

log_level = 2

warn_on_root = 1


[app:android]

android.api = 35
android.minapi = 23

android.archs = arm64-v8a

android.accept_sdk_license = True
