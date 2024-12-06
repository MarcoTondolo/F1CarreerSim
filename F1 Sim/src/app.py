from flask import Flask, render_template, request, redirect, url_for
from lineup import (lineup_blueprint, Pilota, Scuderia, scuderie_piloti, scuderie, piloti,
                    piloti_svincolati, nomi_piloti_svincolati_iniziali, giocatore)
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(lineup_blueprint)
first_start = True

# Inizializzazione della simulazione
def inizializza_simulazione(nome_giocatore, nome_team):

    team_iniziale = None

    for scuderia in scuderie:
        if scuderia.nome == nome_team:
            team_iniziale = scuderia

    pilota_sostituito = random.choice(team_iniziale.piloti)
    piloti.remove(pilota_sostituito)
    piloti_svincolati.append(pilota_sostituito)
    giocatore.nome = nome_giocatore
    giocatore.scuderia = team_iniziale.nome
    team_iniziale.piloti.append(giocatore)
    team_iniziale.piloti.remove(pilota_sostituito)
    piloti.append(giocatore)


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
    global scuderie, piloti, piloti_svincolati, giocatore

    # Pulisci le liste
    scuderie.clear()  # Svuota la lista delle scuderie
    piloti.clear()  # Svuota la lista dei piloti
    piloti_svincolati.clear()  # Svuota la lista dei piloti svincolati


@app.route('/')
def index():
    reset_simulazione()
    crea_piloti()
    return render_template("index.html")

# Rotta per creare il pilota
@app.route('/crea-pilota')
def crea_pilota():
    three_teams = scegli_scuderia()
    return render_template('crea-pilota.html', teams=three_teams)

# Rotta per aggiungere il pilota alla lineup
@app.route('/aggiungi_pilota', methods=['POST'])
def aggiungi_pilota():
    nome = "Player"
    scuderia = request.form['team'].lower().replace(" ", "-")

    inizializza_simulazione(nome, scuderia)

    return redirect(url_for('lineup.lineup'))

if __name__ == '__main__':
    app.run(debug=True)
