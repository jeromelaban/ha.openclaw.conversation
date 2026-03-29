"""Helpers for the OpenClaw Conversation integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openai import AsyncOpenAI
from yarl import URL

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client

from .const import CONF_BASE_URL, DEFAULT_OPTIONS, OPTION_KEYS


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


def create_client(hass: HomeAssistant, entry: ConfigEntry) -> AsyncOpenAI:
    """Create an OpenAI-compatible async client for OpenClaw."""
    settings = get_entry_settings(entry)
    return AsyncOpenAI(
        api_key=settings.get("api_key"),
        base_url=settings[CONF_BASE_URL],
        http_client=get_async_client(hass),
    )
