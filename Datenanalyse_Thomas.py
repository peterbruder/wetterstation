import streamlit as st
import pandas as pd
import chardet
from io import BytesIO

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

# Funktion zur Konvertierung und Anpassung der Datentypen
def convert_to_german_format(df):
    # Konvertiere die Zeitspalte in ein Datumsformat
    df['Zeit'] = pd.to_datetime(df['Zeit'], format='%Y/%m/%d %H:%M')

    # Ersetze das Dezimaltrennzeichen für numerische Spalten mit deutschem Komma
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].applymap(lambda x: f"{x:.2f}".replace('.', ','))

    return df

# Funktion zur Umwandlung in Excel mit deutschem Format
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Daten')

    # Automatische Formatierung anpassen
    workbook = writer.book
    worksheet = writer.sheets['Daten']
    
    # Format für Datum und Zeit
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
    worksheet.set_column('A:A', 20, date_format)

    # Speichern und Rückgabe des Inhalts
    writer.save()
    output.seek(0)
    return output

# Titel des Dashboards
st.title("CSV-Datei Hochladen und in deutsches Excel-Format umwandeln")

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
        
        # Konvertiere in deutsches Format (Datum/Zeit und Dezimaltrennzeichen)
        df_german_format = convert_to_german_format(df)
        
        # Anzeige der bereinigten Rohdaten
        st.subheader("Bereinigte und formatierte Rohdaten")
        st.write(df_german_format)
        
        # Möglichkeit, die angepassten Daten als Excel-Datei herunterzuladen
        st.subheader("Herunterladen der angepassten Excel-Daten")
        excel = to_excel(df_german_format)
        st.download_button(
            label="Excel-Datei herunterladen",
            data=excel,
            file_name='bereinigte_daten_de.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    except Exception as e:
        st.error(f"Es gab ein Problem beim Lesen der Datei: {e}")
else:
    st.write("Bitte lade eine CSV-Datei hoch, um fortzufahren.")
