"""Config flow for OpenClaw Conversation."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY, CONF_LLM_HASS_API
from homeassistant.core import callback
from homeassistant.helpers import llm
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    TemplateSelector,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from httpx import HTTPStatusError, RequestError

from .const import (
    CONF_BASE_URL,
    CONF_MAX_TOKENS,
    CONF_MODEL,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_MAX_TOKENS,
    DEFAULT_OPTIONS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DOMAIN,
)
from .helpers import async_probe_connection, get_entry_settings, normalize_base_url

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL): TextSelector(
            TextSelectorConfig(type=TextSelectorType.URL)
        ),
        vol.Required(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
        vol.Required(CONF_MODEL): TextSelector(),
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


def _valid_llm_api_ids(hass, selected: str | list[str] | None) -> list[str]:
    """Return LLM API ids that still exist."""
    if not selected:
        return []
    if isinstance(selected, str):
        selected = [selected]

    known = {api.id for api in llm.async_get_apis(hass)}
    return [api_id for api_id in selected if api_id in known]


async def _async_validate_connection(
    hass,
    base_url: str,
    api_key: str,
) -> dict[str, str]:
    """Validate the provided OpenClaw connection settings."""
    try:
        await async_probe_connection(hass, base_url, api_key)
    except HTTPStatusError as err:
        if err.status_code in (401, 403):
            return {"base": "invalid_auth"}
        if err.status_code == 404:
            return {"base": "invalid_url"}
        if err.status_code >= 500 or err.status_code == 429:
            return {"base": "cannot_connect"}
        _LOGGER.error("Unexpected API status during validation: %s", err)
        return {"base": "unknown"}
    except RequestError:
        return {"base": "cannot_connect"}
    except Exception:
        _LOGGER.exception("Unexpected exception while validating OpenClaw settings")
        return {"base": "unknown"}

    return {}


class OpenClawConversationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenClaw Conversation."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return OpenClawConversationOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors: dict[str, str] = {}
        try:
            normalized_url = normalize_base_url(user_input[CONF_BASE_URL])
        except ValueError:
            errors["base"] = "invalid_url"
            return self.async_show_form(
                step_id="user",
                data_schema=self.add_suggested_values_to_schema(
                    STEP_USER_DATA_SCHEMA, user_input
                ),
                errors=errors,
            )

        api_key = user_input[CONF_API_KEY].strip()
        model = user_input[CONF_MODEL].strip()
        self._async_abort_entries_match({CONF_BASE_URL: normalized_url})

        errors = await _async_validate_connection(self.hass, normalized_url, api_key)
        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=self.add_suggested_values_to_schema(
                    STEP_USER_DATA_SCHEMA,
                    {
                        **user_input,
                        CONF_BASE_URL: normalized_url,
                        CONF_API_KEY: api_key,
                        CONF_MODEL: model,
                    },
                ),
                errors=errors,
            )

        title = f"OpenClaw ({normalized_url})"
        entry_payload = {
            CONF_BASE_URL: normalized_url,
            CONF_API_KEY: api_key,
        }
        options_payload = {
            **DEFAULT_OPTIONS,
            CONF_MODEL: model,
        }
        return self.async_create_entry(
            title=title,
            data=entry_payload,
            options=options_payload,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm updated credentials."""
        reauth_entry = self._get_reauth_entry()

        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=STEP_REAUTH_DATA_SCHEMA,
            )

        api_key = user_input[CONF_API_KEY].strip()
        errors = await _async_validate_connection(
            self.hass,
            reauth_entry.data[CONF_BASE_URL],
            api_key,
        )
        if errors:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=self.add_suggested_values_to_schema(
                    STEP_REAUTH_DATA_SCHEMA,
                    {CONF_API_KEY: api_key},
                ),
                errors=errors,
            )

        self.hass.config_entries.async_update_entry(
            reauth_entry,
            data={**reauth_entry.data, CONF_API_KEY: api_key},
        )
        await self.hass.config_entries.async_reload(reauth_entry.entry_id)
        return self.async_abort(reason="reauth_successful")


class OpenClawConversationOptionsFlow(OptionsFlow):
    """Handle OpenClaw Conversation options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the integration options."""
        settings = get_entry_settings(self.config_entry)
        selected_llm_apis = _valid_llm_api_ids(
            self.hass, settings.get(CONF_LLM_HASS_API)
        )

        if user_input is not None:
            if not user_input.get(CONF_LLM_HASS_API):
                user_input.pop(CONF_LLM_HASS_API, None)
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_MODEL): TextSelector(),
                        vol.Optional(CONF_PROMPT): TemplateSelector(),
                        vol.Optional(
                            CONF_LLM_HASS_API,
                            description={"suggested_value": selected_llm_apis},
                        ): SelectSelector(
                            SelectSelectorConfig(
                                options=[
                                    SelectOptionDict(label=api.name, value=api.id)
                                    for api in llm.async_get_apis(self.hass)
                                ],
                                multiple=True,
                            )
                        ),
                        vol.Optional(CONF_MAX_TOKENS): NumberSelector(
                            NumberSelectorConfig(
                                min=1,
                                step=1,
                                mode=NumberSelectorMode.BOX,
                            )
                        ),
                        vol.Optional(CONF_TEMPERATURE): NumberSelector(
                            NumberSelectorConfig(
                                min=0,
                                max=2,
                                step=0.1,
                                mode=NumberSelectorMode.BOX,
                            )
                        ),
                        vol.Optional(CONF_TOP_P): NumberSelector(
                            NumberSelectorConfig(
                                min=0,
                                max=1,
                                step=0.05,
                                mode=NumberSelectorMode.BOX,
                            )
                        ),
                    }
                ),
                {
                    CONF_MODEL: settings.get(CONF_MODEL),
                    CONF_PROMPT: settings.get(CONF_PROMPT),
                    CONF_LLM_HASS_API: selected_llm_apis,
                    CONF_MAX_TOKENS: settings.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
                    CONF_TEMPERATURE: settings.get(
                        CONF_TEMPERATURE, DEFAULT_TEMPERATURE
                    ),
                    CONF_TOP_P: settings.get(CONF_TOP_P, DEFAULT_TOP_P),
                },
            ),
        )
