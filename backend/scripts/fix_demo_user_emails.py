"""Repair malformed bulk-seeded user emails (and their passwords).

``seed_empty_models.py`` used to append its uniqueness suffix to the *whole*
generated value, so filler users were created with addresses like
``demo.497725@greenvalley.edu-497725230``:

- the login form's ``.email()`` validation refuses to submit them, and
- the filler rows were stored with an unhashed placeholder password, so
  ``POST /api/v1/auth/login/`` answers ``401`` even if the address is typed in.

This script is the data half of the fix (the seeder is the code half):

1. move the stray suffix into the local part
   (``demo.497725@greenvalley.edu-497725230`` → ``demo.497725-497725230@greenvalley.edu``);
2. put the address on the school's own mail domain when it drifted
   (Test School 0/1 fillers were all generated on ``greenvalley.edu``);
3. give the account the per-role demo password from ``docs/DEMO_CREDENTIALS.md``,
   mark it verified and active, so it can actually be used.

Rerunnable and safe: only users whose address is *invalid* are touched, E2E Test
School is skipped by default (its accounts are pinned by CI), and ``--dry-run``
reports without writing.

Usage (inside the backend container):

    python scripts/fix_demo_user_emails.py [--dry-run] [--include-e2e]
"""

import os
import re
import sys
import uuid
from collections import Counter

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402
from services.auth.models import School, User  # noqa: E402

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
# the shape the old seeder produced: a real domain with a token glued on
SUFFIXED_DOMAIN_RE = re.compile(r"^(?P<base>.+\.[A-Za-z]{2,})-(?P<token>[0-9A-Za-z]+)$")

ROLE_PASSWORDS = {
    "super_admin": "Admin@1234",
    "school_admin": "Admin@1234",
    "teacher": "Teacher@1234",
    "student": "Student@1234",
    "parent": "Parent@1234",
    "accountant": "Admin@1234",
    "librarian": "Admin@1234",
    "counselor": "Admin@1234",
    "alumni": "Alumni@1234",
}
DEFAULT_PASSWORD = "Admin@1234"
SKIPPED_SCHOOLS = ("E2E Test School",)
# a domain is adopted as the school's own only when a decent share of its valid
# accounts already use it — otherwise the school's subdomain is used instead
DOMAIN_MIN_USERS = 5


def is_valid(email):
    return bool(email and EMAIL_RE.match(email))


def school_domain(school, valid_emails):
    """Mail domain to rewrite this school's filler addresses onto.

    Prefer the domain the school's real accounts already use, but only when
    enough of them use it — a single stray ``@school.edu`` row in an otherwise
    empty Test School must not drag the whole school onto another tenant's
    domain. Otherwise fall back to the school's own subdomain.
    """
    counts = Counter(email.rsplit("@", 1)[1].lower() for email in valid_emails)
    if counts:
        domain, n = counts.most_common(1)[0]
        if n >= DOMAIN_MIN_USERS:
            return domain
    if school.subdomain:
        return f"{school.subdomain.lower()}.edu"
    return "greenvalley.edu"


def repaired_address(email, domain, taken):
    """Return a valid, unused address derived from ``email``."""
    local, _, old_domain = email.partition("@")
    token = None
    match = SUFFIXED_DOMAIN_RE.match(old_domain)
    if match:
        token = match.group("token")
    candidate = f"{local}-{token}@{domain}" if token else f"demo.{uuid.uuid4().hex[:8]}@{domain}"
    while candidate.lower() in taken or User.objects.filter(email__iexact=candidate).exists():
        candidate = f"{local}-{token or uuid.uuid4().hex[:8]}.{uuid.uuid4().hex[:4]}@{domain}"
    taken.add(candidate.lower())
    return candidate


def main():
    dry = "--dry-run" in sys.argv
    include_e2e = "--include-e2e" in sys.argv

    schools = list(School.objects.all().order_by("name"))
    hashed_passwords = {role: make_password(pwd) for role, pwd in ROLE_PASSWORDS.items()}

    total_repaired = 0
    per_school = {}
    examples = []

    for school in schools:
        if school.name in SKIPPED_SCHOOLS and not include_e2e:
            per_school[school.name] = "skipped (E2E pins these accounts)"
            continue

        users = list(User.objects.filter(school=school).exclude(email=""))
        malformed = [u for u in users if not is_valid(u.email)]
        if not malformed:
            per_school[school.name] = "nothing to fix"
            continue

        valid_emails = [u.email for u in users if is_valid(u.email)]
        domain = school_domain(school, valid_emails)
        taken = {e.lower() for e in valid_emails}
        changed = 0

        for user in malformed:
            old_email = user.email
            new_email = repaired_address(old_email, domain, taken)
            if not dry:
                # queryset update, not save(): post_save signals dispatch
                # welcome-mail tasks for a demo filler account.
                User.objects.filter(pk=user.pk).update(
                    email=new_email,
                    password=hashed_passwords.get(user.role, hashed_passwords["school_admin"]),
                    email_verified=True,
                    is_active=True,
                )
            changed += 1
            if len(examples) < 6:
                examples.append(f"{old_email}  ->  {new_email}  ({user.role}, {school.name})")

        per_school[school.name] = f"repaired {changed} ({domain})"
        total_repaired += changed

    print(
        f"{'DRY RUN — nothing written' if dry else 'repaired'} {total_repaired} accounts "
        f"(email + role password + verified + active)\n"
    )
    for name in sorted(per_school):
        print(f"  {name:26} {per_school[name]}")
    if examples:
        print("\nexamples:")
        for line in examples:
            print(f"  {line}")
    print(
        "\npasswords now follow docs/DEMO_CREDENTIALS.md "
        f"(default fallback {DEFAULT_PASSWORD}); verify with scripts/verify_all_logins.py"
    )


if __name__ == "__main__":
    main()
