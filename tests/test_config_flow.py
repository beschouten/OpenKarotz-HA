"""Tests for Open Karotz config flow."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import data_entry_flow
from homeassistant.const import CONF_HOST, CONF_NAME

from custom_components.open_karotz.config_flow import (
    OpenKarotzConfigFlow,
    validate_input,
    InvalidHost,
)


@pytest.fixture
def flow_handler():
    """Create a config flow handler."""
    return OpenKarotzConfigFlow()


async def test_show_user_form(flow_handler):
    """Test that the user form is shown."""
    result = await flow_handler.async_step_user()
    
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_valid_host(flow_handler):
    """Test that the user step with valid host creates an entry."""
    with patch(
        "custom_components.open_karotz.config_flow.validate_input", 
        return_value={"title": "Open Karotz"}
    ):
        result = await flow_handler.async_step_user(
            user_input={CONF_HOST: "192.168.1.70", CONF_NAME: "Open Karotz"}
        )
        
        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_HOST] == "192.168.1.70"
        assert result["data"][CONF_NAME] == "Open Karotz"


async def test_user_invalid_host(flow_handler):
    """Test that the user step with invalid host shows error."""
    with patch(
        "custom_components.open_karotz.config_flow.validate_input",
        side_effect=InvalidHost
    ):
        result = await flow_handler.async_step_user(
            user_input={CONF_HOST: "", CONF_NAME: "Open Karotz"}
        )
        
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"][CONF_HOST] == "invalid_host"


async def test_user_unknown_error(flow_handler):
    """Test that the user step with unknown error shows error."""
    with patch(
        "custom_components.open_karotz.config_flow.validate_input",
        side_effect=Exception("Unknown error")
    ):
        result = await flow_handler.async_step_user(
            user_input={CONF_HOST: "192.168.1.70", CONF_NAME: "Open Karotz"}
        )
        
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"]["base"] == "unknown"


async def test_validate_input_empty_host():
    """Test validation with empty host."""
    data = {CONF_HOST: "", CONF_NAME: "Open Karotz"}
    
    with pytest.raises(InvalidHost):
        await validate_input(None, data)


async def test_validate_input_valid_host():
    """Test validation with valid host."""
    data = {CONF_HOST: "192.168.1.70", CONF_NAME: "Open Karotz"}
    
    result = await validate_input(None, data)
    
    assert result["title"] == "Open Karotz"