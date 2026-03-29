"""The OpenClaw Conversation integration."""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryError,
    ConfigEntryNotReady,
)
from homeassistant.helpers import config_validation as cv
from httpx import HTTPStatusError, RequestError

from .const import CONF_BASE_URL, DOMAIN
from .helpers import (
    async_create_client,
    async_import_openai_module,
    async_probe_connection,
)

PLATFORMS: tuple[Platform, ...] = (Platform.AI_TASK, Platform.CONVERSATION)


@dataclass(slots=True)
class OpenClawRuntimeData:
    """Runtime data for a configured OpenClaw entry."""

    client: Any
    openai_module: ModuleType

OpenClawConversationConfigEntry = ConfigEntry[OpenClawRuntimeData]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the OpenClaw Conversation integration."""
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: OpenClawConversationConfigEntry
) -> bool:
    """Set up OpenClaw Conversation from a config entry."""
    try:
        await async_probe_connection(
            hass,
            entry.data[CONF_BASE_URL],
            entry.data[CONF_API_KEY],
        )
    except HTTPStatusError as err:
        if err.status_code in (401, 403):
            raise ConfigEntryAuthFailed from err
        if err.status_code >= 500 or err.status_code == 429:
            raise ConfigEntryNotReady(err) from err
        raise ConfigEntryError(str(err)) from err
    except RequestError as err:
        raise ConfigEntryNotReady(err) from err

    client = await async_create_client(hass, entry)
    openai_module = await async_import_openai_module(hass)

    entry.runtime_data = OpenClawRuntimeData(
        client=client,
        openai_module=openai_module,
    )
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: OpenClawConversationConfigEntry
) -> None:
    """Reload the config entry after an update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: OpenClawConversationConfigEntry
) -> bool:
    """Unload an OpenClaw Conversation entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
