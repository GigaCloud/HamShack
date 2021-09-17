echo "EU EMIT SUNET DE SISTEM"

F:\gstreamer\1.0\msvc_x86_64\bin\gst-launch-1.0 wasapisrc ! audioconvert ! audio/x-raw, rate=48000, channels = 1, format=S16LE ! udpsink host=10.8.0.1 port=5000
