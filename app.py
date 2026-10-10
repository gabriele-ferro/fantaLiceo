# per lanciarlo: streamlit run app.py

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

# Iniezione CSS per rendere l'interfaccia "App-like" e mostrare la firma fissa
st.markdown("""
    <style>
    .firma-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #1E1E1E;
        color: #4CAF50;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
        z-index: 9999;
        border-top: 2px solid #4CAF50;
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
    </style>
    <div class="firma-container">
        ✨ Realizzato da Gabriele Ferro ✨
    </div>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE VARIABILI DI SESSIONE ---
if "kill_switch" not in st.session_state:
    st.session_state["kill_switch"] = False
if "utenti_registrati" not in st.session_state:
    st.session_state["utenti_registrati"] = {}
if "utente_corrente" not in st.session_state:
    st.session_state["utente_corrente"] = None
if "mercato_aperto" not in st.session_state:
    st.session_state["mercato_aperto"] = False
# Nuove impostazioni di lega gestibili dal Super Admin
if "dimensione_rosa" not in st.session_state:
    st.session_state["dimensione_rosa"] = 8  # Default 8 giocatori in rosa totale
if "scadenza_formazione" not in st.session_state:
    st.session_state["scadenza_formazione"] = datetime.now() + timedelta(days=2) # Default 2 giorni
if "keyword_senza_voto" not in st.session_state:
    st.session_state["keyword_senza_voto"] = "@" # Keyword default per voto non assegnato
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
                            st.error("🚨 Tentativo di furto d'identità rilevato. PIN Super Admin errato. Un futtiri cuinnutu 🤘🏻")
                            st.stop()

                    if chiave_utente not in st.session_state["utenti_registrati"]:
                        st.session_state["utenti_registrati"][chiave_utente] = {
                            "nome": nome.title(),
                            "cognome": cognome.title(),
                            "classe": f"{anno}{sezione} {indirizzo}",
                            "crediti": 100,
                            "rosa": [],
                            "formazione_titolare": [],
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
    
    try:
        df_giocatori = pd.read_excel("giocatori.xlsx")
    except FileNotFoundError:
        st.error("🚨 File 'giocatori.xlsx' non trovato nella cartella del progetto! Crea il file Excel con le colonne Nome, Ruolo, Classe, Quotazione.")
        st.stop()

    colonne_richieste = ["Nome", "Ruolo", "Classe", "Quotazione"]
    colonne_mancanti = [c for c in colonne_richieste if c not in df_giocatori.columns]
    if colonne_mancanti:
        st.error(f"🚨 Il file Excel non contiene le seguenti colonne obbligatorie: {colonne_mancanti}")
        st.stop()

    st.info(f"📌 Regola Rosa: Ogni squadra deve essere composta esattamente da **{st.session_state['dimensione_rosa']} giocatori**.")

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

        st.dataframe(df_filtrato, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📝 Componi la tua Rosa")

        lista_nomi = df_giocatori["Nome"].tolist()
        rosa_attuale = dati_utente.get("rosa", [])

        giocatori_scelti = st.multiselect(
            f"Seleziona esattamente {st.session_state['dimensione_rosa']} giocatori dal listone:",
            options=lista_nomi,
            default=rosa_attuale
        )

        spesa_totale = 0
        for nome_gioc in giocatori_scelti:
            riga = df_giocatori[df_giocatori["Nome"] == nome_gioc]
            if not riga.empty:
                spesa_totale += int(riga["Quotazione"].values[0])

        crediti_rimasti_calcolati = 100 - spesa_totale

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Spesa Totale", f"{spesa_totale} 🪙")
        col_m2.metric("Crediti Residui", f"{crediti_rimasti_calcolati} 🪙")

        if len(giocatori_scelti) != st.session_state["dimensione_rosa"]:
            st.warning(f"⚠️ Attenzione: hai selezionato {len(giocatori_scelti)} giocatori. La rosa deve essere composta da esattamente {st.session_state['dimensione_rosa']} giocatori.")

        if crediti_rimasti_calcolati < 0:
            st.error("🚨 ATTENZIONE: Hai superato il budget di 100 crediti! Riduci i giocatori selezionati.")

        if st.button("💾 Salva Formazione / Rosa", use_container_width=True):
            if crediti_rimasti_calcolati >= 0 and len(giocatori_scelti) == st.session_state["dimensione_rosa"]:
                dati_utente["rosa"] = giocatori_scelti
                dati_utente["crediti"] = crediti_rimasti_calcolati
                st.success("🎉 Rosa salvata con successo!")
                st.rerun()
            else:
                st.error("Impossibile salvare: verifica che il budget non sia sforato e di aver rispettato il numero esatto di giocatori richiesti per la rosa.")

elif menu == "⚽ Schiera Formazione":
    st.title("⚽ Schiera la Formazione Titolare")
    
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
    
    if not rosa_utente:
        st.warning("⚠️ Non hai ancora acquistato una rosa nel Calciomercato! Vai prima su 'Calciomercato' per comprare i tuoi giocatori.")
    else:
        st.markdown(f"La tua rosa attuale è composta da {len(rosa_utente)} giocatori.")
        st.write("Seleziona **esattamente 5 giocatori** che scenderanno in campo come titolari per questa giornata. I restanti faranno parte della panchina.")
        
        titolari_salvati = dati_utente.get("formazione_titolare", [])
        
        # Filtriamo per fare in modo che i default siano validi se presenti nella rosa
        default_titolari = [g for g in titolari_salvati if g in rosa_utente]
        
        with st.form("form_formazione"):
            scelti_titolari = st.multiselect(
                "Seleziona i 5 Titolari:",
                options=rosa_utente,
                default=default_titolari,
                max_selections=5
            )
            
            submit_formazione = st.form_submit_button("Conferma e Schiera Titolari 🚀", use_container_width=True)
            
            if submit_formazione:
                if not finestra_aperta:
                    st.error("Impossibile salvare: il tempo limite per la formazione è scaduto.")
                elif len(scelti_titolari) != 5:
                    st.error(f"Devi selezionare esattamente 5 titolari (ne hai selezionati {len(scelti_titolari)}).")
                else:
                    dati_utente["formazione_titolare"] = scelti_titolari
                    st.success("🎉 Formazione titolare salvata con successo!")
        
        # Visualizzazione riepilogo Titolari e Panchina
        if titolari_salvati and len(titolari_salvati) == 5:
            st.markdown("---")
            st.subheader("🏟️ Riepilogo Schieramento Attuale")
            
            col_t, col_p = st.columns(2)
            with col_t:
                st.markdown("#### ⭐ Titolari (In Campo)")
                for t in titolari_salvati:
                    st.markdown(f"- ✅ {t}")
            with col_p:
                st.markdown("#### 🔄 Panchina")
                panchinari = [g for g in rosa_utente if g not in titolari_salvati]
                if panchinari:
                    for p in panchinari:
                        st.markdown(f"- 🔸 {p}")
                else:
                    st.markdown("- *Nessun panchinaro disponibile*")

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
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎛️ Mercato & Regole", "📁 Carica Voti Excel", "⏱️ Timer & Sostituzioni", "🚨 Sicurezza Sito"])
    
    with tab1:
        stato_mercato = st.toggle("Stato Mercato", value=st.session_state["mercato_aperto"])
        if stato_mercato != st.session_state["mercato_aperto"]:
            st.session_state["mercato_aperto"] = stato_mercato
            st.rerun()
            
        st.markdown("---")
        st.subheader("⚙️ Configurazione Dimensione Rosa")
        nuova_dim_rosa = st.number_input("Numero di giocatori che compongono la rosa completa", min_value=5, max_value=15, value=st.session_state["dimensione_rosa"])
        if nuova_dim_rosa != st.session_state["dimensione_rosa"]:
            st.session_state["dimensione_rosa"] = nuova_dim_rosa
            st.success(f"Dimensione rosa aggiornata a {nuova_dim_rosa} giocatori!")
            
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
        st.write("Imposta il carattere o la parola chiave inserita nel file dei voti quando un giocatore non prende voto:")
        nuova_keyword = st.text_input("Keyword Senza Voto", value=st.session_state["keyword_senza_voto"])
        if nuova_keyword != st.session_state["keyword_senza_voto"]:
            st.session_state["keyword_senza_voto"] = nuova_keyword
            st.success(f"Keyword aggiornata con successo a: '{nuova_keyword}'")
            
    with tab3 if False else tab4: # Tab Sicurezza
        st.subheader("Kill Switch (Riservato allo Sviluppatore)")
        st.warning("Premendo questo pulsante l'intero sito diventerà inaccessibile a tutti gli utenti e admin.")
        password_kill = st.text_input("Password di Sviluppo", type="password")
        if st.button("🔴 SPEGNI SITO", type="primary"):
            if password_kill == "gabriele_master_2026":
                st.session_state["kill_switch"] = True
                st.rerun()
            else:
                st.error("Password di sviluppo errata.")