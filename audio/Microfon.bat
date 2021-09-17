echo "EU EMIT MICROFON"
F:\gstreamer\1.0\msvc_x86_64\bin\gst-launch-1.0 wasapisrc device="\{0.0.1.00000000\}.\{cbdb9ef1-4061-404d-9b30-5b1388eb161a\}" ! audioconvert ! audio/x-raw, rate=48000, channels = 1, format=S16LE ! udpsink host=10.8.0.3 port=5000
