import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMinimize, LpMaximize, LpVariable, lpSum, LpStatus, value
from io import StringIO

# ---------------------------------------------------------------------
# 1. SETUP & DATA
# ---------------------------------------------------------------------

# layout="centered" keeps it centered on screen (not too wide)
st.set_page_config(page_title="Z-A Donut Calculator", page_icon="🍩", layout="centered") 

berry_csv = """
Name,Sweet,Spicy,Sour,Bitter,Fresh,Lv_Boost,Cal
Hyper Cheri,0,40,0,0,5,5,80
Hyper Chesto,0,0,0,0,40,3,100
Hyper Pecha,40,0,0,0,0,2,100
Hyper Rawst,0,0,0,40,0,3,110
Hyper Aspear,0,0,40,0,0,4,90
Hyper Oran,10,20,15,15,0,6,90
Hyper Persim,0,15,15,10,20,4,110
Hyper Lum,20,15,10,0,15,3,110
Hyper Sitrus,15,10,0,20,15,4,120
Hyper Pomeg,30,35,0,0,5,7,140
Hyper Kelpsy,5,0,0,30,35,5,160
Hyper Qualot,35,0,30,5,0,4,160
Hyper Hondew,0,5,35,0,30,6,150
Hyper Grepa,0,60,25,0,5,8,140
Hyper Tamato,5,25,0,0,40,6,180
Hyper Occa,60,0,0,5,25,5,180
Hyper Passho,25,0,5,60,0,6,200
Hyper Wacan,0,5,60,25,0,7,160
Hyper Rindo,15,55,0,5,25,9,210
Hyper Yache,25,0,5,15,55,7,250
Hyper Chople,55,5,15,25,0,6,250
Hyper Kebia,0,15,25,55,5,7,270
Hyper Shuca,5,25,55,0,15,8,230
Hyper Coba,10,95,0,10,5,10,240
Hyper Payapa,5,0,10,10,95,8,300
Hyper Tanga,95,10,10,5,0,7,300
Hyper Charti,0,10,5,95,10,8,330
Hyper Kasib,10,5,95,0,10,9,270
Hyper Haban,85,0,0,0,65,8,370
Hyper Colbur,0,0,65,0,85,9,370
Hyper Babiri,0,0,65,85,0,9,400
Hyper Chilan,0,85,0,65,0,9,370
Hyper Roseli,0,65,85,0,0,10,340
"""

recipes = {
    "Darkrai (Bad Dream Cruller)":    {"Sweet":310, "Spicy":100, "Sour":310, "Bitter":40,  "Fresh":40},
    "Groudon (Omega Old-Fashioned)":  {"Sweet":260, "Spicy":160, "Sour":160, "Bitter":20,  "Fresh":260},
    "Kyogre (Alpha Old-Fashioned)":   {"Sweet":50,  "Spicy":50,  "Sour":210, "Bitter":180, "Fresh":370},
    "Rayquaza (Delta Old-Fashioned)": {"Sweet":120, "Spicy":40,  "Sour":340, "Bitter":40,  "Fresh":390},
    "Zeraora (Plasma-Glazed)":        {"Sweet":40,  "Spicy":200, "Sour":400, "Bitter":280, "Fresh":40}
}

# Load Data
df = pd.read_csv(StringIO(berry_csv))
if "Inventory" not in df.columns:
    df["Inventory"] = 0

# ---------------------------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------------------------

def solve_donut(data, target_stats, mode="min"):
    sense = LpMinimize if mode == "min" else LpMaximize
    prob = LpProblem("DonutOpt", sense)
    
    berry_vars = {}
    for i, row in data.iterrows():
        name = row['Name']
        berry_vars[name] = LpVariable(f"count_{name}", lowBound=0, upBound=row['Inventory'], cat='Integer')

    objective_terms = []
    for i, row in data.iterrows():
        objective_terms.append((i + 1) * berry_vars[row['Name']])
    
    prob += lpSum(objective_terms)

    for stat in ["Sweet", "Spicy", "Sour", "Bitter", "Fresh"]:
        prob += lpSum([data.loc[i, stat] * berry_vars[data.loc[i, 'Name']] for i in data.index]) >= target_stats[stat]
        
    prob += lpSum(berry_vars.values()) <= 8
    
    prob.solve()
    
    if LpStatus[prob.status] == "Optimal":
        results = []
        for i, row in data.iterrows():
            name = row['Name']
            val = value(berry_vars[name])
            if val > 0:
                results.append({"Berry": name, "Count": int(val), "Cal": row['Cal'], "Lv_Boost": row['Lv_Boost']})
        return results
    else:
        return None

def display_recipe(results, title, color_emoji):
    if results:
        st.success(f"### {color_emoji} {title}")
        res_df = pd.DataFrame(results)
        st.dataframe(res_df[["Berry", "Count"]], hide_index=True, use_container_width=True)
        total_slots = sum(r['Count'] for r in results)
        total_cal = sum(r['Count'] * r['Cal'] for r in results)
        total_boost = sum(r['Count'] * r['Lv_Boost'] for r in results)
        st.markdown(f"**Slots:** {total_slots}/8  |  **Calories:** {total_cal}  |  **Lv. Boost:** +{total_boost}")
    else:
        st.error(f"### {color_emoji} {title}\nNot possible with current inventory.")

# ---------------------------------------------------------------------
# 3. UI LAYOUT
# ---------------------------------------------------------------------

st.title("🍩 Pokémon Legends: Z-A Donut Calculator")
st.markdown("""
**Instructions:**
1. Enter your **Inventory** in the table below (Look for the **✏️** column).
2. Select the **Donut** you want to craft.
3. Click **Calculate**.
""")

# Input Section
target_donut_name = st.selectbox("Select Target Donut:", list(recipes.keys()))

st.subheader("Your Inventory")

# Configuration for the table columns
# Added emoji icons to clearly distinguish Editable vs Read-Only fields
column_cfg = {
    "Name": st.column_config.TextColumn("Berry Name", disabled=True, width="medium"),
    
    # EDITABLE (Pencil icon)
    "Inventory": st.column_config.NumberColumn(
        "✏️ Inventory (Qty)", 
        help="Enter the amount you have in your bag.",
        min_value=0, 
        step=1, 
        required=True, 
        width="small"
    ),
    
    # READ-ONLY (Lock icon)
    "Sweet": st.column_config.NumberColumn("🔒 Sweet", disabled=True, width="small"),
    "Spicy": st.column_config.NumberColumn("🔒 Spicy", disabled=True, width="small"),
    "Sour": st.column_config.NumberColumn("🔒 Sour", disabled=True, width="small"),
    "Bitter": st.column_config.NumberColumn("🔒 Bitter", disabled=True, width="small"),
    "Fresh": st.column_config.NumberColumn("🔒 Fresh", disabled=True, width="small"),
    "Lv_Boost": st.column_config.NumberColumn("🔒 Lv. Boost", disabled=True, width="small"),
    "Cal": st.column_config.NumberColumn("🔒 Cal", disabled=True, width="small"),
}

edited_df = st.data_editor(
    df,
    column_config=column_cfg,
    hide_index=True,
    use_container_width=True,   # Fits the container width (avoids scrolling if possible)
    num_rows="fixed",           # Keeps the row order fixed
    height=600
)

st.markdown("---")

if st.button("Calculate Recipes", type="primary", use_container_width=True):
    target_stats = recipes[target_donut_name]
    
    economy_res = solve_donut(edited_df, target_stats, mode="min")
    luxury_res = solve_donut(edited_df, target_stats, mode="max")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_recipe(economy_res, "Economy Recipe", "🟢")
        st.caption("*Uses common berries (top of list).*")
        
    with col2:
        display_recipe(luxury_res, "Luxury Recipe", "🟣")
        st.caption("*Uses rare berries (bottom of list).*")

    with st.expander("Show Required Flavor Stats"):
        st.write(target_stats)
