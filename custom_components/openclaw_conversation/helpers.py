"""Helpers for the OpenClaw Conversation integration."""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from httpx import HTTPStatusError, RequestError
from yarl import URL

from .const import CONF_BASE_URL, DEFAULT_OPTIONS, OPTION_KEYS

if TYPE_CHECKING:
    from openai import AsyncOpenAI


def normalize_base_url(value: str) -> str:
    """Normalize a configured OpenAI-compatible base URL."""
    url = URL(value.strip())
    if not url.scheme or not url.host:
        raise ValueError("A full URL is required")

    path = url.path.rstrip("/")
    if not path:
        path = "/v1"
    elif not path.endswith("/v1"):
        path = f"{path}/v1"

    return str(url.with_path(path).with_query(None).with_fragment(None))


def get_entry_settings(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged settings for the entry."""
    settings: dict[str, Any] = dict(DEFAULT_OPTIONS)
    settings.update(entry.data)
    settings.update(entry.options)
    return settings


def get_options_payload(data: Mapping[str, Any]) -> dict[str, Any]:
    """Split non-connection settings into config entry options."""
    return {key: data[key] for key in OPTION_KEYS if key in data}


def get_config_payload(data: Mapping[str, Any]) -> dict[str, Any]:
    """Split connection settings into config entry data."""
    return {key: value for key, value in data.items() if key not in OPTION_KEYS}


async def async_import_openai_module(hass: HomeAssistant) -> Any:
    """Import the OpenAI SDK outside the event loop."""
    return await hass.async_add_executor_job(importlib.import_module, "openai")


async def async_create_client(hass: HomeAssistant, entry: ConfigEntry) -> "AsyncOpenAI":
    """Create an OpenAI-compatible async client for OpenClaw."""
    openai_module = await async_import_openai_module(hass)
    settings = get_entry_settings(entry)
    return openai_module.AsyncOpenAI(
        api_key=settings.get("api_key"),
        base_url=settings[CONF_BASE_URL],
        http_client=get_async_client(hass),
    )


async def async_probe_connection(
    hass: HomeAssistant,
    base_url: str,
    api_key: str,
) -> int:
    """Probe the OpenAI-compatible models endpoint without using SDK parsing."""
    client = get_async_client(hass)
    response = await client.get(
        f"{base_url.rstrip('/')}/models",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )

    try:
        response.raise_for_status()
    except HTTPStatusError:
        raise
    except RequestError:
        raise

    return response.status_code
