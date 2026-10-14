"""Support for Johnson Controls Hx 3 Thermostat sensors"""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature

from .const import DOMAIN


async def async_setup_entry(hass, config, async_add_entities):
    """Set up the Hx 3 sensors."""
    data = hass.data[DOMAIN][config.entry_id]
    entities = []
    for controller in data.controllers:
        entities.append(Hx3HumiditySensor(data, controller))
        entities.append(Hx3OutdoorTemperatureSensor(data, controller))
    async_add_entities(entities, True)


class Hx3Sensor(SensorEntity):
    """Base class for Johnson Controls Hx 3 Thermostat sensors."""

    def __init__(self, data, controller):
        """Initialize the sensor."""
        self._data = data
        self._controller = controller

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._controller.id)},
            "name": self._controller.name,
            "manufacturer": self._controller.brand,
            "model": self._controller.model,
            "sw_version": self._controller.version,
            "suggested_area": self._controller.location_name,
        }

    @property
    def available(self) -> bool:
        return self._data.is_available()

    async def async_update(self):
        """Get the latest data from the service."""
        await self._data.async_update()


class Hx3HumiditySensor(Hx3Sensor):
    """Representation of a Johnson Controls Hx 3 Thermostat humidity sensor.

    Exposed as its own entity (rather than only as the climate entity's
    `current_humidity` attribute) so it shows up in History/Logbook and
    accrues long-term statistics.
    """

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, data, controller):
        """Initialize the humidity sensor."""
        super().__init__(data, controller)

        self._attr_unique_id = f"{controller.id}_humidity"
        self._attr_name = f"{controller.name} Humidity"

    @property
    def native_value(self) -> float | None:
        """Return the current humidity."""
        return self._controller.current_humidity


class Hx3OutdoorTemperatureSensor(Hx3Sensor):
    """Representation of a Johnson Controls Hx 3 Thermostat outdoor temperature.

    Reported in the account's temperature unit, the same as the climate
    entity's indoor temperature.
    """

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, data, controller):
        """Initialize the outdoor temperature sensor."""
        super().__init__(data, controller)

        self._attr_unique_id = f"{controller.id}_outdoor_temperature"
        self._attr_name = f"{controller.name} Outdoor Temperature"
        self._attr_native_unit_of_measurement = (
            UnitOfTemperature.CELSIUS
            if controller.temperature_unit == "C"
            else UnitOfTemperature.FAHRENHEIT
        )

    @property
    def native_value(self) -> float | None:
        """Return the current outdoor temperature."""
        return self._controller.outdoor_temperature
