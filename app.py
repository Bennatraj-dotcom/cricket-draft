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
        "Selector 3": []
    }

if "current_lot" not in st.session_state:
    st.session_state.current_lot = 1

if "draft_sequence" not in st.session_state:
    selectors = ["Selector 1", "Selector 2", "Selector 3"]
    random.shuffle(selectors)
    st.session_state.draft_sequence = selectors

st.title("🏏 Cricket Tournament Draft Portal")
st.caption("🎙️ Admin-Led Central Control Mode (3 Selectors)")

# Sidebar Navigation
page = st.sidebar.radio("Go to", ["Admin Dashboard", "Selector Draft Room", "Team Rosters"], key="nav_menu_v9")

# Helper function to generate PDF bytes
def generate_pdf(teams_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Title Block
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Cricket Tournament - Final Squads", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    
    # Loop through teams and construct rows
    for team_name, squad in teams_data.items():
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"=== {team_name} ===", ln=True)
        pdf.set_font("Helvetica", "", 11)
        
        if squad:
            for i, player in enumerate(squad, 1):
                pdf.cell(0, 8, f"{i}. {player['name']} ({player['role']}) - Lot {player['lot']}", ln=True)
        else:
            pdf.cell(0, 8, "No players drafted yet.", ln=True)
        pdf.ln(5)
        
    return bytes(pdf.output())

# ------------------------------------------------------------------
# ADMIN DASHBOARD
# ------------------------------------------------------------------
if page == "Admin Dashboard":
    st.header("⚙️ Admin Dashboard: Player & Lot Management")

    st.subheader("📊 CSV Data Utilities")
    col_exp, col_imp = st.columns(2)
    
    with col_exp:
        st.write("📂 **Backup Data**")
        if st.session_state.players:
            export_df = pd.DataFrame(st.session_state.players)
            csv_buffer = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Players to CSV",
                data=csv_buffer,
                file_name="cricket_player_database.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No data available to export yet.")
            
    with col_imp:
        st.write("📤 **Bulk Replace Database**")
        uploaded_file = st.file_uploader("Upload new players CSV file", type=["csv"], label_visibility="collapsed", key="csv_uploader_v9")
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                required_headers = {"name", "role", "lot"}
                if not required_headers.issubset(set(uploaded_df.columns)):
                    st.error("❌ Invalid CSV headers! Must contain exactly: 'name', 'role', and 'lot'")
                else:
                    st.session_state.players = []
                    for team in st.session_state.teams:
                        st.session_state.teams[team] = []
                        
                    st.session_state.current_lot = 1
                    selectors = ["Selector 1", "Selector 2", "Selector 3"]
                    random.shuffle(selectors)
                    st.session_state.draft_sequence = selectors
                    
                    success_count = 0
                    full_lot_count = 0
                    
                    for _, row in uploaded_df.iterrows():
                        p_name = str(row['name']).strip()
                        p_role = str(row['role']).strip()
                        p_lot = int(row['lot'])
                        
                        lot_count = sum(1 for p in st.session_state.players if p["lot"] == p_lot)
                        
                        if lot_count >= 4:
                            full_lot_count += 1
                        else:
                            st.session_state.players.append({"name": p_name, "role": p_role, "lot": p_lot})
                            success_count += 1
                    
                    st.success(f"💥 Database overwritten! {success_count} fresh entries loaded successfully.")
                    if full_lot_count > 0:
                        st.error(f"❌ Skipped {full_lot_count} records because target lots were already filled with 4 players.")
                    
                    time.sleep(1.0)
                    st.rerun()
            except Exception as csv_err:
                st.error(f"Error parsing file: {csv_err}")

    st.write("---")

    with st.form("add_player_form", clear_on_submit=True):
        st.subheader("➕ Add Single New Player")
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
                    st.error(f"❌ Lot {lot_number} is already full!")
                else:
                    st.session_state.players.append({"name": name, "role": role, "lot": lot_number})
                    st.success(f"✅ Added {name} to Lot {lot_number} as a {role}")
                    st.rerun()

    st.write("---")
    
    st.subheader("🗑️ Delete Existing Player")
    if st.session_state.players:
        player_options = [f"{p['name']} (Lot {p['lot']} - {p['role']})" for p in st.session_state.players]
        player_to_delete_str = st.selectbox("Select player profile to remove:", player_options, key="delete_select_v9")
        
        if st.button("Delete Player Profile", type="primary", key="del_btn_v9"):
            idx = player_options.index(player_to_delete_str)
            target_player = st.session_state.players[idx]
            st.session_state.players.pop(idx)
            
            for team in st.session_state.teams:
                st.session_state.teams[team] = [p for p in st.session_state.teams[team] if p["name"] != target_player["name"]]
                
            st.success(f"🗑️ Removed completely from system.")
            st.rerun()
    else:
        st.info("No players available to delete.")

    st.write("---")
    st.subheader("Current Player Lots")
    if st.session_state.players:
        df = pd.DataFrame(st.session_state.players)
        st.dataframe(df.sort_values(by=["lot", "role"]), use_container_width=True)
        st.metric(label="Total Registered Players", value=len(st.session_state.players))

# ------------------------------------------------------------------
# SELECTOR DRAFT ROOM
# ------------------------------------------------------------------
elif page == "Selector Draft Room":
    st.header("🎯 Live Draft Room")
    
    # Track available players remaining in the active lot
    available_in_lot = []
    for p in st.session_state.players:
        if p["lot"] == st.session_state.current_lot:
            is_picked = False
            for team_squad in st.session_state.teams.values():
                if any(t["name"] == p["name"] and t["lot"] == p["lot"] and t["role"] == p["role"] for t in team_squad):
                    is_picked = True
                    break
            if not is_picked:
                available_in_lot.append(p)
                
    # CRITICAL SCALE RULE FOR 3 SELECTORS:
    # Since lots have 4 players, when exactly 1 player is left unpicked, that means all 3 selectors have had their turn.
    # The final player is skipped, and we trigger a lot transition.
    if len(available_in_lot) <= 1:
        remaining_lots = []
        for p in st.session_state.players:
            is_picked = False
            for team_squad in st.session_state.teams.values():
                if any(t["name"] == p["name"] and t["lot"] == p["lot"] and t["role"] == p["role"] for t in team_squad):
                    is_picked = True
                    break
            if not is_picked and p["lot"] > st.session_state.current_lot:
                remaining_lots.append(p["lot"])
                
        if remaining_lots:
            st.session_state.current_lot = min(remaining_lots)
            
            # Left-shift sequence rotation for 3 elements
            old_sequence = st.session_state.draft_sequence
            rotated_sequence = old_sequence[1:] + [old_sequence[0]]
            st.session_state.draft_sequence = rotated_sequence
            
            st.toast(f"Lot completed! Shifting automatically to Lot {st.session_state.current_lot}")
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 All lots completed! The draft is officially over.")
            st.stop()

    # Calculate active selection pointer index (0, 1, or 2)
    # 4 players available -> Pick 1
    # 3 players available -> Pick 2
    # 2 players available -> Pick 3
    players_picked_in_this_lot = 4 - len(available_in_lot)
    if players_picked_in_this_lot > 2:
        players_picked_in_this_lot = 2
        
    current_turn_selector = st.session_state.draft_sequence[players_picked_in_this_lot]

    if players_picked_in_this_lot == 0:
        st.info("🔄 Order will rotate automatically for each lot.")
        if st.button("🔀 Manual Shuffle for this Lot", type="secondary", key="shuffle_v9"):
            selectors = ["Selector 1", "Selector 2", "Selector 3"]
            random.shuffle(selectors)
            st.session_state.draft_sequence = selectors
            st.rerun()

    st.write("---")

    st.subheader("📋 Lot Picking Sequence")
    cols = st.columns(3)
    for index, selector_name in enumerate(st.session_state.draft_sequence):
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
        st.markdown(f"### 📦 Active: **Lot {st.session_state.current_lot}**")
        st.markdown(f"**Skill Type:** {available_in_lot[0]['role'] if available_in_lot else 'N/A'}")
    with col2:
        st.markdown(f"### 🕒 Current Turn: <span style='color:#FF4B4B'>{current_turn_selector}</span>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Available Players in Lot")
    
    options = [p["name"] for p in available_in_lot]
    
    if options:
        radio_id = f"rad_v9_l{st.session_state.current_lot}_p{players_picked_in_this_lot}_len{len(options)}"
        selected_player_name = st.radio("Select the player called out by the captain:", options, key=radio_id)
        
        if st.button("Confirm Selection ➡️", type="primary", use_container_width=True, key=f"btn_v9_{radio_id}"):
            with st.spinner(f"Processing pick... Assigning to {current_turn_selector}"):
                player_obj = next(p for p in available_in_lot if p["name"] == selected_player_name)
                st.session_state.teams[current_turn_selector].append(player_obj)
                time.sleep(0.4) 
            st.rerun()
    else:
        st.warning("No players currently available to draft.")

# ------------------------------------------------------------------
# TEAM ROSTERS
# ------------------------------------------------------------------
elif page == "Team Rosters":
    st.header("📋 Current Team Squads")
    
    try:
        pdf_bytes = generate_pdf(st.session_state.teams)
        st.download_button(
            label="📥 Download Rosters as PDF",
            data=pdf_bytes,
            file_name="cricket_squads_final.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key="pdf_download_btn_v9"
        )
    except Exception as e:
        st.error(f"Error compiling PDF: {e}")
        
    st.write("---")
    
    cols = st.columns(3)
    for i, (team_name, squad) in enumerate(st.session_state.teams.items()):
        with cols[i]:
            st.subheader(team_name)
            if squad:
                for player in squad:
                    st.write(f"• **{player['name']}** ({player['role']}) - _Lot {player['lot']}_")
            else:
                st.write("_No players drafted yet_")
