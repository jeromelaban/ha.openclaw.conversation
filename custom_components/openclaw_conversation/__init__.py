"""The OpenClaw Conversation integration."""

from __future__ import annotations

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, AuthenticationError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError, ConfigEntryNotReady

from .helpers import create_client

PLATFORMS: tuple[Platform, ...] = (Platform.AI_TASK, Platform.CONVERSATION)

OpenClawConversationConfigEntry = ConfigEntry[AsyncOpenAI]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the OpenClaw Conversation integration."""
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: OpenClawConversationConfigEntry
) -> bool:
    """Set up OpenClaw Conversation from a config entry."""
    client = create_client(hass, entry)

    try:
        await client.models.list()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed from err
    except APIStatusError as err:
        if err.status_code in (401, 403):
            raise ConfigEntryAuthFailed from err
        if err.status_code >= 500 or err.status_code == 429:
            raise ConfigEntryNotReady(err) from err
        raise ConfigEntryError(str(err)) from err
    except APIConnectionError as err:
        raise ConfigEntryNotReady(err) from err

    entry.runtime_data = client
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
