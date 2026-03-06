import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################

"""Ensures cancellation removes the user completely and allows them to re-register."""
def test_reregister_after_cancel():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.cancel("u1")
    status = er.register("u1")
    assert status == UserStatus("registered")
    assert er.snapshot()["registered"] == ["u1"]

"""Verifies FIFO promotions remain correct across multiple promotions."""
def test_multiple_cancellations_sequence():
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")  # waitlist pos1
    er.register("u4")  # waitlist pos2

    er.cancel("u1")  # promotes u3
    er.cancel("u2")  # promotes u4

    snap = er.snapshot()
    assert snap["registered"] == ["u3", "u4"]
    assert snap["waitlist"] == []

"""Ensures waitlist reorders correctly after a removal"""
def test_waitlisted_user_cancels_before_promotion():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")  # u2 cancels before promotion

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]

"""Directly tests my AC6"""
def test_query_unknown_user_returns_none():
    er = EventRegistration(capacity=2)
    er.register("u1")
    assert er.status("unknown") == UserStatus("none")

"""Ensures correct error handling"""
def test_cancel_unknown_user_raises_notfound():
    er = EventRegistration(capacity=2)
    er.register("u1")
    with pytest.raises(NotFound):
        er.cancel("unknown_user")

def test_multiple_promotions_and_queries():
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")  # waitlist pos1
    er.register("u4")  # waitlist pos2

    er.cancel("u1")  # promotes u3
    assert er.status("u3") == UserStatus("registered")
    assert er.status("u4") == UserStatus("waitlisted", 1)

    er.cancel("u2")  # promotes u4
    assert er.status("u4") == UserStatus("registered")
    snap = er.snapshot()
    assert snap["waitlist"] == []
    assert snap["registered"] == ["u3", "u4"]