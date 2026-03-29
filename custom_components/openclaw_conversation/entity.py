"""Entity helpers for OpenClaw Conversation."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
import json
from typing import Any, Literal

import openai
from openai.types.chat import ChatCompletionMessage
import voluptuous as vol
from voluptuous_openapi import convert
from yarl import URL

from homeassistant.components import conversation
from homeassistant.const import CONF_MAX_TOKENS, CONF_MODEL
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, llm
from homeassistant.helpers.entity import Entity
from homeassistant.util.json import json_dumps
from homeassistant.util.slugify import slugify

from . import OpenClawConversationConfigEntry
from .const import (
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
    LOGGER,
    MAX_TOOL_ITERATIONS,
)
from .helpers import get_entry_settings


def _adjust_schema(schema: dict[str, Any]) -> None:
    """Adjust a JSON schema for provider compatibility."""
    schema_type = schema.get("type")

    if schema_type == "object":
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            return

        required = schema.setdefault("required", [])
        for key, value in properties.items():
            if isinstance(value, dict):
                _adjust_schema(value)
            if key not in required:
                value_type = value.get("type")
                if isinstance(value_type, str):
                    value["type"] = [value_type, "null"]
                required.append(key)

    if schema_type == "array" and isinstance(schema.get("items"), dict):
        _adjust_schema(schema["items"])


def _format_structured_output(
    name: str,
    schema: vol.Schema,
    custom_serializer: Callable[[Any], Any] | None,
) -> dict[str, Any]:
    """Format structured output schema for OpenAI-compatible providers."""
    converted = convert(schema, custom_serializer=custom_serializer)
    _adjust_schema(converted)
    return {
        "name": slugify(name),
        "strict": True,
        "schema": converted,
    }


def _format_tool(
    tool: llm.Tool,
    custom_serializer: Callable[[Any], Any] | None,
) -> dict[str, Any]:
    """Format a Home Assistant tool for the chat completions API."""
    parameters = convert(tool.parameters, custom_serializer=custom_serializer)
    _adjust_schema(parameters)
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": parameters,
            "strict": True,
        },
    }


def _decode_tool_arguments(arguments: str) -> dict[str, Any]:
    """Decode tool call arguments."""
    try:
        return json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as err:
        raise HomeAssistantError(f"Unexpected tool argument response: {err}") from err


def _convert_content_to_chat_message(
    content: conversation.Content,
) -> dict[str, Any] | None:
    """Convert chat log content into a chat completions message."""
    if isinstance(content, conversation.ToolResultContent):
        return {
            "role": "tool",
            "tool_call_id": content.tool_call_id,
            "content": json_dumps(content.tool_result),
        }

    if content.role == "system" and content.content:
        return {"role": "system", "content": content.content}

    if content.role == "user" and content.content:
        return {"role": "user", "content": content.content}

    if isinstance(content, conversation.AssistantContent):
        message: dict[str, Any] = {
            "role": "assistant",
            "content": content.content or "",
        }
        if content.tool_calls:
            message["tool_calls"] = [
                {
                    "type": "function",
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.tool_name,
                        "arguments": json_dumps(tool_call.tool_args),
                    },
                }
                for tool_call in content.tool_calls
            ]
        return message

    return None


async def _transform_response(
    message: ChatCompletionMessage,
) -> AsyncGenerator[conversation.AssistantContentDeltaDict]:
    """Transform an OpenAI-compatible message into chat log deltas."""
    content: str | None
    if isinstance(message.content, str) or message.content is None:
        content = message.content
    else:
        content = "".join(
            part.text
            for part in message.content
            if getattr(part, "type", None) == "text" and getattr(part, "text", None)
        )

    data: conversation.AssistantContentDeltaDict = {
        "role": "assistant",
        "content": content,
    }

    if message.tool_calls:
        data["tool_calls"] = [
            llm.ToolInput(
                id=tool_call.id,
                tool_name=tool_call.function.name,
                tool_args=_decode_tool_arguments(tool_call.function.arguments),
            )
            for tool_call in message.tool_calls
            if tool_call.type == "function"
        ]

    yield data


class OpenClawBaseEntity(Entity):
    """Base entity for OpenClaw Conversation."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: OpenClawConversationConfigEntry, unique_suffix: Literal["conversation", "ai_task"]
    ) -> None:
        """Initialize the entity."""
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"
        base_url = URL(get_entry_settings(entry)["base_url"])
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            entry_type=dr.DeviceEntryType.SERVICE,
            manufacturer="OpenClaw",
            model="Gateway API",
            name="OpenClaw Conversation",
            configuration_url=str(base_url.with_path("/")),
        )

    @property
    def settings(self) -> dict[str, Any]:
        """Return merged entry settings."""
        return get_entry_settings(self.entry)

    async def _async_handle_chat_log(
        self,
        chat_log: conversation.ChatLog,
        structure_name: str | None = None,
        structure: vol.Schema | None = None,
    ) -> None:
        """Generate an answer for the supplied chat log."""
        settings = self.settings

        tools: list[dict[str, Any]] | None = None
        if chat_log.llm_api:
            tools = [
                _format_tool(tool, chat_log.llm_api.custom_serializer)
                for tool in chat_log.llm_api.tools
            ]

        model_args: dict[str, Any] = {
            "model": settings[CONF_MODEL],
            "messages": [
                message
                for content in chat_log.content
                if (message := _convert_content_to_chat_message(content))
            ],
            "user": chat_log.conversation_id,
        }

        if tools:
            model_args["tools"] = tools

        if max_tokens := settings.get(CONF_MAX_TOKENS):
            model_args["max_tokens"] = max_tokens

        if temperature := settings.get(CONF_TEMPERATURE):
            model_args["temperature"] = temperature

        if top_p := settings.get(CONF_TOP_P):
            model_args["top_p"] = top_p

        if structure is not None and structure_name is not None:
            model_args["response_format"] = {
                "type": "json_schema",
                "json_schema": _format_structured_output(
                    structure_name,
                    structure,
                    chat_log.llm_api.custom_serializer if chat_log.llm_api else None,
                ),
            }

        client = self.entry.runtime_data

        for _iteration in range(MAX_TOOL_ITERATIONS):
            try:
                result = await client.chat.completions.create(**model_args)
            except openai.AuthenticationError as err:
                self.entry.async_start_reauth(self.hass)
                raise HomeAssistantError("Authentication with OpenClaw failed") from err
            except openai.OpenAIError as err:
                LOGGER.error("Error talking to OpenClaw: %s", err)
                raise HomeAssistantError("Error talking to the OpenClaw gateway") from err

            if result.usage is not None and hasattr(chat_log, "async_trace"):
                chat_log.async_trace(
                    {
                        "stats": {
                            "input_tokens": getattr(result.usage, "prompt_tokens", None),
                            "output_tokens": getattr(
                                result.usage, "completion_tokens", None
                            ),
                        }
                    }
                )

            result_message = result.choices[0].message
            model_args["messages"].extend(
                [
                    message
                    async for content in chat_log.async_add_delta_content_stream(
                        self.entity_id,
                        _transform_response(result_message),
                    )
                    if (message := _convert_content_to_chat_message(content))
                ]
            )

            if not chat_log.unresponded_tool_results:
                break

        if not isinstance(chat_log.content[-1], conversation.AssistantContent):
            raise HomeAssistantError("The OpenClaw gateway did not return an assistant response")
