import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMinimize, LpMaximize, LpVariable, lpSum, LpStatus, value
from io import StringIO

# ---------------------------------------------------------------------
# 1. SETUP & TRANSLATIONS
# ---------------------------------------------------------------------

st.set_page_config(page_title="Z-A Donut Calculator", page_icon="🍩", layout="centered") 

# Translation Dictionary
TRANSLATIONS = {
    "English 🇺🇸": {
        "title": "🍩 Pokémon Legends: Z-A Donut Calculator",
        "intro": """When you don't have many rare berries in your satchel, it can be difficult or annoying to check if you are able to create the donuts to battle the Legendary Pokémon. \nThis guide helps you figure out if it is possible to create each donut based on your inventory. \nIt also suggests an economical (using fewer rare berries) and a luxurious (using rare berries, giving full power) recipe.""",
        "hope": "Hope this helps!",
        "instructions_header": "Instructions:",
        "step1": "1. Enter your **Inventory** in the table below (Look for the **✏️** column).",
        "step2": "2. Select the **Donut** you want to craft.",
        "step3": "3. Click **Calculate**.",
        "select_label": "Select Target Donut:",
        "inventory_header": "Your Inventory",
        "toggle_stats": "Show Berry Stats",
        "toggle_help": "Check this to see detailed flavor values.",
        "calc_button": "Calculate Recipes",
        "eco_title": "Economy Recipe",
        "eco_desc": "*Uses common berries (top of list).*",
        "lux_title": "Luxury Recipe",
        "lux_desc": "*Uses rare berries (bottom of list).*",
        "stats_expand": "Show Required Flavor Stats",
        "error_msg": "Not possible with current inventory.",
        "slots": "Slots",
        "cal": "Calories",
        "boost": "Lv. Boost",
        # Column Headers
        "col_name": "Berry Name",
        "col_inv": "✏️ Inventory",
        "col_inv_help": "Enter the amount you have in your bag.",
        "col_sweet": "🔒 Sweet",
        "col_spicy": "🔒 Spicy",
        "col_sour": "🔒 Sour",
        "col_bitter": "🔒 Bitter",
        "col_fresh": "🔒 Dry/Fresh", # Fresh replaces Dry in newer games usually
        "col_boost": "🔒 Lv. Boost",
        "col_cal": "🔒 Cal"
    },
    "Deutsch 🇩🇪": {
        "title": "🍩 Pokémon Legenden: Z-A Donut Rechner",
        "intro": """Wenn man nicht viele seltene Beeren im Beutel hat, kann es nervig sein herauszufinden, ob man die Donuts für den Kampf gegen die Legendären Pokémon herstellen kann. \nDieser Guide hilft dir zu prüfen, ob ein Rezept mit deinem Inventar möglich ist. \nEr schlägt außerdem ein sparsames (wenige seltene Beeren) und ein luxuriöses (maximale Power) Rezept vor.""",
        "hope": "Hoffentlich hilft das!",
        "instructions_header": "Anleitung:",
        "step1": "1. Trage dein **Inventar** unten in die Tabelle ein (Spalte mit **✏️**).",
        "step2": "2. Wähle den **Donut**, den du backen möchtest.",
        "step3": "3. Klicke auf **Berechnen**.",
        "select_label": "Wähle den Ziel-Donut:",
        "inventory_header": "Dein Inventar",
        "toggle_stats": "Beeren-Werte anzeigen",
        "toggle_help": "Anklicken, um Details zu Geschmack und Kalorien zu sehen.",
        "calc_button": "Rezepte berechnen",
        "eco_title": "Sparsammes Rezept",
        "eco_desc": "*Nutzt häufige Beeren (oben in der Liste).* und spart Slots.",
        "lux_title": "Luxus Rezept",
        "lux_desc": "*Nutzt seltene Beeren (unten in der Liste) und füllt Slots auf.*",
        "stats_expand": "Benötigte Geschmackswerte anzeigen",
        "error_msg": "Mit dem aktuellen Inventar nicht machbar.",
        "slots": "Plätze",
        "cal": "Kalorien",
        "boost": "Lv. Bonus",
        "col_name": "Beere",
        "col_inv": "✏️ Anzahl",
        "col_inv_help": "Trage hier ein, wie viele du im Beutel hast.",
        "col_sweet": "🔒 Süß",
        "col_spicy": "🔒 Scharf",
        "col_sour": "🔒 Sauer",
        "col_bitter": "🔒 Bitter",
        "col_fresh": "🔒 Herb/Frisch",
        "col_boost": "🔒 Lv. Bonus",
        "col_cal": "🔒 Kal"
    },
    "Français 🇫🇷": {
        "title": "🍩 Calculateur de Beignets Pokémon Z-A",
        "intro": "Il est parfois difficile de savoir si l'on peut cuisiner les beignets pour les Pokémon Légendaires. Ce guide vous aide à vérifier la faisabilité selon votre inventaire.",
        "hope": "J'espère que cela aidera !",
        "instructions_header": "Instructions :",
        "step1": "1. Entrez votre **Inventaire** dans le tableau (Colonne **✏️**).",
        "step2": "2. Sélectionnez le **Beignet**.",
        "step3": "3. Cliquez sur **Calculer**.",
        "select_label": "Choisir le Beignet :",
        "inventory_header": "Votre Inventaire",
        "toggle_stats": "Afficher les stats",
        "toggle_help": "Voir les détails des saveurs.",
        "calc_button": "Calculer les Recettes",
        "eco_title": "Recette Économique",
        "eco_desc": "*Utilise des baies communes.*",
        "lux_title": "Recette Luxe",
        "lux_desc": "*Utilise des baies rares.*",
        "stats_expand": "Voir les stats requises",
        "error_msg": "Impossible avec l'inventaire actuel.",
        "slots": "Slots",
        "cal": "Calories",
        "boost": "Boost Niv.",
        "col_name": "Baie",
        "col_inv": "✏️ Qté",
        "col_inv_help": "Quantité dans votre sac.",
        "col_sweet": "🔒 Sucré",
        "col_spicy": "🔒 Épicé",
        "col_sour": "🔒 Acide",
        "col_bitter": "🔒 Amer",
        "col_fresh": "🔒 Apre",
        "col_boost": "🔒 Boost",
        "col_cal": "🔒 Cal"
    },
    "Italiano 🇮🇹": {
        "title": "🍩 Calcolatore Ciambelle Pokémon Z-A",
        "intro": "Controlla se hai abbastanza bacche per cucinare le ciambelle per i Pokémon Leggendari.",
        "hope": "Spero sia d'aiuto!",
        "instructions_header": "Istruzioni:",
        "step1": "1. Inserisci il tuo **Inventario** nella tabella (Colonna **✏️**).",
        "step2": "2. Seleziona la **Ciambella**.",
        "step3": "3. Clicca su **Calcola**.",
        "select_label": "Seleziona Ciambella:",
        "inventory_header": "Il tuo Inventario",
        "toggle_stats": "Mostra statistiche",
        "toggle_help": "Vedi i dettagli dei sapori.",
        "calc_button": "Calcola Ricette",
        "eco_title": "Ricetta Economica",
        "eco_desc": "*Usa bacche comuni.*",
        "lux_title": "Ricetta Lusso",
        "lux_desc": "*Usa bacche rare.*",
        "stats_expand": "Vedi statistiche richieste",
        "error_msg": "Impossibile con l'inventario attuale.",
        "slots": "Slot",
        "cal": "Calorie",
        "boost": "Liv. Boost",
        "col_name": "Bacca",
        "col_inv": "✏️ Qtà",
        "col_inv_help": "Quantità nella borsa.",
        "col_sweet": "🔒 Dolce",
        "col_spicy": "🔒 Pepato",
        "col_sour": "🔒 Aspro",
        "col_bitter": "🔒 Amaro",
        "col_fresh": "🔒 Secco",
        "col_boost": "🔒 Lv. Boost",
        "col_cal": "🔒 Cal"
    },
    "Español 🇪🇸": {
        "title": "🍩 Calculadora de Donas Pokémon Z-A",
        "intro": "Comprueba si tienes suficientes bayas para cocinar las donas para los Pokémon Legendarios.",
        "hope": "¡Espero que ayude!",
        "instructions_header": "Instrucciones:",
        "step1": "1. Introduce tu **Inventario** en la tabla (Columna **✏️**).",
        "step2": "2. Selecciona la **Dona**.",
        "step3": "3. Haz clic en **Calcular**.",
        "select_label": "Seleccionar Dona:",
        "inventory_header": "Tu Inventario",
        "toggle_stats": "Mostrar estadísticas",
        "toggle_help": "Ver detalles de sabor.",
        "calc_button": "Calcular Recetas",
        "eco_title": "Receta Económica",
        "eco_desc": "*Usa bayas comunes.*",
        "lux_title": "Receta de Lujo",
        "lux_desc": "*Usa bayas raras.*",
        "stats_expand": "Ver estadísticas requeridas",
        "error_msg": "Imposible con el inventario actual.",
        "slots": "Espacios",
        "cal": "Calorías",
        "boost": "Niv. Boost",
        "col_name": "Baya",
        "col_inv": "✏️ Cant.",
        "col_inv_help": "Cantidad en tu bolsa.",
        "col_sweet": "🔒 Dulce",
        "col_spicy": "🔒 Picante",
        "col_sour": "🔒 Ácido",
        "col_bitter": "🔒 Amargo",
        "col_fresh": "🔒 Seco",
        "col_boost": "🔒 Niv.+",
        "col_cal": "🔒 Cal"
    },
    "Korean 🇰🇷": {
        "title": "🍩 포켓몬 레전드 Z-A 도넛 계산기",
        "intro": "전설의 포켓몬을 위한 도넛을 만들 재료가 충분한지 확인하세요.",
        "hope": "도움이 되길 바랍니다!",
        "instructions_header": "사용법:",
        "step1": "1. 아래 표에 **가방(인벤토리)** 수량을 입력하세요 (**✏️** 열).",
        "step2": "2. 만들고 싶은 **도넛**을 선택하세요.",
        "step3": "3. **계산하기** 버튼을 누르세요.",
        "select_label": "도넛 선택:",
        "inventory_header": "보유 열매",
        "toggle_stats": "상세 스탯 표시",
        "toggle_help": "맛과 칼로리 정보를 확인합니다.",
        "calc_button": "레시피 계산",
        "eco_title": "경제적인 레시피",
        "eco_desc": "*흔한 열매 위주 사용.*",
        "lux_title": "고급 레시피",
        "lux_desc": "*희귀 열매 위주 사용.*",
        "stats_expand": "필요 조건 보기",
        "error_msg": "현재 재료로는 만들 수 없습니다.",
        "slots": "슬롯",
        "cal": "칼로리",
        "boost": "레벨 부스트",
        "col_name": "열매 이름",
        "col_inv": "✏️ 수량",
        "col_inv_help": "가방에 있는 수량을 입력하세요.",
        "col_sweet": "🔒 단맛",
        "col_spicy": "🔒 매운맛",
        "col_sour": "🔒 신맛",
        "col_bitter": "🔒 쓴맛",
        "col_fresh": "🔒 떫은맛",
        "col_boost": "🔒 Lv.+",
        "col_cal": "🔒 Cal"
    },
    "Japanese 🇯🇵": {
        "title": "🍩 ポケモンレジェンズZ-A ドーナツ計算機",
        "intro": "伝説のポケモン用のドーナツを作るためのきのみが足りているか確認しましょう。",
        "hope": "お役に立てば幸いです！",
        "instructions_header": "使い方:",
        "step1": "1. 下の表に**持ち物**の数を入力してください (**✏️** の列)。",
        "step2": "2. 作りたい**ドーナツ**を選んでください。",
        "step3": "3. **計算する**をクリックしてください。",
        "select_label": "ドーナツを選択:",
        "inventory_header": "バッグの中身",
        "toggle_stats": "ステータスを表示",
        "toggle_help": "味やカロリーの詳細を表示します。",
        "calc_button": "レシピを計算",
        "eco_title": "節約レシピ",
        "eco_desc": "*手に入りやすいきのみを使用。*",
        "lux_title": "豪華レシピ",
        "lux_desc": "*レアなきのみを使用。*",
        "stats_expand": "必要ステータスを見る",
        "error_msg": "現在の持ち物では作れません。",
        "slots": "スロット",
        "cal": "カロリー",
        "boost": "Lv.ブースト",
        "col_name": "きのみ",
        "col_inv": "✏️ 所持数",
        "col_inv_help": "バッグに入っている数を入力。",
        "col_sweet": "🔒 甘さ",
        "col_spicy": "🔒 辛さ",
        "col_sour": "🔒 酸っぱさ",
        "col_bitter": "🔒 苦さ",
        "col_fresh": "🔒 渋さ",
        "col_boost": "🔒 Lv.UP",
        "col_cal": "🔒 Cal"
    },
    "Mandarin 🇨🇳": {
        "title": "🍩 宝可梦传说 Z-A 甜甜圈计算器",
        "intro": "检查你是否有足够的树果来制作传说宝可梦的甜甜圈。",
        "hope": "希望能帮到你！",
        "instructions_header": "使用说明：",
        "step1": "1. 在下表中输入你的**库存**数量（**✏️** 列）。",
        "step2": "2. 选择你要制作的**甜甜圈**。",
        "step3": "3. 点击**计算**。",
        "select_label": "选择甜甜圈：",
        "inventory_header": "你的库存",
        "toggle_stats": "显示详细数值",
        "toggle_help": "查看口味和卡路里详情。",
        "calc_button": "计算配方",
        "eco_title": "经济配方",
        "eco_desc": "*使用常见树果。*",
        "lux_title": "豪华配方",
        "lux_desc": "*使用稀有树果。*",
        "stats_expand": "查看所需数值",
        "error_msg": "当前库存无法制作。",
        "slots": "槽位",
        "cal": "卡路里",
        "boost": "等级提升",
        "col_name": "树果名称",
        "col_inv": "✏️ 数量",
        "col_inv_help": "输入背包中的数量。",
        "col_sweet": "🔒 甜",
        "col_spicy": "🔒 辣",
        "col_sour": "🔒 酸",
        "col_bitter": "🔒 苦",
        "col_fresh": "🔒 涩",
        "col_boost": "🔒 Lv.+",
        "col_cal": "🔒 Cal"
    }
}

# The Data
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

def display_recipe(results, title, desc, labels_dict, color_emoji):
    if results:
        st.success(f"### {color_emoji} {title}")
        res_df = pd.DataFrame(results)
        
        # Rename columns for display based on language
        display_cols = {"Berry": labels_dict["col_name"], "Count": labels_dict["col_inv"]}
        res_df_display = res_df.rename(columns=display_cols)
        
        st.dataframe(res_df_display[[labels_dict["col_name"], labels_dict["col_inv"]]], hide_index=True, use_container_width=True)
        
        total_slots = sum(r['Count'] for r in results)
        total_cal = sum(r['Count'] * r['Cal'] for r in results)
        total_boost = sum(r['Count'] * r['Lv_Boost'] for r in results)
        
        st.markdown(f"**{labels_dict['slots']}:** {total_slots}/8  |  **{labels_dict['cal']}:** {total_cal}  |  **{labels_dict['boost']}:** +{total_boost}")
        st.caption(desc)
    else:
        st.error(f"### {color_emoji} {title}\n{labels_dict['error_msg']}")

# ---------------------------------------------------------------------
# 3. UI LAYOUT
# ---------------------------------------------------------------------

# --- LANGUAGE SELECTOR (Top of page) ---
selected_lang = st.selectbox("Language / Sprache / Langue / 言語", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang] # Load the dictionary for the selected language

st.title(t["title"])

# --- INTRO TEXT & INSTRUCTIONS ---
st.markdown(t["intro"])
st.markdown(t["hope"])

st.markdown(f"**{t['instructions_header']}**")
st.markdown(t["step1"])
st.markdown(t["step2"])
st.markdown(t["step3"])
st.markdown("---")

# --- INPUT SECTION ---

target_donut_name = st.selectbox(t["select_label"], list(recipes.keys()))

st.subheader(t["inventory_header"])

# Mobile Friendly Toggle
show_stats = st.checkbox(t["toggle_stats"], value=False, help=t["toggle_help"])

# Define which columns to display (using English keys for internal logic)
cols_to_show = ["Name", "Inventory"]
if show_stats:
    cols_to_show += ["Sweet", "Spicy", "Sour", "Bitter", "Fresh", "Lv_Boost", "Cal"]

# Filter the dataframe for display
df_display = df[cols_to_show]

# Configuration for the table columns (Mapping English Data -> Translated Labels)
column_cfg = {
    "Name": st.column_config.TextColumn(t["col_name"], disabled=True, width="medium"),
    "Inventory": st.column_config.NumberColumn(
        t["col_inv"], 
        help=t["col_inv_help"],
        min_value=0, step=1, required=True, width="small"
    ),
    "Sweet": st.column_config.NumberColumn(t["col_sweet"], disabled=True, width="small"),
    "Spicy": st.column_config.NumberColumn(t["col_spicy"], disabled=True, width="small"),
    "Sour": st.column_config.NumberColumn(t["col_sour"], disabled=True, width="small"),
    "Bitter": st.column_config.NumberColumn(t["col_bitter"], disabled=True, width="small"),
    "Fresh": st.column_config.NumberColumn(t["col_fresh"], disabled=True, width="small"),
    "Lv_Boost": st.column_config.NumberColumn(t["col_boost"], disabled=True, width="small"),
    "Cal": st.column_config.NumberColumn(t["col_cal"], disabled=True, width="small"),
}

# The Data Editor
edited_df = st.data_editor(
    df_display,
    column_config=column_cfg,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed", 
    height=600 if show_stats else 400
)

# SYNC LOGIC
df.set_index("Name", inplace=True)
df_display_indexed = edited_df.set_index("Name")
df.update(df_display_indexed[["Inventory"]])
df.reset_index(inplace=True)

st.markdown("---")

if st.button(t["calc_button"], type="primary", use_container_width=True):
    target_stats = recipes[target_donut_name]
    
    economy_res = solve_donut(df, target_stats, mode="min")
    luxury_res = solve_donut(df, target_stats, mode="max")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_recipe(economy_res, t["eco_title"], t["eco_desc"], t, "🟢")
        
    with col2:
        display_recipe(luxury_res, t["lux_title"], t["lux_desc"], t, "🟣")

    with st.expander(t["stats_expand"]):
        st.write(target_stats)
