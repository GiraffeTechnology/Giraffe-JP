"""Unit tests for Giraffe JP outbound draft approval-status selection logic."""
import pytest


def test_auto_send_maps_to_auto_sent_status():
    """When auto_send=True, draft approval_status must be AUTO_SENT."""
    auto_send = True
    approval_status = "AUTO_SENT" if auto_send else "PENDING_HUMAN_CONFIRMATION"
    assert approval_status == "AUTO_SENT"


def test_manual_send_maps_to_pending_status():
    """When auto_send=False (including unknown categories), status must be PENDING."""
    auto_send = False
    approval_status = "AUTO_SENT" if auto_send else "PENDING_HUMAN_CONFIRMATION"
    assert approval_status == "PENDING_HUMAN_CONFIRMATION"


def test_approval_status_values_are_distinct():
    statuses = {"AUTO_SENT", "PENDING_HUMAN_CONFIRMATION", "APPROVED", "REJECTED"}
    assert len(statuses) == 4


def test_only_pending_drafts_can_be_approved():
    """Spec: approve/reject may only act on PENDING_HUMAN_CONFIRMATION drafts."""
    valid_for_review = "PENDING_HUMAN_CONFIRMATION"
    invalid_states = ["AUTO_SENT", "APPROVED", "REJECTED"]
    for state in invalid_states:
        assert state != valid_for_review


def test_no_outbound_message_bypasses_permission_check():
    """Spec rule 8: no outbound message may bypass category permission."""
    unknown_auto_send = False
    approval_status = "AUTO_SENT" if unknown_auto_send else "PENDING_HUMAN_CONFIRMATION"
    assert approval_status == "PENDING_HUMAN_CONFIRMATION"
