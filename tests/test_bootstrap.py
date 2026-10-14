"""Tests for the orchestrator: ordering, --only, critical/non-critical, exit codes."""

from __future__ import annotations

import pytest

from dotfiles import bootstrap
from dotfiles.config.settings import Settings
from dotfiles.utils.exceptions import StepError


@pytest.fixture
def recording_steps(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace STEPS with lightweight steps that record the order they ran in."""
    order: list[str] = []

    def make(
        name: str, *, fail: bool = False, critical: bool = False
    ) -> bootstrap.Step:
        def _run(_settings: Settings) -> None:
            order.append(name)
            if fail:
                raise StepError(f"{name} boom")

        return bootstrap.Step(name, _run, critical=critical)

    steps = (
        make("alpha"),
        make("beta", fail=True),
        make("gamma"),
    )
    monkeypatch.setattr(bootstrap, "STEPS", steps)
    return order


def test_runs_all_steps_in_declared_order(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    order: list[str] = []
    steps = tuple(
        bootstrap.Step(n, lambda _s, n=n: order.append(n)) for n in ("a", "b", "c")
    )
    monkeypatch.setattr(bootstrap, "STEPS", steps)
    assert bootstrap.run(settings) == 0
    assert order == ["a", "b", "c"]


def test_only_filters_but_preserves_order(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    order: list[str] = []
    steps = tuple(
        bootstrap.Step(n, lambda _s, n=n: order.append(n)) for n in ("a", "b", "c")
    )
    monkeypatch.setattr(bootstrap, "STEPS", steps)
    bootstrap.run(settings, only=["c", "a"])
    assert order == ["a", "c"]


def test_non_critical_failure_continues_and_exits_one(
    recording_steps: list[str], settings: Settings
) -> None:
    code = bootstrap.run(settings)
    assert recording_steps == ["alpha", "beta", "gamma"]
    assert code == 1


def test_critical_failure_aborts(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    order: list[str] = []

    def boom(_s: Settings) -> None:
        order.append("boom")
        raise StepError("critical fail")

    steps = (
        bootstrap.Step("first", lambda _s: order.append("first")),
        bootstrap.Step("boom", boom, critical=True),
        bootstrap.Step("never", lambda _s: order.append("never")),
    )
    monkeypatch.setattr(bootstrap, "STEPS", steps)
    code = bootstrap.run(settings)
    assert code == 1
    assert "never" not in order


def test_non_dotfiles_errors_propagate(
    monkeypatch: pytest.MonkeyPatch, settings: Settings
) -> None:
    def bug(_s: Settings) -> None:
        raise KeyError("a real bug, not a DotfilesError")

    monkeypatch.setattr(bootstrap, "STEPS", (bootstrap.Step("bug", bug),))
    # A genuine bug must surface, not be swallowed as a step "issue".
    with pytest.raises(KeyError):
        bootstrap.run(settings)


def test_step_names_matches_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    steps = tuple(bootstrap.Step(n, lambda _s: None) for n in ("x", "y"))
    monkeypatch.setattr(bootstrap, "STEPS", steps)
    assert bootstrap.step_names() == ["x", "y"]
