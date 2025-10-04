import os
import json
import streamlit as st
import pandas as pd

from app.helpers.config import PROFILE_CONFIG, PROFILES_DIR


def prepare_profile():
    payload = {}
    for prof_item in PROFILE_CONFIG:
        state_key, json_key, alt_result = prof_item
        if state_key in ['key_start_date', 'key_end_date']:
            payload[json_key] = st.session_state.get(
                state_key, alt_result).strftime('%Y-%m-%d')
        else:
            payload[json_key] = st.session_state.get(state_key, alt_result)
    return payload


def save_profile(name):
    payload = prepare_profile()
    safe_name = ''.join(ch for ch in name if ch.isalnum()
                        or ch in (' ', '_', '-')).rstrip()
    path = os.path.join(PROFILES_DIR, f"{safe_name}.json")
    with open(path, 'w') as fh:
        json.dump(payload, fh, default=str, indent=2)
    return path


def list_profiles():
    return [f for f in os.listdir(PROFILES_DIR) if f.endswith('.json')]


def load_profile(fname):
    path = os.path.join(PROFILES_DIR, fname)
    with open(path) as fh:
        payload = json.load(fh)
    for prof_item in PROFILE_CONFIG:
        state_key, json_key, alt_result = prof_item
        if state_key in ['key_start_date', 'key_end_date']:
            st.session_state[state_key] = pd.to_datetime(
                payload.get(json_key, alt_result)).date()
        else:
            st.session_state[state_key] = payload.get(json_key, alt_result)


# ----------------------------
# Initialize session state
# ----------------------------
def initialize_state_or_profile():
    if "load_profile" in st.session_state:
        load_profile(st.session_state.pop("load_profile"))
    else:
        for prof_item in PROFILE_CONFIG:
            state_key, _, alt_result = prof_item
            if state_key not in st.session_state:
                st.session_state[state_key] = alt_result

    if 'profiles_cache' not in st.session_state:
        st.session_state.profiles_cache = list_profiles()
