"""Guards for the demo-seeder helpers that produced unusable filler accounts.

``seed_empty_models`` used to satisfy uniqueness by appending a run suffix to
the whole generated value, which turned generated addresses into
``demo.497725@greenvalley.edu-497725230`` — invalid, un-mailable, and rejected by
the login form. These tests load the script by path (it is not an importable
package) and pin the two behaviours that fixed it.
"""

import importlib.util
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "seed_empty_models.py"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


@pytest.fixture(scope="module")
def seeder():
    spec = importlib.util.spec_from_file_location("seed_empty_models_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "value",
    [
        "demo.497725@greenvalley.edu",
        "sarah.mitchell@demo.edusphere.school",
    ],
)
def test_unique_suffix_keeps_addresses_valid(seeder, value):
    """The suffix goes into the local part so the domain stays intact."""
    field = next(f for f in _user_fields(seeder) if f.name == "email")
    suffixed = seeder.unique_suffix(value, field, "-deadbeef123")

    assert EMAIL_RE.match(suffixed), suffixed
    local, _, domain = suffixed.partition("@")
    assert domain == value.partition("@")[2]
    assert local.endswith("-deadbeef123")


def test_unique_suffix_respects_max_length(seeder):
    """A long local part is truncated, never the domain."""
    field = next(f for f in _user_fields(seeder) if f.name == "email")
    suffixed = seeder.unique_suffix("a" * 300 + "@school.edu", field, "-deadbeef123")

    assert len(suffixed) <= field.max_length
    assert suffixed.endswith("@school.edu")
    assert EMAIL_RE.match(suffixed)


def test_unique_suffix_still_suffixes_plain_strings(seeder):
    """Non-email uniques keep the historical append behaviour."""
    field = next(f for f in _user_fields(seeder) if f.name == "first_name")
    assert seeder.unique_suffix("Alpha", field, "-deadbeef123") == "Alpha-deadbeef123"


def test_generated_addresses_are_valid(seeder):
    """Whatever the seeder generates for an email field must be a real address."""
    field = next(f for f in _user_fields(seeder) if f.name == "email")
    value = seeder.value_for_field(field, _user_model(seeder), None, 0, 0, {})
    assert EMAIL_RE.match(value), value


def test_role_passwords_cover_every_login_role(seeder):
    """Filler users get a hashed role password, so every role needs an entry."""
    expected = {
        "super_admin",
        "school_admin",
        "teacher",
        "student",
        "parent",
        "accountant",
        "librarian",
        "counselor",
    }
    assert expected <= set(seeder.ROLE_PASSWORDS)
    assert set(seeder.ROLE_PASSWORDS.values()) == {
        "Admin@1234",
        "Teacher@1234",
        "Student@1234",
        "Parent@1234",
        "Alumni@1234",
    }


def _user_model(seeder):
    return seeder.apps.get_model("auth_service", "User")


def _user_fields(seeder):
    return _user_model(seeder)._meta.fields
