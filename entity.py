import logging

_LOGGER = logging.getLogger(__name__)

class BaseEntity:
    def __init__(self, hass,hub):
        self.hass = hass
        self.hub = hub
        self.unit = None