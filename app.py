import streamlit as st
import pandas as pd
import random

# Initialize session state for data persistence
if "players" not in st.session_state:
    # Pre-populating with your example data for demonstration
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

if "current_lot" not in st.session_state:
    st.session_state.current_lot = 1

if "current_turn" not in st.session_state:
    # Game starts with a random selector for Lot 1
    st.session_state.current_turn = random.choice(["Selector 1", "Selector 2", "Selector 3", "Selector 4"])

st.title("🏏 Cricket Tournament Draft Portal")

# Sidebar Navigation
page = st.sidebar.radio("Go to", ["Admin Dashboard", "Selector Draft Room", "Team Rosters"])

# ------------------------------------------------------------------
# ADMIN DASHBOARD
# ------------------------------------------------------------------
if page == "Admin Dashboard":
    st.header("⚙️ Admin Dashboard: Player & Lot Management")
    
    # Form to ADD players
    with st.form("add_player_form", clear_on_submit=True):
        st.subheader("➕ Add New Player")
        name = st.text_input("Player Name")
        role = st.selectbox("Role/Skill", ["Batter", "Bowler", "All-rounder"])
        lot_number = st.number_input("Assign to Lot Number", min_value=1, max_value=15, value=1, step=1)
        
        submit = st.form_submit_button("Add Player")
        if submit and name:
            # Check if lot already has 4 players
            lot_count = sum(1 for p in st.session_state.players if p["lot"] == lot_number)
            if lot_count >= 4:
                st.error(f"❌ Lot {lot_number} is already full! (Max 4 players per lot)")
            else:
                st.session_state.players.append({"name": name, "role": role, "lot": lot_number})
                st.success(f"✅ Added {name} to Lot {lot_number} as a {role}")
                st.rerun()

    st.write("---")
    
    # Form to DELETE players
    st.subheader("🗑️ Delete Existing Player")
    if st.session_state.players:
        player_names = [p["name"] for p in st.session_state.players]
        player_to_delete = st.selectbox("Select player profile to remove:", player_names)
        
        if st.button("Delete Player Profile", type="primary"):
            st.session_state.players = [p for p in st.session_state.players if p["name"] != player_to_delete]
            
            # Remove from selector teams if already drafted
            for team in st.session_state.teams:
                st.session_state.teams[team] = [p for p in st.session_state.teams[team] if p["name"] != player_to_delete]
                
            st.success(f"🗑️ {player_to_delete} has been completely removed.")
            st.rerun()
    else:
        st.info("No players available to delete.")

    st.write("---")
    st.subheader("Current Player Lots")
    if st.session_state.players:
        df = pd.DataFrame(st.session_state.players)
        st.dataframe(df.sort_values(by=["lot", "role"]), use_container_width=True)
        st.metric(label="Total Registered Players", value=len(st.session_state.players))
    else:
        st.info("No players registered yet.")

# ------------------------------------------------------------------
# SELECTOR DRAFT ROOM
# ------------------------------------------------------------------
elif page == "Selector Draft Room":
    st.header("🎯 Live Draft Room")
    
    picked_players = [p for team in st.session_state.teams.values() for p in team]
    available_in_lot = [p for p in st.session_state.players if p["lot"] == st.session_state.current_lot and p["name"] not in picked_players]
    
    # Dynamic transition logic if current lot runs dry
    if not available_in_lot:
        remaining_lots = [p["lot"] for p in st.session_state.players if p["name"] not in picked_players]
        if remaining_lots:
            st.session_state.current_lot = min(remaining_lots)
            
            # CRITICAL UPDATE: Randomize who gets the 1st pick of this new lot
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            st.session_state.current_turn = random.choice(selectors)
            
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📦 Current Active: **Lot {st.session_state.current_lot}**")
        st.markdown(f"**Skill Level/Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Turn to Pick: <span style='color:#FF4B4B'>{st.session_state.current_turn}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players in this Lot")
    
    options = [p["name"] for p in available_in_lot]
    selected_player_name = st.radio("Choose a player to draft:", options)
    
    if st.button("Confirm Selection ➡️"):
        player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
        st.session_state.teams[st.session_state.current_turn].append(player_obj)
        
        # Maintain standard rotation order AFTER the random start has been assigned
        selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
        current_idx = selectors.index(st.session_state.current_turn)
        next_idx = (current_idx + 1) % 4
        st.session_state.current_turn = selectors[next_idx]
        
        st.toast(f"{selected_player_name} drafted successfully!")
        st.rerun()

# ------------------------------------------------------------------
# TEAM ROSTERS
# ------------------------------------------------------------------
elif page == "Team Rosters":
    st.header("📋 Current Team Squads")
    
    cols = st.columns(4)
    for i, (team_name, squad) in enumerate(st.session_state.teams.items()):
        with cols[i]:
            st.subheader(team_name)
            if squad:
                for player in squad:
                    st.write(f"• **{player['name']}** ({player['role']}) - _Lot {player['lot']}_")
            else:
                st.write("_No players drafted yet_")
