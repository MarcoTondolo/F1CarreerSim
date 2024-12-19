import random
from flask import Flask, render_template, request, redirect, url_for
from F1Sim.lineup import (lineup_blueprint, Pilota, Scuderia, giocatore, scuderie_f1, scuderie_f2, scuderie_f3, scuderie_f4,
                          piloti, piloti_svincolati, nomi_piloti_svincolati_iniziali, reset_year)
from info.teams import scuderie_piloti_f1, scuderie_piloti_f2, scuderie_piloti_f3, scuderie_piloti_f4
from faker import Faker

fake = Faker()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(lineup_blueprint)
first_start = True

# Inizializzazione della simulazione
def inizializza_simulazione(nome_giocatore, nome_team):
    team_iniziale = None

    for scuderia in scuderie_f4:
        if scuderia.nome == nome_team:
            team_iniziale = scuderia

    pilota_sostituito = random.choice(team_iniziale.piloti)
    piloti.remove(pilota_sostituito)
    piloti_svincolati.append(pilota_sostituito)
    giocatore.nome = nome_giocatore
    giocatore.scuderia = team_iniziale.nome
    giocatore.categoria = team_iniziale.categoria
    giocatore.race_wins = 0
    giocatore.wdc = []
    giocatore.wcc = []
    team_iniziale.piloti.append(giocatore)
    team_iniziale.piloti.remove(pilota_sostituito)
    piloti.append(giocatore)


def scegli_scuderia():
    scuderie_diverse = False
    scuderie_scelte = random.sample(scuderie_f4, 3)
    while not scuderie_diverse:
        if scuderie_scelte[0].nome != scuderie_scelte[1].nome:
            if scuderie_scelte[0].nome != scuderie_scelte[2].nome:
                if scuderie_scelte[1].nome != scuderie_scelte[2].nome:
                    scuderie_diverse = True
                else:
                    scuderie_scelte[2] = random.choice(scuderie_f4)
            else:
                scuderie_scelte[2] = random.choice(scuderie_f4)
        else:
            scuderie_scelte[1] = random.choice(scuderie_f4)

    return scuderie_scelte


def crea_piloti():
    scuderie_categorie = {
        1: (scuderie_piloti_f1, scuderie_f1),
        2: (scuderie_piloti_f2, scuderie_f2),
        3: (scuderie_piloti_f3, scuderie_f3),
        4: (scuderie_piloti_f4, scuderie_f4),
    }

    for categoria, (scuderie_piloti, lista_scuderie) in scuderie_categorie.items():
        for nome_scuderia, nomi_piloti in scuderie_piloti.items():
            scuderia = Scuderia(nome_scuderia, categoria)

            if nomi_piloti:
                for nome_pilota in nomi_piloti:
                    # Imposta l'academy in base alla categoria
                    pilota = Pilota(nome_pilota, scuderia.nome, categoria, academy, nome_pilota.split()[-1].lower())
                    scuderia.piloti.append(pilota)
                    piloti.append(pilota)
            else:
                for i in range(2):  # Aggiungi due piloti
                    # Imposta l'academy in base alla categoria
                    academy = nome_scuderia if categoria == 1 else random.choice(academy_casuali)
                    pilota = Pilota(f"{fake.first_name()} {fake.last_name()}", scuderia.nome, categoria, academy, "tbd")
                    scuderia.piloti.append(pilota)
                    piloti.append(pilota)

            lista_scuderie.append(scuderia)

    for nome_pilota in nomi_piloti_svincolati_iniziali:
        pilota = Pilota(nome_pilota, "Svincolato", 1, "None", nome_pilota.split()[-1].lower())
        piloti_svincolati.append(pilota)

def reset_simulazione():
    # Resetta tutte le liste e variabili
    # Pulisci le liste
    if scuderie_f1 and scuderie_f2 and scuderie_f3 and scuderie_f4:
        scuderie_f1.clear()
        scuderie_f2.clear()
        scuderie_f3.clear()
        scuderie_f4.clear()

    if piloti:
        piloti.clear()  # Svuota la lista dei piloti

    if piloti_svincolati:
        piloti_svincolati.clear()  # Svuota la lista dei piloti svincolati

    reset_year()


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
    nome = "Marco Tondolo"
    scuderia = request.form['team'].lower().replace(" ", "-")

    inizializza_simulazione(nome, scuderia)

    return redirect(url_for('lineup.lineup'))

if __name__ == '__main__':
    app.run(debug=True)
