"""Nox tasks for the beskid_standard repository."""

from __future__ import annotations

import nox


@nox.session(python=False, name="quality")
def quality(session: nox.Session) -> None:
    session.run("python", "ci/quality.py")


@nox.session(python=False, name="test")
def test(session: nox.Session) -> None:
    session.run("python", "ci/run_corelib_tests.py")


@nox.session(python=False, name="compute_version")
def compute_version(session: nox.Session) -> None:
    session.run("python", "ci/version.py")


@nox.session(python=False, name="regen_fluent")
def regen_fluent(session: nox.Session) -> None:
    session.run("python", "ci/regen_fluent_surfaces.py")


@nox.session(python=False, name="publish_corelib")
def publish_corelib(session: nox.Session) -> None:
    session.run("python", "ci/publish_corelib.py")
