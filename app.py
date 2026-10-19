import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA E GRAFICA ---
st.set_page_config(
    page_title="FantaLiceo ⚽🎓",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Iniezione CSS per interfaccia "App-like", Colori Ruoli, Campo da Calcio, Panchina e Firma
st.markdown("""
    <style>
    .firma-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
        color: #38bdf8;
        text-align: center;
        padding: 12px;
        font-size: 15px;
        font-weight: bold;
        z-index: 9999;
        border-top: 2px solid #6366f1;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
    }
    .card-bonus {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 5px solid #4CAF50;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .card-malus {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 5px solid #F44336;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .main-title {
        text-align: center;
        background: -webkit-linear-gradient(#4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Colori Ruoli per il Calciomercato e Targhette */
    .card-p { background-color: #f39c12 !important; color: #ffffff !important; padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 5px; border: 2px solid #f39c12; }
    .card-d { background-color: #2ecc71 !important; color: #ffffff !important; padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 5px; border: 2px solid #2ecc71; }
    .card-c { background-color: #3498db !important; color: #ffffff !important; padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 5px; border: 2px solid #3498db; }
    .card-a { background-color: #e74c3c !important; color: #ffffff !important; padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 5px; border: 2px solid #e74c3c; }

    /* Campo da Calcio a 5 */
    .pitch {
        background: linear-gradient(to bottom, #1e7123, #155219);
        border: 3px solid #ffffff;
        border-radius: 12px;
        padding: 20px;
        position: relative;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .pitch-line {
        border-top: 2px dashed rgba(255, 255, 255, 0.5);
        margin: 15px 0;
    }
    .player-card-pitch {
        background: #111827;
        color: #ffffff;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
        margin: 5px;
    }

    /* Panchina dello Stadio */
    .bench-container {
        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
        border: 2px solid #4b5563;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    }
    .player-card-bench {
        background: #374151;
        color: #ffffff;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        font-weight: bold;
        margin: 5px;
    }
    </style>
    <div class="firma-container">
        ✨ Realizzato da Gabriele Ferro ✨
    </div>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE VARIABILI DI SESSIONE (PERSISTENZA ADMIN) ---
if "kill_switch" not in st.session_state:
    st.session_state["kill_switch"] = False
if "utenti_registrati" not in st.session_state:
    st.session_state["utenti_registrati"] = {}
if "utente_corrente" not in st.session_state:
    st.session_state["utente_corrente"] = None
if "mercato_aperto" not in st.session_state:
    st.session_state["mercato_aperto"] = False

# Impostazioni di lega persistenti gestibili dal Super Admin
if "dimensione_rosa" not in st.session_state:
    st.session_state["dimensione_rosa"] = 8  # Default 8 giocatori in rosa totale
if "budget_totale" not in st.session_state:
    st.session_state["budget_totale"] = 100  # Default 100 crediti
if "moduli_disponibili" not in st.session_state:
    st.session_state["moduli_disponibili"] = ["2-1-1", "1-2-1"]
if "modulo_scelto" not in st.session_state:
    st.session_state["modulo_scelto"] = "1-2-1"

# Limiti di giocatori per ruolo modificabili dall'admin
if "limiti_ruoli" not in st.session_state:
    st.session_state["limiti_ruoli"] = {"Portiere": 1, "Difensore": 3, "Centrocampista": 3, "Attaccante": 1}

if "scadenza_formazione" not in st.session_state:
    st.session_state["scadenza_formazione"] = datetime.now() + timedelta(days=2)
if "keyword_senza_voto" not in st.session_state:
    st.session_state["keyword_senza_voto"] = "@"
if "voti_caricati" not in st.session_state:
    st.session_state["voti_caricati"] = None

if "bonus_list" not in st.session_state:
    st.session_state["bonus_list"] = [
        {"Descrizione": "Gol segnato", "Punti": "+3"},
        {"Descrizione": "Assist", "Punti": "+1"},
        {"Descrizione": "Coreografia classe", "Punti": "+20"}
    ]
if "malus_list" not in st.session_state:
    st.session_state["malus_list"] = [
        {"Descrizione": "Ammonizione", "Punti": "-1"},
        {"Descrizione": "Espulsione", "Punti": "-3"},
        {"Descrizione": "Ritardo", "Punti": "-2"}
    ]

# --- 1. KILL SWITCH (Controllo Emergenza) ---
if st.session_state["kill_switch"]:
    st.error("🚨 SITO ATTUALMENTE IN MANUTENZIONE STRAORDINARIA 🚨")
    st.markdown("L'applicazione è stata temporaneamente sospesa dall'amministratore di sistema.")
    
    sblocco = st.text_input("Codice di ripristino:", type="password")
    if sblocco == "gabriele_sblocco_2026":
        st.session_state["kill_switch"] = False
        st.rerun()
    st.stop()

# --- FUNZIONI DI SUPPORTO ---
def controllo_volgarita(testo):
    parole_vietate = ["stupido", "idiota", "scemo"]
    testo_pulito = testo.lower().strip()
    if re.search(r'[!@#$%^&*()_+={}\[\]:;"\'<>,.?/\\|]', testo_pulito):
        return False
    for parola in parole_vietate:
        if parola in testo_pulito:
            return False
    return True

def normalizza_ruolo(ruolo):
    r = str(ruolo).strip().capitalize()
    if r in ["Portiere", "P"]:
        return "Portiere"
    elif r in ["Difensore", "D"]:
        return "Difensore"
    elif r in ["Centrocampista", "C", "Centro"]:
        return "Centrocampista"
    elif r in ["Attaccante", "A"]:
        return "Attaccante"
    return r

def get_card_class(ruolo):
    r = normalizza_ruolo(ruolo)
    if r == "Portiere":
        return "card-p"
    elif r == "Difensore":
        return "card-d"
    elif r == "Centrocampista":
        return "card-c"
    else:
        return "card-a"

def carica_listone():
    try:
        df = pd.read_excel("giocatori.xlsx")
        df["Ruolo"] = df["Ruolo"].apply(normalizza_ruolo)
        return df
    except FileNotFoundError:
        return None

# --- 2. SISTEMA DI LOGIN & REGISTRAZIONE ---
if st.session_state["utente_corrente"] is None:
    st.markdown("<h1 class='main-title'>FantaLiceo 2026 🎓</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### 📝 Iscrizione Studenti (Posti Illimitati)")
        with st.form("registrazione"):
            nome = st.text_input("Nome")
            cognome = st.text_input("Cognome")
            anno = st.selectbox("Anno", ["1", "2", "3", "4", "5"])
            sezione = st.selectbox("Sezione", ["A", "B", "C", "D", "E", "Altra"])
            indirizzo = st.selectbox("Indirizzo", ["Scientifico Tradizionale", "Scientifico Scienze Applicate", "Linguistico", "Classico"])
            
            pin_super_admin = st.text_input("PIN (Lasciare vuoto se studente)", type="password")
            
            submit = st.form_submit_button("Entra nel FantaLiceo 🚀", use_container_width=True)

            if submit:
                if not nome or not cognome:
                    st.error("Inserisci Nome e Cognome.")
                elif not controllo_volgarita(nome) or not controllo_volgarita(cognome):
                    st.error("❌ Nome non valido o contenente caratteri non ammessi. Riprova con il tuo vero nome.")
                else:
                    chiave_utente = f"{nome.title()} {cognome.title()}"
                    
                    is_super_admin = False
                    if nome.lower() == "alessandro" and cognome.lower() == "carbone" and anno == "5" and sezione == "A" and indirizzo == "Scientifico Tradizionale":
                        if pin_super_admin == "AleSuper2026!":
                            is_super_admin = True
                            st.success("Accesso Super Admin Verificato!")
                        else:
                            st.error("🚨 Tentativo di furto d'identità rilevato. PIN Super Admin errato.")
                            st.stop()

                    if chiave_utente not in st.session_state["utenti_registrati"]:
                        st.session_state["utenti_registrati"][chiave_utente] = {
                            "nome": nome.title(),
                            "cognome": cognome.title(),
                            "classe": f"{anno}{sezione} {indirizzo}",
                            "crediti": st.session_state["budget_totale"],
                            "rosa": [],
                            "formazione_titolare": [],
                            "panchina_ordinata": [],
                            "is_super_admin": is_super_admin
                        }
                        st.toast('Registrazione completata! 🎉')
                    
                    st.session_state["utente_corrente"] = chiave_utente
                    st.rerun()
    st.stop()

# --- GESTIONE UTENTE LOGGATO ---
utente_id = st.session_state["utente_corrente"]
dati_utente = st.session_state["utenti_registrati"][utente_id]

# --- BARRA LATERALE ---
st.sidebar.markdown(f"### 👋 Ciao, {dati_utente['nome']}!")
st.sidebar.markdown(f"🏫 **Classe:** {dati_utente['classe']}")
st.sidebar.metric(label="💰 Crediti Disponibili", value=f"{dati_utente['crediti']} 🪙")
st.sidebar.markdown("---")

voci_menu = ["🏠 Home & Regolamento", "🛒 Calciomercato", "⚽ Schiera Formazione", "🏆 Classifica Partecipanti"]
if dati_utente.get("is_super_admin", False) or utente_id == "Admin Segreto":
    voci_menu.append("👑 Pannello Super-Admin")
elif "admin" in utente_id.lower():
    voci_menu.append("⚙️ Pannello Admin")

menu = st.sidebar.radio("Navigazione", voci_menu)

if st.sidebar.button("🚪 Esci", use_container_width=True):
    st.session_state["utente_corrente"] = None
    st.rerun()

# --- SEZIONI DELL'APP ---

if menu == "🏠 Home & Regolamento":
    st.markdown("<h1 class='main-title'>Regolamento & Bonus/Malus</h1>", unsafe_allow_html=True)
    st.write("Consulta qui le regole del torneo. Punta alla vetta!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color: #4CAF50;'>🟢 BONUS ATTIVI</h3>", unsafe_allow_html=True)
        for b in st.session_state["bonus_list"]:
            st.markdown(f"""
                <div class='card-bonus'>
                    <b>{b['Descrizione']}</b> <span style='float:right; font-size:18px;'><b>{b['Punti']} pt</b></span>
                </div>
            """, unsafe_allow_html=True)
            
    with col2:
        st.markdown("<h3 style='color: #F44336;'>🔴 MALUS ATTIVI</h3>", unsafe_allow_html=True)
        for m in st.session_state["malus_list"]:
            st.markdown(f"""
                <div class='card-malus'>
                    <b>{m['Descrizione']}</b> <span style='float:right; font-size:18px;'><b>{m['Punti']} pt</b></span>
                </div>
            """, unsafe_allow_html=True)

elif menu == "🛒 Calciomercato":
    st.title("🛒 Calciomercato")
    
    df_giocatori = carica_listone()
    if df_giocatori is None:
        st.error("🚨 File 'giocatori.xlsx' non trovato nella cartella del progetto! Crea il file Excel con le colonne Nome, Ruolo, Classe, Quotazione.")
        st.stop()

    colonne_richieste = ["Nome", "Ruolo", "Classe", "Quotazione"]
    colonne_mancanti = [c for c in colonne_richieste if c not in df_giocatori.columns]
    if colonne_mancanti:
        st.error(f"🚨 Il file Excel non contiene le seguenti colonne obbligatorie: {colonne_mancanti}")
        st.stop()

    st.info(f"📌 Regola Rosa: Ogni squadra deve essere composta esattamente da **{st.session_state['dimensione_rosa']} giocatori** (secondo i limiti di ruolo stabiliti dall'amministratore).")

    if not st.session_state["mercato_aperto"]:
        st.warning("🔴 IL MERCATO È ATTUALMENTE CHIUSO. Puoi solo visualizzare la tua rosa attuale.")
        st.markdown(f"### 📋 La tua Rosa Attuale: {dati_utente['rosa']}")
        st.markdown(f"**Crediti residui:** {dati_utente['crediti']} 🪙")
    else:
        st.success("🟢 IL MERCATO È APERTO! Seleziona i tuoi giocatori e gestisci il budget.")
        
        st.subheader("🔍 Filtri Listone")
        c1, c2 = st.columns(2)
        with c1:
            ruoli_disponibili = ["Tutti"] + list(df_giocatori["Ruolo"].unique())
            filtro_ruolo = st.selectbox("Filtra per Ruolo", ruoli_disponibili)
        with c2:
            ricerca_nome = st.text_input("Cerca giocatore per nome", "")

        df_filtrato = df_giocatori.copy()
        if filtro_ruolo != "Tutti":
            df_filtrato = df_filtrato[df_filtrato["Ruolo"] == filtro_ruolo]
        if ricerca_nome:
            df_filtrato = df_filtrato[df_filtrato["Nome"].str.contains(ricerca_nome, case=False, na=False)]

        # Tabella ordinabile e pulita (stile Codice 0)
        st.dataframe(df_filtrato, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📝 Componi la tua Rosa")

        lista_nomi = df_giocatori["Nome"].tolist()
        rosa_attuale = dati_utente.get("rosa", [])

        giocatori_scelti = st.multiselect(
            f"Seleziona esattamente {st.session_state['dimensione_rosa']} giocatori dal listone:",
            options=lista_nomi,
            default=rosa_attuale,
            max_selections=st.session_state['dimensione_rosa']
        )

        # Calcolo spesa e crediti
        spesa_totale = 0
        conteggio_ruoli = {"Portiere": 0, "Difensore": 0, "Centrocampista": 0, "Attaccante": 0}
        
        for nome_gioc in giocatori_scelti:
            riga = df_giocatori[df_giocatori["Nome"] == nome_gioc]
            if not riga.empty:
                spesa_totale += int(riga["Quotazione"].values[0])
                r = riga["Ruolo"].values[0]
                if r in conteggio_ruoli:
                    conteggio_ruoli[r] += 1

        crediti_rimasti_calcolati = st.session_state["budget_totale"] - spesa_totale

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Spesa Totale", f"{spesa_totale} 🪙")
        col_m2.metric("Crediti Residui", f"{crediti_rimasti_calcolati} 🪙")

        # Verifica vincoli di ruolo impostati dall'admin
        limiti = st.session_state["limiti_ruoli"]
        vincoli_rispettati = True
        st.markdown("#### 📊 Verifica Limiti Ruoli in Rosa:")
        r_cols = st.columns(4)
        idx_r = 0
        for ruolo_k, lim_v in limiti.items() if isinstance(limiti, dict) else []:
            with r_cols[idx_r % 4]:
                attuale_r = conteggio_ruoli.get(ruolo_k, 0)
                if attuale_r == lim_v:
                    st.success(f"{ruolo_k}: {attuale_r}/{lim_v}")
                else:
                    st.warning(f"{ruolo_k}: {attuale_r}/{lim_v}")
                    vincoli_rispettati = False
            idx_r += 1

        if len(giocatori_scelti) != st.session_state["dimensione_rosa"]:
            st.warning(f"⚠️ Attenzione: hai selezionato {len(giocatori_scelti)} giocatori. La rosa deve essere composta da esattamente {st.session_state['dimensione_rosa']} giocatori.")

        if crediti_rimasti_calcolati < 0:
            st.error("🚨 ATTENZIONE: Hai superato il budget disponibile! Riduci i giocatori selezionati.")

        if st.button("💾 Salva Formazione / Rosa", use_container_width=True):
            if crediti_rimasti_calcolati >= 0 and len(giocatori_scelti) == st.session_state["dimensione_rosa"] and vincoli_rispettati:
                dati_utente["rosa"] = giocatori_scelti
                dati_utente["crediti"] = crediti_rimasti_calcolati
                st.success("🎉 Rosa salvata con successo!")
                st.rerun()
            else:
                st.error("Impossibile salvare: verifica budget, numero esatto di giocatori e limiti di ruolo stabiliti dall'admin.")

elif menu == "⚽ Schiera Formazione":
    st.title("⚽ Schiera la Formazione e Panchina")
    
    # Gestione Timer / Conto alla rovescia
    tempo_rimanente = st.session_state["scadenza_formazione"] - datetime.now()
    
    if tempo_rimanente.total_seconds() > 0:
        ore = int(tempo_rimanente.total_seconds() // 3600)
        minuti = int((tempo_rimanente.total_seconds() % 3600) // 60)
        secondi = int(tempo_rimanente.total_seconds() % 60)
        st.success(f"⏳ **Finestra Formazione Aperta!** Tempo rimanente: **{ore} ore, {minuti} minuti e {secondi} secondi**")
        finestra_aperta = True
    else:
        st.error("⏰ **Tempo scaduto!** La finestra per schierare o modificare la formazione è chiusa.")
        finestra_aperta = False

    rosa_utente = dati_utente.get("rosa", [])
    df_giocatori = carica_listone()
    
    if not rosa_utente or len(rosa_utente) < 5 or df_giocatori is None:
        st.warning("⚠️ Per schierare la formazione devi aver acquistato una rosa completa nel Calciomercato!")
    else:
        # Mappa giocatore -> ruolo
        mapping_ruoli = dict(zip(df_giocatori["Nome"], df_giocatori["Ruolo"]))
        
        # Suddividiamo la rosa dell'utente per ruolo
        rosa_portieri = [g for g in rosa_utente if mapping_ruoli.get(g) == "Portiere"]
        rosa_difensori = [g for g in rosa_utente if mapping_ruoli.get(g) == "Difensore"]
        rosa_centrocampisti = [g for g in rosa_utente if mapping_ruoli.get(g) == "Centrocampista"]
        rosa_attaccanti = [g for g in rosa_utente if mapping_ruoli.get(g) == "Attaccante"]

        # Selezione Modulo
        modulo = st.selectbox(
            "Scegli il Modulo Tattico per i Titolari (4 giocatori di movimento + 1 portiere):", 
            options=st.session_state["moduli_disponibili"],
            index=st.session_state["moduli_disponibili"].index(st.session_state["modulo_scelto"]) if st.session_state["modulo_scelto"] in st.session_state["moduli_disponibili"] else 0
        )
        st.session_state["modulo_scelto"] = modulo

        st.subheader("⭐ Seleziona i 5 Titolari per Ruolo:")
        
        # Slot basati rigorosamente sul modulo
        # Esempio: 1-2-1 -> 1 POR, 1 DIF, 2 CEN, 1 ATT
        # 2-1-1 -> 1 POR, 2 DIF, 1 CEN, 1 ATT
        num_dif, num_cen, num_att = 1, 2, 1
        if modulo == "2-1-1":
            num_dif, num_cen, num_att = 2, 1, 1
        elif modulo == "1-2-1":
            num_dif, num_cen, num_att = 1, 2, 1

        titolari_selezionati = []
        
        with st.form("form_formazione"):
            col_s = st.columns(5)
            
            # Portiere obbligatorio (POR)
            with col_s[0]:
                p_por = st.selectbox("POR (Portiere)", ["-- Seleziona --"] + rosa_portieri)
                if p_por != "-- Seleziona --":
                    titolari_selezionati.append(p_por)

            # Difensori (DIF)
            selected_d = []
            for i in range(num_dif):
                with col_s[1 + i]:
                    pdif = st.selectbox(f"DIF {i+1}", ["-- Seleziona --"] + [g for g in rosa_difensori if g not in selected_d])
                    if pdif != "-- Seleziona --":
                        selected_d.append(pdif)
                        titolari_selezionati.append(pdif)

            # Centrocampisti (CEN)
            selected_c = []
            for i in range(num_cen):
                with col_s[2 + num_dif - 1 + i]:
                    pcen = st.selectbox(f"CEN {i+1}", ["-- Seleziona --"] + [g for g in rosa_centrocampisti if g not in selected_c])
                    if pcen != "-- Seleziona --":
                        selected_c.append(pcen)
                        titolari_selezionati.append(pcen)

            # Attaccanti (ATT)
            selected_a = []
            for i in range(num_att):
                with col_s[4 - i]:
                    patt = st.selectbox(f"ATT {i+1}", ["-- Seleziona --"] + [g for g in rosa_attaccanti if g not in selected_a])
                    if patt != "-- Seleziona --":
                        selected_a.append(patt)
                        titolari_selezionati.append(patt)

            st.divider()
            
            # Panchina dinamica: differenza tra totale rosa e 5 titolari (senza caselle vuote fisse)
            num_panchina = st.session_state["dimensione_rosa"] - 5
            st.subheader(f"🪑 Gestione Panchina ({num_panchina} posti)")
            st.write("Indica i panchinari in **ordine gerarchico** di subentro per ruolo:")

            panchina_ordinata = []
            b_cols = st.columns(num_panchina if num_panchina > 0 else 1)
            
            disponibili_panchina = [g for g in rosa_utente if g not in titolari_selezionati]
            
            for i in range(num_panchina):
                with b_cols[i]:
                    sub_scelto = st.selectbox(f"{i+1}° Cambio", ["-- Nessuno --"] + [g for g in disponibili_panchina if g not in panchina_ordinata], key=f"sub_{i}")
                    if sub_scelto and sub_scelto != "-- Nessuno --":
                        panchina_ordinata.append(sub_scelto)

            submit_formazione = st.form_submit_button("💾 Salva Formazione e Panchina", use_container_width=True)

            if submit_formazione:
                if not finestra_aperta:
                    st.error("Impossibile salvare: il tempo limite per la formazione è scaduto.")
                elif len(titolari_selezionati) != 5:
                    st.error(f"Devi selezionare esattamente 5 titolari validi (ne hai selezionati {len(titolari_selezionati)}).")
                else:
                    dati_utente["formazione_titolare"] = titolari_selezionati
                    dati_utente["panchina_ordinata"] = panchina_ordinata
                    st.success("🎉 Formazione titolare e panchina salvate con successo!")

        # --- GRAFICA CAMPO DA CALCIO A 5 & PANCHINA STADIO ---
        titolari_salvati = dati_utente.get("formazione_titolare", [])
        if len(titolari_salvati) == 5:
            st.markdown("---")
            st.subheader("🟢 Visualizzazione Tattica - Campo da Calcio a 5")
            st.markdown('<div class="pitch">', unsafe_allow_html=True)
            
            # Classifichiamo i titolari salvati per ruolo
            t_por = [g for g in titolari_salvati if mapping_ruoli.get(g) == "Portiere"]
            t_dif = [g for g in titolari_salvati if mapping_ruoli.get(g) == "Difensore"]
            t_cen = [g for g in titolari_salvati if mapping_ruoli.get(g) == "Centrocampista"]
            t_att = [g for g in titolari_salvati if mapping_ruoli.get(g) == "Attaccante"]

            tp1 = t_por[0] if t_por else "N/D"
            
            if modulo == "1-2-1":
                tp_att = t_att[0] if t_att else "N/D"
                tp_c1 = t_cen[0] if len(t_cen) > 0 else "N/D"
                tp_c2 = t_cen[1] if len(t_cen) > 1 else "N/D"
                tp_dif = t_dif[0] if t_dif else "N/D"

                st.markdown(f'<div class="player-card-pitch {get_card_class("Attaccante")}">⚽ ATT: {tp_att}</div>', unsafe_allow_html=True)
                st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f'<div class="player-card-pitch {get_card_class("Centrocampista")}">🏃 CEN: {tp_c1}</div>', unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f'<div class="player-card-pitch {get_card_class("Centrocampista")}">🏃 CEN: {tp_c2}</div>', unsafe_allow_html=True)
                st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="player-card-pitch {get_card_class("Difensore")}">🛡️ DIF: {tp_dif}</div>', unsafe_allow_html=True)
                st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="player-card-pitch {get_card_class("Portiere")}">🧤 POR: {tp1}</div>', unsafe_allow_html=True)

            elif modulo == "2-1-1":
                tp_att = t_att[0] if t_att else "N/D"
                tp_cen = t_cen[0] if t_cen else "N/D"
                tp_d1 = t_dif[0] if len(t_dif) > 0 else "N/D"
                tp_d2 = t_dif[1] if len(t_dif) > 1 else "N/D"

                st.markdown(f'<div class="player-card-pitch {get_card_class("Attaccante")}">⚽ ATT: {tp_att}</div>', unsafe_allow_html=True)
                st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="player-card-pitch {get_card_class("Centrocampista")}">🏃 CEN: {tp_cen}</div>', unsafe_allow_html=True)
                st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown(f'<div class="player-card-pitch {get_card_class("Difensore")}">🛡️ DIF: {tp_d1}</div>', unsafe_allow_html=True)
                with col_d2:
                    st.markdown(f'<div class="player-card-pitch {get_card_class("Difensore")}">🛡️ DIF: {tp_d2}</div>', unsafe_allow_html=True)
                st.markdown('<div class="pitch-line"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="player-card-pitch {get_card_class("Portiere")}">🧤 POR: {tp1}</div>', unsafe_allow_html=True)
            else:
                for idx_t, gt in enumerate(titolari_salvati):
                    st.markdown(f'<div class="player-card-pitch {get_card_class(mapping_ruoli.get(gt, "C"))}">Titolare {idx_t+1}: {gt}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Panchina Stadio con sfondo dedicato
            st.subheader("🏟️ Panchina dello Stadio (Ordine di Subentro)")
            st.markdown('<div class="bench-container">', unsafe_allow_html=True)
            cambi_correnti = dati_utente.get("panchina_ordinata", [])
            if cambi_correnti:
                b_cols_vis = st.columns(len(cambi_correnti))
                for i, c_item in enumerate(cambi_correnti):
                    with b_cols_vis[i]:
                        st.markdown(f'<div class="player-card-bench">🔄 {i+1}° Cambio: {c_item}</div>', unsafe_allow_html=True)
            else:
                st.markdown("*Nessun cambio impostato in panchina.*")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏆 Classifica Partecipanti":
    st.title("🏆 Partecipanti Iscritti")
    df_iscritti = pd.DataFrame([
        {
            "Nome": v["nome"], 
            "Cognome": v["cognome"], 
            "Classe": v["classe"], 
            "Crediti Rimanenti": v["crediti"], 
            "Giocatori in Rosa": len(v["rosa"]),
            "Titolari Schierati": len(v.get("formazione_titolare", []))
        } 
        for k, v in st.session_state["utenti_registrati"].items()
    ])
    st.dataframe(df_iscritti, use_container_width=True, hide_index=True)

elif menu in ["👑 Pannello Super-Admin", "⚙️ Pannello Admin"]:
    st.title("👑 Pannello di Controllo Riservato")
    
    if dati_utente.get("is_super_admin", False):
        st.success("Autenticato come SUPER ADMIN: Alessandro Carbone. Hai priorità massima.")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎛️ Mercato & Regole", "📁 Carica Voti Excel", "⏱️ Timer & Sostituzioni", "📐 Gestione Moduli", "🚨 Sicurezza Sito"])
    
    with tab1:
        # Toggle mercato persistente in session state
        stato_mercato = st.toggle("Stato Mercato (Aperto / Chiuso)", value=st.session_state["mercato_aperto"])
        if stato_mercato != st.session_state["mercato_aperto"]:
            st.session_state["mercato_aperto"] = stato_mercato
            st.rerun()
            
        st.markdown("---")
        st.subheader("⚙️ Configurazione Rosa, Budget e Limiti Ruoli")
        
        nuova_dim_rosa = st.number_input("Numero di giocatori che compongono la rosa completa", min_value=5, max_value=15, value=st.session_state["dimensione_rosa"])
        if nuova_dim_rosa != st.session_state["dimensione_rosa"]:
            st.session_state["dimensione_rosa"] = nuova_dim_rosa
            st.success(f"Dimensione rosa aggiornata a {nuova_dim_rosa} giocatori!")

        nuovo_budget = st.number_input("Crediti Totali a disposizione per utente:", min_value=50, max_value=2000, value=st.session_state["budget_totale"], step=10)
        if nuovo_budget != st.session_state["budget_totale"]:
            st.session_state["budget_totale"] = nuovo_budget
            st.success(f"Budget totale aggiornato a {nuovo_budget} crediti!")

        st.markdown("##### 📌 Numero di giocatori per ruolo obbligatori in rosa:")
        limiti = st.session_state["limiti_ruoli"]
        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        with col_l1:
            limiti["Portiere"] = st.number_input("Portieri", min_value=1, max_value=5, value=limiti.get("Portiere", 1))
        with col_l2:
            limiti["Difensore"] = st.number_input("Difensori", min_value=1, max_value=8, value=limiti.get("Difensore", 3))
        with col_l3:
            limiti["Centrocampista"] = st.number_input("Centrocampisti", min_value=1, max_value=8, value=limiti.get("Centrocampista", 3))
        with col_l4:
            limiti["Attaccante"] = st.number_input("Attaccanti", min_value=1, max_value=8, value=limiti.get("Attaccante", 1))
        
        st.session_state["limiti_ruoli"] = limiti
            
    with tab2:
        st.subheader("Caricamento Massivo Voti")
        st.write(f"Nota: La keyword attuale per indicare che un giocatore **non ha preso voto** (non ha giocato) è: `{st.session_state['keyword_senza_voto']}`")
        file_voti = st.file_uploader("Allega qui il file Excel o CSV con i voti della settimana", type=['csv', 'xlsx'])
        if file_voti is not None:
            try:
                if file_voti.name.endswith('.csv'):
                    df_voti_caricato = pd.read_csv(file_voti)
                else:
                    df_voti_caricato = pd.read_excel(file_voti)
                
                st.session_state["voti_caricati"] = df_voti_caricato
                st.success(f"File {file_voti.name} caricato con successo nel sistema!")
                st.dataframe(df_voti_caricato, use_container_width=True)
            except Exception as e:
                st.error(f"Errore nella lettura del file: {e}")
                
    with tab3:
        st.subheader("⏱️ Gestione Timer Formazione")
        st.write(f"Scadenza attuale: {st.session_state['scadenza_formazione'].strftime('%d/%m/%Y %H:%M:%S')}")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            aggiungi_ore = st.number_input("Aggiungi ore alla scadenza", min_value=0, max_value=168, value=24)
        with col_t2:
            if st.button("Aggiorna / Estendi Timer", use_container_width=True):
                st.session_state["scadenza_formazione"] = datetime.now() + timedelta(hours=aggiungi_ore)
                st.success(f"Timer aggiornato! Nuova scadenza tra {aggiungi_ore} ore.")
                st.rerun()
                
        st.markdown("---")
        st.subheader("🔄 Configurazione Keyword Panchina / Sostituzioni")
        nuova_keyword = st.text_input("Keyword Senza Voto", value=st.session_state["keyword_senza_voto"])
        if nuova_keyword != st.session_state["keyword_senza_voto"]:
            st.session_state["keyword_senza_voto"] = nuova_keyword
            st.success(f"Keyword aggiornata con successo a: '{nuova_keyword}'")

    with tab4:
        st.subheader("📐 Gestione Moduli Tattici")
        st.write("Moduli attualmente abilitati:", ", ".join(st.session_state["moduli_disponibili"]))
        st.info("Nota: I moduli predefiniti '2-1-1' e '1-2-1' sono obbligatori e non possono essere rimossi.")
        
        nuovo_modulo = st.text_input("Aggiungi un nuovo modulo (es. 2-2-0 o 3-0-1):")
        if st.button("Aggiungi Modulo"):
            if nuovo_modulo and nuovo_modulo not in st.session_state["moduli_disponibili"]:
                st.session_state["moduli_disponibili"].append(nuovo_modulo)
                st.success(f"Modulo '{nuovo_modulo}' aggiunto con successo!")
                st.rerun()
            elif nuovo_modulo in st.session_state["moduli_disponibili"]:
                st.warning("Questo modulo è già presente nell'elenco.")

    with tab5:
        st.subheader("Kill Switch (Riservato allo Sviluppatore)")
        st.warning("Premendo questo pulsante l'intero sito diventerà inaccessibile a tutti gli utenti e admin.")
        password_kill = st.text_input("Password di Sviluppo", type="password")
        if st.button("🔴 SPEGNI SITO", type="primary"):
            if password_kill == "gabriele_master_2026":
                st.session_state["kill_switch"] = True
                st.rerun()
            else:
                st.error("Password di sviluppo errata.")
