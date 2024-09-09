import streamlit as st
import pandas as pd
import chardet

# Funktion zur Erkennung der Dateikodierung
def detect_encoding(file):
    raw_data = file.read()
    result = chardet.detect(raw_data)
    file.seek(0)  # Setze den Dateizeiger zurück, um später erneut auf die Datei zuzugreifen
    return result['encoding']

# Funktion zur Bereinigung der fehlerhaften Zeichen
def clean_column_names(columns):
    clean_columns = []
    for col in columns:
        # Ersetzen von fehlerhaften Zeichen
        col = col.replace('â„ƒ', '°C').replace('ÃŸ', 'ß').replace('Â°', '°')
        clean_columns.append(col)
    return clean_columns

# Titel des Dashboards
st.title("Spezielle CSV-Datei Hochladen und Bearbeiten")

# Upload der CSV-Datei
uploaded_file = st.file_uploader("Wähle eine CSV-Datei aus", type=["csv"])

if uploaded_file is not None:
    # Automatische Erkennung der Kodierung
    encoding = detect_encoding(uploaded_file)
    
    # Ausgabe der erkannten Kodierung
    st.write(f"Erkannte Kodierung: {encoding}")
    
    try:
        # Lesen der hochgeladenen Datei in einen Pandas DataFrame unter Verwendung der erkannten Kodierung
        df = pd.read_csv(uploaded_file, encoding=encoding)
        
        # Bereinigung der Spaltennamen
        df.columns = clean_column_names(df.columns)
        
        # Anzeige der bereinigten Rohdaten
        st.subheader("Bereinigte Rohdaten")
        st.write(df)
        
        # Möglichkeit zur Bearbeitung der Daten
        st.subheader("Daten bearbeiten und anpassen")
        
        # Dropdown-Menü zur Auswahl der Spalten, die bearbeitet werden sollen
        selected_columns = st.multiselect("Wähle die Spalten aus, die du anzeigen oder bearbeiten möchtest", df.columns)
        
        if selected_columns:
            st.write(df[selected_columns])
        
        # Weitere Bearbeitungsoptionen, z.B. Spalten umbenennen oder Filtern nach bestimmten Kriterien
        st.subheader("Datenvereinheitlichung")
        
        # Beispiel: Spalten umbenennen
        new_column_name = st.text_input("Gib einen neuen Spaltennamen ein", "")
        column_to_rename = st.selectbox("Wähle die Spalte, die du umbenennen möchtest", df.columns)
        
        if st.button("Spalte umbenennen"):
            df = df.rename(columns={column_to_rename: new_column_name})
            st.write("Aktualisierte Daten mit umbenannter Spalte:")
            st.write(df)

        # Beispiel: Filter auf bestimmte Werte anwenden
        st.subheader("Daten filtern")
        column_to_filter = st.selectbox("Wähle die Spalte zum Filtern", df.columns)
        filter_value = st.text_input("Gib den Filterwert ein")
        
        if st.button("Anwenden"):
            filtered_df = df[df[column_to_filter].astype(str).str.contains(filter_value, na=False)]
            st.write(f"Gefilterte Daten basierend auf {filter_value}:")
            st.write(filtered_df)
        
        # Möglichkeit, die angepassten Daten als CSV mit Semikolon als Trennzeichen herunterzuladen
        st.subheader("Herunterladen der angepassten Daten (Semikolon-getrennt)")
        csv = df.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button(
            label="CSV-Datei herunterladen",
            data=csv,
            file_name='bearbeitete_daten_semikolon.csv',
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"Es gab ein Problem beim Lesen der Datei: {e}")
else:
    st.write("Bitte lade eine CSV-Datei hoch, um fortzufahren.")
