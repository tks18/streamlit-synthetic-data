import streamlit as st
from typing import cast

from app.helpers.config import STATE_CONFIG
from app.types import TAppStateConfig


def get_state_config() -> TAppStateConfig:
    payload = {}
    for prof_item in STATE_CONFIG:
        state_key, json_key, alt_result = prof_item
        if state_key in ['key_start_date', 'key_end_date']:
            payload[json_key] = st.session_state.get(
                state_key, alt_result).strftime('%Y-%m-%d')
        else:
            payload[json_key] = st.session_state.get(state_key, alt_result)
    return cast(TAppStateConfig, payload)
