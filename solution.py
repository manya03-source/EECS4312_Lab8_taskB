## Student Name: Manya Khattri
## Student ID: 219830025

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator. 
You are asked to implement a Python module that manages registration for a single event with a fixed capacity. 
The system must:
•	Accept a fixed capacity.
•	Register users until capacity is reached.
•	Place additional users into a FIFO waitlist.
•	Automatically promote the earliest waitlisted user when a registered user cancels.
•	Prevent duplicate registrations.
•	Allow users to query their current status.

The system must ensure that:
•	The number of registered users never exceeds capacity.
•	Waitlist ordering preserves FIFO behavior.
•	Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
•	A user may not appear more than once in the system.
•	A user may not simultaneously exist in multiple states.
•	The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
•	Multiple cancellations in sequence.
•	Users attempting to re-register after canceling.
•	Waitlisted users canceling before promotion.
•	Capacity equal to zero.
•	Simultaneous or rapid consecutive operations.
•	Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation (if required by handout)."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None
    explanation: Optional[str] = None  # Optional field for additional info (e.g., error messages)


class EventRegistration:
    """
    Students must implement this class per the lab handout.
    Deterministic ordering is required (e.g., FIFO waitlist, predictable registration order).
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        # TODO: Initialize internal data structures
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self._capacity = capacity
        self._registered: List[str] = []  # List of registered user IDs
        self._waitlist: List[str] = []    # List of waitlisted user IDs
        self._users = set()  # Set of all user IDs for quick duplicate checks

    def _check_invariants(self) -> None:
        """
        Ensures system invariants remain valid after each operations.
        """
        assert len(self._registered) <= self._capacity, \
            "Registered users exceed capacity"
        assert len(set(self._registered)) == len(set(self._registered)), \
            "Duplicate users detected in registered list"
        assert len(set(self._waitlist)) == len(set(self._waitlist)), \
            "Duplicate users found in waitlist"
        assert not (set(self._registered) & set(self._waitlist)), \
            "User exists in both registered and waitlist"

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        # TODO: Implement per lab handout
        if user_id in self._users:
            raise DuplicateRequest(f"User {user_id} already exists, Registration failed")
        if user_id in self._registered or user_id in self._waitlist:
            raise DuplicateRequest(f"User {user_id} already exists")
        self._users.add(user_id)

        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            explanation = "User registered successfully"
            self._check_invariants()
            return UserStatus(
                state="registered",
                explanation=explanation
            )
        self._waitlist.append(user_id)
        explanation = "Event Full, User added to waitlist"
        self._check_invariants()
        return UserStatus(
            state="waitlisted", 
            position=len(self._waitlist),
            explanation=explanation
        )

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - behavior when user not found depends on handout (raise NotFound or ignore)

        Raises:
            NotFound (if required by handout)
        """
        # TODO: Implement per lab handout
        if user_id not in self._users:
            raise NotFound(f"User {user_id} not found for cancellation")
        self._users.remove(user_id)

        if user_id in self._registered:
            self._registered.remove(user_id)
            explanation = f"User {user_id} cancelled registration"
            if self._waitlist:
                promoted_user = self._waitlist.pop(0)
                self._registered.append(promoted_user)
                explanation += (
                    f" Waitlisted user {promoted_user} promoted to registered"
                )
            self._check_invariants()
            return explanation
        if user_id in self._waitlist:
            self._waitlist.remove(user_id)
            self._check_invariants()
            return f"User {user_id} removed from waitlist"
        raise NotFound(
            f"Cancellation failed: User {user_id} not found in registered or waitlist"
        )

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        # TODO: Implement per lab handout
        if user_id in self._registered:
            return UserStatus(
                state="registered",
                explanation="User is currently registered"
            )
        if user_id in self._waitlist:
            position = self._waitlist.index(user_id) + 1
            return UserStatus(state="waitlisted", position=position, explanation=f"User is waitlisted at position {position}")
        return UserStatus(state="none", explanation="User not found in registered or waitlist")


    def snapshot(self) -> dict:
        """
        (Optional helper for debugging/tests)
        Return a deterministic snapshot of internal state.
        """
        # TODO: Implement if required/allowed
        return {
            "capacity": self._capacity,
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
            "registered_count": len(self._registered),
            "waitlist_count": len(self._waitlist)
        }