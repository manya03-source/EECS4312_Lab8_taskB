import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound

def assert_status(actual, expected_state, expected_position=None):
    assert actual.state == expected_state
    if expected_state == "waitlisted":
        assert actual.position == expected_position
    else:
        assert actual.position is None

def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert_status(s1, "registered")
    assert_status(s2, "registered")
    assert_status(s3, "waitlisted", 1)
    assert_status(s4, "waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert_status(er.status("u1"), "none")
    assert_status(er.status("u2"), "registered")
    assert_status(er.status("u3"), "waitlisted", 1)

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

    assert_status(er.status("u2"), "none")
    assert_status(er.status("u3"), "waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert_status(er.register("u1"), "waitlisted", 1)
    assert_status(er.register("u2"), "waitlisted", 2)  
    # No one can ever be registered when capacity=0
    
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
    assert_status(er.register("u1"), "registered")
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

    assert_status(er.status("u2"), "none")
    assert_status(er.status("u3"), "waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]

"""Directly tests my AC6"""
def test_query_unknown_user_returns_none():
    er = EventRegistration(capacity=2)
    er.register("u1")
    assert_status(er.status("unknown_user"), "none")

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
    assert_status(er.status("u3"), "registered")

    er.cancel("u2")  # promotes u4
    assert_status(er.status("u4"), "registered")
    snap = er.snapshot()
    assert snap["waitlist"] == []
    assert snap["registered"] == ["u3", "u4"]

#Covers C3, AC4
def test_waitlist_promotion_is_deterministic():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u1")  # should promote u2
    snap = er.snapshot()

    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]

#Covers C6, AC5
def test_duplicate_registration_after_cancellation():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.cancel("u1")
    assert_status(er.register("u1"), "registered")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

#Covers EC2, AC4
def test_edge_case_capacity_zero_behaviour():
    er = EventRegistration(capacity=0)
    result = er.register("u1")
    assert_status(result, "waitlisted", 1)
    assert er.snapshot()["registered"] == []
    assert er.snapshot()["waitlist"] == ["u1"]

#Covers C2, AC6
def test_invariant_no_user_in_multiple_states():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist
    snap = er.snapshot()
    assert set(snap["registered"]).isdisjoint(set(snap["waitlist"]))

#Covers EC4
def test_multiple_waitlist_promotions_fifo_order():
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")  
    er.register("u3")  
    er.register("u4")  

    er.cancel("u1")  # promotes u2
    er.cancel("u2")  # promotes u3

    snap = er.snapshot()
    assert snap["registered"] == ["u3","u4"]
    assert snap["waitlist"] == []

#Covers C6
def test_cancel_unknown_user_error_behaviour():
    er = EventRegistration(capacity=2)
    er.register("u1")
    with pytest.raises(NotFound):
        er.cancel("does_not_exist")