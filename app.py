from flask import Flask, render_template, request, redirect
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

SPREADSHEET_ID = '1zF_8Kh7DDq03IZr4JdX1JdrVP2VZispMsb7JJ3JnLYE'
SHEET_NAME = 'Novedades'
RANGE = SHEET_NAME
CREDENTIALS_FILE = 'credentials.json'

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build('sheets', 'v4', credentials=creds)


@app.route('/')

def index():
    service = get_service()
    sheet = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    rows = sheet.get('values', [])
    
    # 👇 Este bloque imprime los datos que vienen del Sheets
    print(">>> Datos obtenidos desde Google Sheets:")
    for r in rows:
        print(r)

    if not rows:
        return "No hay datos."

    headers = rows[0]
    data = rows[1:]

    # 👇 Aquí filtras solo los pendientes
    data = [(i + 2, row) for i, row in enumerate(data) if len(row) > 8 and row[8] == "Pendiente"]

    return render_template('index.html', headers=headers, data=data)

@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    fila = int(request.form['fila'])
    estado = request.form['estado']

    service = get_service()
    rango_estado = f"{SHEET_NAME}!I{fila}"
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=rango_estado,
        valueInputOption="RAW",
        body={"values": [[estado]]}
    ).execute()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
