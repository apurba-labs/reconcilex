import pytest

from pydantic import ValidationError

from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.planner import PlannedToolCall
from reconcilex.investigator.tool_executor import (
    ALLOWED_INVESTIGATION_TOOLS,
    ToolExecutionError,
    ToolExecutor,
)
from reconcilex.tools.payment_tools import PaymentTools


def build_executor() -> ToolExecutor:
    store = PaymentRecordStore("data/records")

    return ToolExecutor(
        PaymentTools(store),
    )


def test_executor_exposes_exact_investigation_allowlist():
    executor = build_executor()

    assert executor.allowed_tools == ALLOWED_INVESTIGATION_TOOLS

    assert executor.allowed_tools == frozenset(
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


def test_executor_can_read_invoice():
    executor = build_executor()

    result = executor.execute(
        PlannedToolCall(
            tool_name="get_invoice",
            arguments={
                "invoice_id": "INV-1008",
            },
        )
    )

    assert result is not None
    assert result["invoice_id"] == "INV-1008"
    assert result["currency"] == "EUR"


def test_executor_can_read_webhook_events():
    executor = build_executor()

    result = executor.execute(
        PlannedToolCall(
            tool_name="get_webhook_events",
            arguments={
                "payment_id": "PI-1008",
            },
        )
    )

    assert result
    assert result[0]["webhook_id"] == "WH-8001"


@pytest.mark.parametrize(
    "forbidden_tool",
    [
        "read_file",
        "open_file",
        "write_file",
        "delete_file",
        "execute_python",
        "execute_sql",
        "shell",
        "bash",
        "refund_payment",
        "capture_payment",
        "mark_invoice_paid",
        "replay_webhook",
    ],
)
def test_executor_rejects_forbidden_capabilities(
    forbidden_tool: str,
):
    executor = build_executor()

    with pytest.raises(
        ToolExecutionError,
        match="not allowed",
    ):
        executor.execute(
            PlannedToolCall(
                tool_name=forbidden_tool,
                arguments={},
            )
        )


def test_executor_rejects_invalid_arguments():
    executor = build_executor()

    with pytest.raises(
        ValidationError,
        match="Extra inputs are not permitted",
    ):
        PlannedToolCall(
            tool_name="get_invoice",
            arguments={
                "wrong_argument": "INV-1008",
            },
        )