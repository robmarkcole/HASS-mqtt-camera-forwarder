"""
Platform that will perform object detection.
"""
from collections import namedtuple, Counter
import io
import logging

from PIL import Image

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

from homeassistant.const import ATTR_ENTITY_ID, ATTR_NAME

_LOGGER = logging.getLogger(__name__)

EVENT_FRAME_SENT = "mqtt_camera_forwarder.frame_sent"
CONF_MQTT_TOPIC = "mqtt_topic"
DEFAULT_MQTT_TOPIC = "hass_camera"

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
                mqtt_topic = config.get(CONF_MQTT_TOPIC)
                camera_entity=camera.get(CONF_ENTITY_ID),
                name=camera.get(CONF_NAME),
            )
        )
    add_devices(entities)


class MqttCameraForwarder(ImageProcessingEntity):
    """Forward camera frames on MQTT"""

    def __init__(
        self,
        mqtt_topic,
        camera_entity,
        name=None,
    ):
        """Init with the client."""
        self._mqtt_topic = mqtt_topic
        self._camera_entity = camera_entity
        if name:  # Since name is optional.
            self._name = name
        else:
            entity_name = split_entity_id(camera_entity)[1]
            self._name = f"rekognition_{entity_name}"
        self._state = None # will count the number of frames published?

    def process_image(self, image):
        """Process an image."""
        self._image = Image.open(io.BytesIO(bytearray(image)))  # used for saving only

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
