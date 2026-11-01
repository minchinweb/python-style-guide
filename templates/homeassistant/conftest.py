# Copyright (c) 2026 Your Name
"""Shared fixtures; most come from pytest-homeassistant-custom-component."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.example.constants import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load the integration from `custom_components/`."""
    return


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """A config entry, as the config flow would create it."""
    return MockConfigEntry(domain=DOMAIN, title="Example", data={}, options={})
