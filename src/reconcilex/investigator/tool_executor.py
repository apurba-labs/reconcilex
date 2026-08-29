from __future__ import annotations

from typing import Any, Callable

from reconcilex.investigator.planner import PlannedToolCall
from reconcilex.tools.payment_tools import PaymentTools


ALLOWED_INVESTIGATION_TOOLS = frozenset(
    {
        "get_case_context",
        "get_invoice",
        "get_gateway_events",
        "get_webhook_events",
        "get_settlements",
        "get_refunds",
        "get_audit_events",
        "get_payment_timeline",
    }
)


class ToolExecutionError(Exception):
    """Raised when the agent requests an invalid or unauthorized tool call."""


class ToolExecutor:
    """
    Controlled execution boundary for the investigation agent.

    The agent receives no filesystem, shell, SQL, arbitrary Python,
    or mutation capabilities. It can only call explicitly registered,
    read-only investigation tools.
    """

    def __init__(self, tools: PaymentTools):
        self._registry: dict[str, Callable[..., Any]] = {
            "get_case_context": tools.get_case_context,
            "get_invoice": tools.get_invoice,
            "get_gateway_events": tools.get_gateway_events,
            "get_webhook_events": tools.get_webhook_events,
            "get_settlements": tools.get_settlements,
            "get_refunds": tools.get_refunds,
            "get_audit_events": tools.get_audit_events,
            "get_payment_timeline": tools.get_payment_timeline,
        }

        if set(self._registry) != set(ALLOWED_INVESTIGATION_TOOLS):
            raise RuntimeError(
                "Tool registry does not match the approved investigation allowlist."
            )

    @property
    def allowed_tools(self) -> frozenset[str]:
        return ALLOWED_INVESTIGATION_TOOLS

    def execute(self, tool_call: PlannedToolCall) -> Any:
        if tool_call.tool_name not in ALLOWED_INVESTIGATION_TOOLS:
            raise ToolExecutionError(
                f"Tool '{tool_call.tool_name}' is not allowed."
            )

        tool = self._registry.get(tool_call.tool_name)

        if tool is None:
            raise ToolExecutionError(
                f"Tool '{tool_call.tool_name}' is not registered."
            )

        try:
            return tool(**tool_call.arguments)
        except TypeError as exc:
            raise ToolExecutionError(
                f"Invalid arguments for tool "
                f"'{tool_call.tool_name}': {exc}"
            ) from exc