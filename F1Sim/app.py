import random
from flask import Flask, render_template, request, redirect, url_for
from F1Sim.lineup import (lineup_blueprint, Pilota, Scuderia, giocatore, scuderie, piloti, piloti_svincolati,
                          scuderie_piloti,
                          nomi_piloti_svincolati_iniziali, reset_year, current_season, set_year)
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(lineup_blueprint)
first_start = True
folder = "F1Sim"


def inizializza_titoli(filename):
    # Carica i dati dal file JSON
    with open(filename, "r", encoding="utf-8") as file:
        dati = json.load(file)

    # Aggiorna i titoli WCC per le scuderie
    for dati_scuderia in dati["team"]:
        for scuderia in scuderie:
            if scuderia.nome == dati_scuderia["nome"]:
                for anno in dati_scuderia["WCC"]:
                    if anno not in scuderia.wcc:
                        scuderia.wcc.append(anno)

    # Aggiorna i titoli WDC per i piloti
    for dati_pilota in dati["piloti"]:
        for pilota in piloti:
            if pilota.nome == dati_pilota["nome"]:
                for wdc in dati_pilota["WDC"]:
                    pilota.wdc.append({'scuderia': wdc['team'], 'anno': wdc['anno']})
                for wcc in dati_pilota["WCC"]:
                    for anno in wcc["anni"]:
                        pilota.wcc.append({'scuderia': wcc["team"], 'anno': anno})

                pilota.race_wins = dati_pilota["race_wins"]

    # Aggiorna i titoli WDC per i piloti svincolati
    for dati_pilota in dati["piloti_svincolati"]:
        for pilota in piloti_svincolati:
            if pilota.nome == dati_pilota["nome"]:
                for wdc in dati_pilota["WDC"]:
                    pilota.wdc.append({'scuderia': wdc['team'], 'anno': wdc['anno']})
                for wcc in dati_pilota["WCC"]:
                    for anno in wcc["anni"]:
                        pilota.wcc.append({'scuderia': wcc["team"], 'anno': anno})

                pilota.race_wins = dati_pilota["race_wins"]


# Inizializzazione della simulazione
def inizializza_simulazione(nome_giocatore, nome_team):
    team_iniziale = None
    filename = "titoli_f1_attuali.json"

    for scuderia in scuderie:
        if scuderia.nome == nome_team:
            team_iniziale = scuderia

    pilota_sostituito = random.choice(team_iniziale.piloti)
    piloti.remove(pilota_sostituito)
    piloti_svincolati.append(pilota_sostituito)
    giocatore.nome = nome_giocatore
    giocatore.scuderia = team_iniziale.nome
    giocatore.race_wins = 0
    giocatore.wdc = []
    giocatore.wcc = []
    giocatore.rating = 50
    team_iniziale.piloti.append(giocatore)
    team_iniziale.piloti.remove(pilota_sostituito)
    piloti.append(giocatore)
    if not os.path.exists(filename):
        file_path = os.path.join(folder, filename)
    else:
        file_path = filename  # già dentro F1Sim
    if (( os.path.exists(filename) or os.path.exists(file_path) )
            and ( os.stat(file_path).st_size > 0 or os.stat(filename).st_size > 0) ):
        inizializza_titoli(filename)


def scegli_scuderia():
    scuderie_diverse = False
    scuderie_scelte = random.sample(scuderie, 3)
    while not scuderie_diverse:
        if scuderie_scelte[0].nome != scuderie_scelte[1].nome:
            if scuderie_scelte[0].nome != scuderie_scelte[2].nome:
                if scuderie_scelte[1].nome != scuderie_scelte[2].nome:
                    scuderie_diverse = True
                else:
                    scuderie_scelte[2] = random.choice(scuderie)
            else:
                scuderie_scelte[2] = random.choice(scuderie)
        else:
            scuderie_scelte[1] = random.choice(scuderie)

    return scuderie_scelte


def crea_piloti():
    for nome_scuderia, nomi_piloti in scuderie_piloti.items():
        scuderia = Scuderia(nome_scuderia, [])
        for nome_pilota in nomi_piloti:
            pilota = Pilota(nome_pilota, scuderia.nome, nome_pilota.split()[-1].lower())
            scuderia.piloti.append(pilota)
            piloti.append(pilota)
        scuderie.append(scuderia)

    for nome_pilota in nomi_piloti_svincolati_iniziali:
        pilota = Pilota(nome_pilota, "Svincolato", nome_pilota.split()[-1].lower())
        piloti_svincolati.append(pilota)

def reset_simulazione():
    # Resetta tutte le liste e variabili
    # Pulisci le liste
    if scuderie:
        scuderie.clear()  # Svuota la lista delle scuderie

    if piloti:
        piloti.clear()  # Svuota la lista dei piloti

    if piloti_svincolati:
        piloti_svincolati.clear()  # Svuota la lista dei piloti svincolati

    reset_year()

    filename = "dati_f1.json"
    if os.path.exists(filename):
        with open(filename, "w", encoding="utf-8"):
            pass


def carica_dati(filename):
    """Carica i dati delle scuderie, dei piloti e del giocatore da un file JSON, se presente."""
    with open(filename, "r", encoding="utf-8") as file:
        dati = json.load(file)

    if scuderie:
        scuderie.clear()
    if piloti_svincolati:
        piloti_svincolati.clear()
    for scuderia_data in dati["scuderie"]:
        piloti_caricati = []
        for pilota_data in scuderia_data["piloti"]:
            pilota = Pilota(
                pilota_data["nome"],
                pilota_data["scuderia"],
                pilota_data["image"],
                pilota_data["punti"],
                pilota_data["punti_gara"],
                pilota_data["race_wins"],
                pilota_data["rating"],
                pilota_data["temp_rating"],
                pilota_data["wdc"],
                pilota_data["wcc"]
            )
            piloti_caricati.append(pilota)
            piloti.append(pilota)
        scuderia = Scuderia(scuderia_data["nome"], piloti_caricati)
        scuderia.wcc = scuderia_data["wcc"]
        scuderia.last_position = scuderia_data["last_position"]
        scuderia.leaderboard_change = scuderia_data["leaderboard_change"]
        scuderia.rating = scuderia_data["rating"]
        scuderie.append(scuderia)

    giocatore_data = dati["giocatore"]
    giocatore.nome = giocatore_data["nome"]
    giocatore.scuderia = giocatore_data["scuderia"]
    giocatore.image = giocatore_data["image"]
    giocatore.punti = giocatore_data["punti"]
    giocatore.punti_gara = giocatore_data["punti_gara"]
    giocatore.race_wins = giocatore_data["race_wins"]
    giocatore.rating = giocatore_data["rating"]
    giocatore.temp_rating = giocatore_data["temp_rating"]
    giocatore.wdc = giocatore_data["wdc"]
    giocatore.wcc = giocatore_data["wcc"]
    giocatore.posizione_finale = giocatore_data["posizione_finale"]

    for pilota_data in dati["piloti_svincolati"]:
        pilota = Pilota(
            pilota_data["nome"],
            pilota_data["scuderia"],
            pilota_data["image"],
            pilota_data["punti"],
            pilota_data["punti_gara"],
            pilota_data["race_wins"],
            pilota_data["rating"],
            pilota_data["temp_rating"],
            pilota_data["wdc"],
            pilota_data["wcc"]
        )
        piloti_svincolati.append(pilota)

    set_year(dati["current_season"])

    print("Dati caricati con successo.")

def rimuovi_duplicati(lista):
    unici = []
    nomi_visti = set()
    for item in lista:
        if item.nome not in nomi_visti:
            unici.append(item)
            nomi_visti.add(item.nome)
    return unici



@app.route('/reset')
def reset():
    reset_simulazione()
    crea_piloti()
    return render_template("index.html", anno=current_season)


@app.route('/')
def index():
    filename = "dati_f1.json"
    if not os.path.exists(filename):
        filename = os.path.join(folder, filename)
    if os.path.exists(filename) and os.stat(filename).st_size > 0:
        try:
            carica_dati(filename)
            piloti[:] = rimuovi_duplicati(piloti)
            scuderie[:] = rimuovi_duplicati(scuderie)
            piloti_svincolati[:] = rimuovi_duplicati(piloti_svincolati)
            return redirect(url_for('lineup.lineup'))
        except Exception:
            reset_simulazione()
            crea_piloti()
            return render_template("index.html", anno=current_season)
    else:
        reset_simulazione()
        crea_piloti()
        return render_template("index.html", anno=current_season)

# Rotta per creare il pilota
@app.route('/crea-pilota')
def crea_pilota():
    three_teams = scegli_scuderia()
    return render_template('crea-pilota.html', teams=three_teams)

# Rotta per aggiungere il pilota alla lineup
@app.route('/aggiungi_pilota', methods=['POST'])
def aggiungi_pilota():
    nome = "Marco Tondolo"
    scuderia = request.form['team'].lower().replace(" ", "-")

    inizializza_simulazione(nome, scuderia)

    return redirect(url_for('lineup.lineup'))

if __name__ == '__main__':
    app.run(debug=True)
