import streamlit as st
import pandas as pd
import random

# Initialize session state for single-device data persistence
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

# Generate a randomized sequence order for the very first lot
if "draft_sequence" not in st.session_state:
    selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
    random.shuffle(selectors)
    st.session_state.draft_sequence = selectors

st.title("🏏 Cricket Tournament Draft Portal")
st.caption("🎙️ Admin-Led Central Control Mode")

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
        name = st.text_input("Player Name").strip()
        role = st.selectbox("Role/Skill", ["Batter", "Bowler", "All-rounder"])
        lot_number = st.number_input("Assign to Lot Number", min_value=1, max_value=15, value=1, step=1)
        
        submit = st.form_submit_button("Add Player")
        if submit and name:
            existing_names = [p["name"].lower() for p in st.session_state.players]
            if name.lower() in existing_names:
                st.error(f"❌ Safeguard Active: '{name}' is already registered.")
            else:
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
    
    # Filter available players remaining in the active lot
    picked_players = [p for team in st.session_state.teams.values() for p in team]
    available_in_lot = [p for p in st.session_state.players if p["lot"] == st.session_state.current_lot and p["name"] not in picked_players]
    
    # Check if current lot is completely empty
    if not available_in_lot:
        remaining_lots = [p["lot"] for p in st.session_state.players if p["name"] not in picked_players]
        if remaining_lots:
            st.session_state.current_lot = min(remaining_lots)
            
            # Instantly shuffle a fresh pick sequence queue for the next upcoming lot
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            
            st.toast(f"Moving automatically to Lot {st.session_state.current_lot}!")
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    # Track how many picks have already happened in this exact lot (0 to 3)
    players_picked_in_this_lot = 4 - len(available_in_lot)
    current_turn_selector = st.session_state.draft_sequence[players_picked_in_this_lot]

    # Manual Shuffle Button (Only clickable before the very first pick of the lot is selected)
    if players_picked_in_this_lot == 0:
        st.info("💡 Fresh Lot loaded! You can shuffle the order right now if the selectors want a recalculation.")
        if st.button("🔀 Shuffle Pick Order for this Lot", type="secondary"):
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            st.rerun()

    st.write("---")

    # Visual Sequence Progress Board
    st.subheader("📋 Lot Picking Sequence")
    cols = st.columns(4)
    for index, selector_name in enumerate(st.session_state.draft_sequence):
        with cols[index]:
            if index == players_picked_in_this_lot:
                st.markdown(f"🎨 **Pick {index+1}:** \n <span style='color:#FF4B4B; font-weight:bold;'>👉 {selector_name} (CHOOSING NOW)</span>", unsafe_allow_html=True)
            elif index < players_picked_in_this_lot:
                st.markdown(f"✅ **Pick {index+1}:** \n ~~{selector_name}~~")
            else:
                st.markdown(f"⏳ **Pick {index+1}:** \n {selector_name}")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📦 Active: **Lot {st.session_state.current_lot}**")
        st.markdown(f"**Skill Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Current Turn: <span style='color:#FF4B4B'>{current_turn_selector}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players in Lot")
    
    options = [p["name"] for p in available_in_lot]
    
    if options:
        # Dynamic cache key mapping ensuring radio state resets immediately on every single click
        radio_key = f"single_device_lot_{st.session_state.current_lot}_pick_{players_picked_in_this_lot}"
        selected_player_name = st.radio("Select the player called out by the captain:", options, key=radio_key)
        
        # Big confirmation execution block
        if st.button("Confirm Selection ➡️", type="primary", use_container_width=True):
            player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
            
            # Append directly to the active captain's team
            st.session_state.teams[current_turn_selector].append(player_obj)
            st.toast(f"{selected_player_name} assigned to {current_turn_selector}!")
            
            # INSTANT RERUN: Forces top-to-bottom calculation. Bumps turn, updates list immediately!
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
st.title("🏏 Cricket Tournament Draft Portal")

# Sidebar Navigation
page = st.sidebar.radio("Go to", ["Admin Dashboard", "Selector Draft Room", "Team Rosters"])

# ------------------------------------------------------------------
# ADMIN DASHBOARD
# ------------------------------------------------------------------
if page == "Admin Dashboard":
    st.header("⚙️ Admin Dashboard: Player & Lot Management")

    st.subheader("🎲 Draft Sequence Configuration")
    st.write(f"Current Base Order for Lot {shared_data['current_lot']}: **{' ➡️ '.join(shared_data['draft_sequence'])}**")
        
    st.write("---")

    # Form to ADD players
    with st.form("add_player_form", clear_on_submit=True):
        st.subheader("➕ Add New Player")
        name = st.text_input("Player Name").strip()
        role = st.selectbox("Role/Skill", ["Batter", "Bowler", "All-rounder"])
        lot_number = st.number_input("Assign to Lot Number", min_value=1, max_value=15, value=1, step=1)
        
        submit = st.form_submit_button("Add Player")
        if submit and name:
            existing_names = [p["name"].lower() for p in shared_data["players"]]
            if name.lower() in existing_names:
                st.error(f"❌ Safeguard Active: '{name}' is already registered.")
            else:
                lot_count = sum(1 for p in shared_data["players"] if p["lot"] == lot_number)
                if lot_count >= 4:
                    st.error(f"❌ Lot {lot_number} is already full!")
                else:
                    shared_data["players"].append({"name": name, "role": role, "lot": lot_number})
                    st.success(f"✅ Added {name} to Lot {lot_number}")
                    st.invalidate_pages() # Forces cache sync
                    st.rerun()

    st.write("---")
    
    # Form to DELETE players
    st.subheader("🗑️ Delete Existing Player")
    if shared_data["players"]:
        player_names = [p["name"] for p in shared_data["players"]]
        player_to_delete = st.selectbox("Select player profile to remove:", player_names)
        
        if st.button("Delete Player Profile", type="primary"):
            shared_data["players"] = [p for p in shared_data["players"] if p["name"] != player_to_delete]
            for team in shared_data["teams"]:
                shared_data["teams"][team] = [p for p in shared_data["teams"][team] if p["name"] != player_to_delete]
            st.success(f"🗑️ {player_to_delete} removed.")
            st.rerun()

# ------------------------------------------------------------------
# SELECTOR DRAFT ROOM
# ------------------------------------------------------------------
elif page == "Selector Draft Room":
    st.header("🎯 Live Draft Room")
    
    # MOBILE FIX: Global sync refresh button right at the top
    if st.button("🔄 Refresh Draft Board", type="primary", use_container_width=True):
        st.toast("Syncing data with server...")
        st.rerun()

    # Calculate active parameters based on live shared data
    picked_players = [p for team in shared_data["teams"].values() for p in team]
    available_in_lot = [p for p in shared_data["players"] if p["lot"] == shared_data["current_lot"] and p["name"] not in picked_players]
    
    # Handle Lot transitions
    if not available_in_lot:
        remaining_lots = [p["lot"] for p in shared_data["players"] if p["name"] not in picked_players]
        if remaining_lots:
            shared_data["current_lot"] = min(remaining_lots)
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            shared_data["draft_sequence"] = selectors
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    # Determine current active picker based on remaining count
    players_picked_in_this_lot = 4 - len(available_in_lot)
    current_turn_selector = shared_data["draft_sequence"][players_picked_in_this_lot]

    # Manual Shuffle control before picks start
    if players_picked_in_this_lot == 0:
        if st.button("🔀 Shuffle Pick Order for this Lot", type="secondary"):
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            shared_data["draft_sequence"] = selectors
            st.rerun()

    st.write("---")

    # Visual Sequence Tracker
    st.subheader("📋 Lot Picking Order")
    cols = st.columns(4)
    for index, selector_name in enumerate(shared_data["draft_sequence"]):
        with cols[index]:
            if index == players_picked_in_this_lot:
                st.markdown(f"🎨 **Pick {index+1}:** \n <span style='color:#FF4B4B; font-weight:bold;'>👉 {selector_name}</span>", unsafe_allow_html=True)
            elif index < players_picked_in_this_lot:
                st.markdown(f"✅ **Pick {index+1}:** \n ~~{selector_name}~~")
            else:
                st.markdown(f"⏳ **Pick {index+1}:** \n {selector_name}")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📦 Active: **Lot {shared_data['current_lot']}**")
        st.markdown(f"**Skill Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Turn: <span style='color:#FF4B4B'>{current_turn_selector}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players")
    
    options = [p["name"] for p in available_in_lot]
    
    if options:
        # Generate layout change key to clear selection bubbles automatically
        radio_key = f"lot_{shared_data['current_lot']}_pick_{players_picked_in_this_lot}"
        selected_player_name = st.radio("Choose a player:", options, key=radio_key)
        
        if st.button("Confirm Selection ➡️", use_container_width=True):
            # Safe check again to prevent speed double-clicks
            fresh_picked_check = [p for team in shared_data["teams"].values() for p in team]
            if selected_player_name in [p["name"] for p in fresh_picked_check]:
                st.error("⚠️ This player has already been snapped up! Click Refresh.")
            else:
                player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
                shared_data["teams"][current_turn_selector].append(player_obj)
                st.toast(f"Drafted successfully!")
                st.rerun()
    else:
        st.warning("Please click the 'Refresh Draft Board' button at the top to load incoming lot picks.")

# ------------------------------------------------------------------
# TEAM ROSTERS
# ------------------------------------------------------------------
elif page == "Team Rosters":
    st.header("📋 Current Team Squads")
    cols = st.columns(4)
    for i, (team_name, squad) in enumerate(shared_data["teams"].items()):
        with cols[i]:
            st.subheader(team_name)
            if squad:
                for player in squad:
                    st.write(f"• **{player['name']}** ({player['role']})")
        submit = st.form_submit_button("Add Player")
        if submit and name:
            existing_names = [p["name"].lower() for p in st.session_state.players]
            
            if name.lower() in existing_names:
                st.error(f"❌ Safeguard Active: A player named '{name}' is already registered.")
            else:
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
    
    # CRITICAL FIX: Instantly filter out picked players so they can NEVER be double-selected
    picked_players = [p for team in st.session_state.teams.values() for p in team]
    available_in_lot = [p for p in st.session_state.players if p["lot"] == st.session_state.current_lot and p["name"] not in picked_players]
    
    # Handle Lot transitions and auto-shuffling for the incoming lot
    if not available_in_lot:
        remaining_lots = [p["lot"] for p in st.session_state.players if p["name"] not in picked_players]
        if remaining_lots:
            st.session_state.current_lot = min(remaining_lots)
            
            # Auto-shuffle a fresh sequence queue for the new lot
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    # Determine current active picker based on how many players are left in the current lot
    players_picked_in_this_lot = 4 - len(available_in_lot)
    current_turn_selector = st.session_state.draft_sequence[players_picked_in_this_lot]

    # Shuffle button logic
    if players_picked_in_this_lot == 0:
        st.info("💡 New Lot opened! You can shuffle the sequence below before making the first pick.")
        if st.button("🔀 Shuffle Pick Order for this Lot", type="secondary"):
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            st.toast("🎲 Sequence Shuffled!")
            st.rerun()
    else:
        st.caption("🔒 Shuffle disabled for this round because picking has already started.")

    st.write("---")

    # Visual Sequence Tracker
    st.subheader("📋 Lot Picking Order")
    cols = st.columns(4)
    for index, selector_name in enumerate(st.session_state.draft_sequence):
        with cols[index]:
            if index == players_picked_in_this_lot:
                st.markdown(f"🎨 **Pick {index+1}:** \n <span style='color:#FF4B4B; font-weight:bold;'>👉 {selector_name} (UP NOW)</span>", unsafe_allow_html=True)
            elif index < players_picked_in_this_lot:
                st.markdown(f"✅ **Pick {index+1}:** \n ~~{selector_name}~~")
            else:
                st.markdown(f"⏳ **Pick {index+1}:** \n {selector_name}")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📦 Current Active: **Lot {st.session_state.current_lot}**")
        st.markdown(f"**Skill Level/Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Turn to Pick: <span style='color:#FF4B4B'>{current_turn_selector}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players in this Lot")
    
    options = [p["name"] for p in available_in_lot]
    
    if options:
        # FIX: We use a dynamic unique key for the radio widget. 
        # When a selection is confirmed, the key changes, forcing the radio button to reset cleanly for the next selector.
        radio_key = f"lot_{st.session_state.current_lot}_pick_{players_picked_in_this_lot}"
        selected_player_name = st.radio("Choose an available player:", options, key=radio_key)
        
        if st.button("Confirm Selection ➡️"):
            # Double check that the selected player wasn't already picked
            fresh_picked_check = [p for team in st.session_state.teams.values() for p in team]
            if selected_player_name in [p["name"] for p in fresh_picked_check]:
                st.error("⚠️ This player has already been selected!")
            else:
                # Add player to current selector's team
                player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
                st.session_state.teams[current_turn_selector].append(player_obj)
                
                st.toast(f"{selected_player_name} drafted successfully by {current_turn_selector}!")
                
                # Force an instant app rerun to shift turn state and clear out the picked player option
                st.rerun()
    else:
        st.warning("No players currently available to draft in this lot.")

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
        st.subheader("➕ Add New Player")
        name = st.text_input("Player Name").strip()
        role = st.selectbox("Role/Skill", ["Batter", "Bowler", "All-rounder"])
        lot_number = st.number_input("Assign to Lot Number", min_value=1, max_value=15, value=1, step=1)
        
        submit = st.form_submit_button("Add Player")
        if submit and name:
            # SAFEGUARD 1: Check if player name already exists globally (case-insensitive)
            existing_names = [p["name"].lower() for p in st.session_state.players]
            
            if name.lower() in existing_names:
                st.error(f"❌ Safeguard Active: A player named '{name}' is already registered in the tournament database. Duplicates are blocked!")
            else:
                # Safeguard 2: Check if lot already has 4 players
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
    
    # SAFEGUARD 3: Instantly calculates who has already been picked so they can never show up again
    picked_players = [p for team in st.session_state.teams.values() for p in team]
    available_in_lot = [p for p in st.session_state.players if p["lot"] == st.session_state.current_lot and p["name"] not in picked_players]
    
    # Handle Lot transitions and auto-shuffling for the incoming lot
    if not available_in_lot:
        remaining_lots = [p["lot"] for p in st.session_state.players if p["name"] not in picked_players]
        if remaining_lots:
            st.session_state.current_lot = min(remaining_lots)
            
            # Auto-shuffle a fresh sequence queue for the new lot
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    # Determine current active picker based on how many players are left in the current lot
    players_picked_in_this_lot = 4 - len(available_in_lot)
    current_turn_selector = st.session_state.draft_sequence[players_picked_in_this_lot]

    # FEATURE: SHUFFLE BUTTON IN DRAFT ROOM
    if players_picked_in_this_lot == 0:
        st.info("💡 New Lot opened! You can shuffle the sequence below before making the first pick.")
        if st.button("🔀 Shuffle Pick Order for this Lot", type="secondary"):
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            st.toast("🎲 Sequence Shuffled!")
            st.rerun()
    else:
        st.caption("🔒 Shuffle disabled for this round because picking has already started.")

    st.write("---")

    # Visual Sequence Tracker
    st.subheader("📋 Lot Picking Order")
    cols = st.columns(4)
    for index, selector_name in enumerate(st.session_state.draft_sequence):
        with cols[index]:
            if index == players_picked_in_this_lot:
                st.markdown(f"🎨 **Pick {index+1}:** \n <span style='color:#FF4B4B; font-weight:bold;'>👉 {selector_name} (UP NOW)</span>", unsafe_allow_html=True)
            elif index < players_picked_in_this_lot:
                st.markdown(f"✅ **Pick {index+1}:** \n ~~{selector_name}~~")
            else:
                st.markdown(f"⏳ **Pick {index+1}:** \n {selector_name}")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📦 Current Active: **Lot {st.session_state.current_lot}**")
        st.markdown(f"**Skill Level/Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Turn to Pick: <span style='color:#FF4B4B'>{current_turn_selector}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players in this Lot")
    
    options = [p["name"] for p in available_in_lot]
    
    # SAFEGUARD 4: Defensive check to prevent layout rendering issues if choices empty out weirdly
    if options:
        selected_player_name = st.radio("Choose a player to draft:", options)
        
        if st.button("Confirm Selection ➡️"):
            # Double check that the selected player wasn't sniped right before clicking
            still_available_picked_check = [p for team in st.session_state.teams.values() for p in team]
            if selected_player_name in [p["name"] for p in still_available_picked_check]:
                st.error("⚠️ This player has already been selected by someone else!")
            else:
                player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
                st.session_state.teams[current_turn_selector].append(player_obj)
                st.toast(f"{selected_player_name} drafted successfully by {current_turn_selector}!")
                st.rerun()
    else:
        st.warning("No players currently available to draft in this lot.")

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
    with st.form("add_player_form", clear_on_submit=True):
        st.subheader("➕ Add New Player")
        name = st.text_input("Player Name")
        role = st.selectbox("Role/Skill", ["Batter", "Bowler", "All-rounder"])
        lot_number = st.number_input("Assign to Lot Number", min_value=1, max_value=15, value=1, step=1)
        
        submit = st.form_submit_button("Add Player")
        if submit and name:
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
    
    # Handle Lot transitions and auto-shuffling for the incoming lot
    if not available_in_lot:
        remaining_lots = [p["lot"] for p in st.session_state.players if p["name"] not in picked_players]
        if remaining_lots:
            st.session_state.current_lot = min(remaining_lots)
            
            # Auto-shuffle a fresh sequence queue for the new lot
            selectors = ["Selector 1", "Selector 2", "Selector 3", "Selector 4"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    # Determine current active picker based on how many players are left in the current lot
    # 4 players left -> 1st in sequence picks
    # 3 players left -> 2nd in sequence picks, etc.
    players_picked_in_this_lot = 4 - len(available_in_lot)
    current_turn_selector = st.session_state.draft_sequence[players_picked_in_this_lot]

    # NEW VISUAL FEATURE: Show the structural sequence of the active lot pick order
    st.subheader("📋 Lot Picking Order")
    cols = st.columns(4)
    for index, selector_name in enumerate(st.session_state.draft_sequence):
        with cols[index]:
            if index == players_picked_in_this_lot:
                st.markdown(f"🎨 **Pick {index+1}:** \n <span style='color:#FF4B4B; font-weight:bold;'>👉 {selector_name} (UP NOW)</span>", unsafe_allow_html=True)
            elif index < players_picked_in_this_lot:
                st.markdown(f"✅ **Pick {index+1}:** \n ~~{selector_name}~~")
            else:
                st.markdown(f"⏳ **Pick {index+1}:** \n {selector_name}")

    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📦 Current Active: **Lot {st.session_state.current_lot}**")
        st.markdown(f"**Skill Level/Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Turn to Pick: <span style='color:#FF4B4B'>{current_turn_selector}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players in this Lot")
    
    options = [p["name"] for p in available_in_lot]
    selected_player_name = st.radio("Choose a player to draft:", options)
    
    if st.button("Confirm Selection ➡️"):
        player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
        st.session_state.teams[current_turn_selector].append(player_obj)
        st.toast(f"{selected_player_name} drafted successfully by {current_turn_selector}!")
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
