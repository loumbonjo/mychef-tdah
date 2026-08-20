import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MyChef TDAH", page_icon="🥗", layout="centered")

# --- SUPABASE CONNECTION ---
# Ces valeurs seront lues de manière sécurisée depuis tes Secrets Streamlit
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.title("🥗 Mon Assistant Santé & Repas")

# --- ONGLETS PRINCIPAUX ---
tab_repas, tab_eau, tab_courses = st.tabs(["🍽️ Repas du jour", "💧 Hydratation", "🛒 Courses"])

# ==========================================
# 1. ONGLET REPAS
# ==========================================
with tab_repas:
    st.header("Mes Repas")
    
    # Récupération des repas depuis Supabase
    response = supabase.table("repas").select("*").order("id").execute()
    repas_list = response.data

    if not repas_list:
        st.info("Aucun repas planifié pour le moment.")
    else:
        for r in repas_list:
            with st.expander(f"**{r.get('creneau', 'Repas')}** : {r.get('nom_plat', 'Plat')}", expanded=True):
                st.write(f"**Ingrédients :** {r.get('ingredients', '')}")
                if r.get('boisson'):
                    st.write(f"🥤 **Boisson associée :** {r['boisson']}")
                
                # Checkbox Médicaments
                med_state = r.get("rappel_medocs", False)
                new_med = st.checkbox("💊 Traitement / Suppléments pris", value=med_state, key=f"med_{r['id']}")
                if new_med != med_state:
                    supabase.table("repas").update({"rappel_medocs": new_med}).eq("id", r["id"]).execute()
                    st.rerun()

                # Checkbox Repas Validé
                val_state = r.get("valide", False)
                new_val = st.checkbox("✅ Repas terminé", value=val_state, key=f"val_{r['id']}")
                if new_val != val_state:
                    supabase.table("repas").update({"valide": new_val}).eq("id", r["id"]).execute()
                    st.rerun()

# ==========================================
# 2. ONGLET HYDRATATION
# ==========================================
with tab_eau:
    st.header("Suivi d'Hydratation")
    
    eau_data = supabase.table("hydratation").select("*").order("id").execute().data
    
    if not eau_data:
        st.info("Aucune boisson enregistrée.")
    else:
        for b in eau_data:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{b.get('moment', '')}** : {b.get('boisson_nom', '')}")
            with col2:
                bu_state = b.get("bu", False)
                new_bu = st.checkbox("Bu ?", value=bu_state, key=f"eau_{b['id']}")
                if new_bu != bu_state:
                    supabase.table("hydratation").update({"bu": new_bu}).eq("id", b["id"]).execute()
                    st.rerun()

# ==========================================
# 3. ONGLET LISTE DE COURSES
# ==========================================
with tab_courses:
    st.header("Liste de Courses par Rayon")
    
    courses_data = supabase.table("courses").select("*").order("rayon").execute().data
    
    if not courses_data:
        st.info("Ta liste de courses est vide !")
    else:
        # Groupement par rayon
        rayons = list(set([c.get("rayon", "Divers") for c in courses_data]))
        for rayon in rayons:
            st.subheader(f"📦 {rayon}")
            items = [c for c in courses_data if c.get("rayon") == rayon]
            for item in items:
                checked = item.get("achete", False)
                label = f"~~{item['article']}~~" if checked else item['article']
                new_check = st.checkbox(label, value=checked, key=f"course_{item['id']}")
                if new_check != checked:
                    supabase.table("courses").update({"achete": new_check}).eq("id", item["id"]).execute()
                    st.rerun()
