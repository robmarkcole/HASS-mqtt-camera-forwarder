"""
Platform that will perform object detection.
"""
from collections import namedtuple, Counter
import io
import logging

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components.image_processing import (
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_SOURCE,
    DOMAIN,
    PLATFORM_SCHEMA,
    ImageProcessingEntity,
)
from homeassistant.components import mqtt
from homeassistant.const import ATTR_ENTITY_ID, ATTR_NAME
from homeassistant.core import split_entity_id

_LOGGER = logging.getLogger(__name__)

EVENT_FRAME_SENT = "mqtt_camera_forwarder.frame_sent"
CONF_MQTT_TOPIC = "mqtt_topic"
DEFAULT_MQTT_TOPIC = "hass_camera"
MQTT_QOS = 0

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_MQTT_TOPIC, default=DEFAULT_MQTT_TOPIC): cv.string,
    }
)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up."""

    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(
            MqttCameraForwarder(
                hass,
                mqtt_topic = config.get(CONF_MQTT_TOPIC),
                camera_entity=camera.get(CONF_ENTITY_ID),
                name=camera.get(CONF_NAME),
            )
        )
    add_devices(entities)


class MqttCameraForwarder(ImageProcessingEntity):
    """Forward camera frames on MQTT"""

    def __init__(
        self,
        hass,
        mqtt_topic,
        camera_entity,
        name=None,
    ):
        """Init with the client."""
        self._hass = hass
        self._mqtt_topic = mqtt_topic
        self._camera_entity = camera_entity
        if name:  # Since name is optional.
            self._name = name
        else:
            entity_name = split_entity_id(camera_entity)[1]
            self._name = f"mqtt_camera_forwarder_{entity_name}"
        self._state = None # will count the number of frames published?

    def process_image(self, image):
        """Process an image."""
        mqtt.async_publish(self.hass, self._mqtt_topic, bytearray(image), qos=MQTT_QOS, retain=False)

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        attr["mqtt_topic"] = self._mqtt_topic
        return attr
