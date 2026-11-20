"""Regression tests for the two bugs the Lab 12 gate caught and the suite missed.

The shipped suite never cancels a booking that has already begun, and it always
passes ``adjustments`` to ``build_statement`` explicitly, so neither path below
ran before.
"""

from refunds import policy, service
from refunds.models import utc


def test_a_cancellation_after_the_start_settles_at_zero(booking, cancellation):
    # mypy: policy.refund_cents returned None (declared -> int) for a no-show.
    request = cancellation(utc(2026, 3, 10, 14, 30))
    assert policy.refund_cents(booking, request) == 0
    statement = service.decide_refund(booking, request)
    assert statement.refund_cents == 0
    assert statement.withheld_cents == 12000


def test_statements_built_with_default_notes_do_not_share_them(booking):
    # ruff B006: a mutable default list was shared across calls.
    first = service.build_statement(booking, 12000, "full")
    second = service.build_statement(booking, 9000, "standard")
    assert first.adjustments == ("settled under the full tier",)
    assert second.adjustments == (
        "settled under the standard tier",
        "withheld $30.00 of $120.00",
    )
