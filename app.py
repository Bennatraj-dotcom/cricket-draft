import streamlit as st
import pandas as pd
import random
import time
from fpdf import FPDF

# Initialize session state for single-device data persistence
if "players" not in st.session_state:
    st.session_state.players = [
        {"name": "Kevin", "role": "Batter", "lot": 1},
        {"name": "Suresh", "role": "Batter", "lot": 1},
        {"name": "Sathish", "role": "Batter", "lot": 1},
        {"name": "Ben", "role": "Batter", "lot": 1},
        {"name": "Kannan", "role": "Bowler", "lot": 2},
        {"name": "KD", "role": "Bowler", "lot": 2},
        {"name": "Joy", "role": "Bowler", "lot": 2},
        {"name": "Raghu", "role": "Bowler", "lot": 2},
        {"name": "Maddy", "role": "All-rounder", "lot": 3},
        {"name": "Hari", "role": "All-rounder", "lot": 3},
        {"name": "Arun", "role": "All-rounder", "lot": 3},
        {"name": "Vijay", "role": "All-rounder", "lot": 3},
    ]

if "teams" not in st.session_state:
    st.session_state.teams = {
        "Selector 1": [],
        "Selector 2": [],
        "Selector 3": [],
        "Selector 4": []
    }

if
