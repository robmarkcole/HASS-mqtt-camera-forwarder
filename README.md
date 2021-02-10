# HASS-mqtt-camera-forwarder
Custom integration which forwards a camera feed onto an MQTT topic

Add to your config:
```yaml
image_processing:
  - platform: mqtt_camera_forwarder
    mqtt_topic: hass_camera_1
    source:
    - entity_id: camera.local_file_1
```

You can create an [MQTT camera](https://www.home-assistant.io/integrations/camera.mqtt) to monitor the feed by subscribing to the same topic:
```
camera:
  - platform: mqtt
    topic: hass_camera_1
    name: mqtt_camera_1
```


## Dev references
- https://github.com/home-assistant/core/blob/dev/homeassistant/components/mqtt_eventstream/__init__.py
- https://github.com/robmarkcole/mqtt-camera-streamer/blob/master/scripts/opencv-camera-publish.py
