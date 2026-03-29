"""Constants for the OpenClaw Conversation integration."""

from __future__ import annotations

import logging

from homeassistant.const import CONF_LLM_HASS_API, CONF_MAX_TOKENS, CONF_MODEL, CONF_PROMPT
from homeassistant.helpers import llm

DOMAIN = "openclaw_conversation"
LOGGER = logging.getLogger(__package__)

CONF_BASE_URL = "base_url"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"

DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 1.0
MAX_TOOL_ITERATIONS = 10

DEFAULT_OPTIONS: dict[str, object] = {
    CONF_PROMPT: llm.DEFAULT_INSTRUCTIONS_PROMPT,
    CONF_LLM_HASS_API: [],
    CONF_MAX_TOKENS: DEFAULT_MAX_TOKENS,
    CONF_TEMPERATURE: DEFAULT_TEMPERATURE,
    CONF_TOP_P: DEFAULT_TOP_P,
}

OPTION_KEYS = {
    CONF_MODEL,
    CONF_PROMPT,
    CONF_LLM_HASS_API,
    CONF_MAX_TOKENS,
    CONF_TEMPERATURE,
    CONF_TOP_P,
}
