from random import randint
from flask import Blueprint, render_template, request, session
import datetime

lineup_blueprint = Blueprint('lineup', __name__)

market1 = True
market2 = True
notizie_mercato = {}
notizie_serializzate = {}
offerte_giocatore = None

gp_names = [
    "Bahrain", "Arabia Saudita", "Australia", "Giappone", "Cina", "Miami",
    "Emilia Romagna", "Monaco", "Canada", "Spagna", "Austria", "Gran Bretagna",
    "Ungheria", "Belgio", "Olanda", "Italia", "Azerbaijan", "Singapore", "Stati Uniti",
    "Messico", "Brasile", "Las Vegas", "Qatar", "Abu Dhabi"
]

races = {gp: {"winner_name": "", "winner_team": ""} for gp in gp_names}

MAX_RACES = len(gp_names)  # Utilizza direttamente la lunghezza di gp_names
current_race_count = 0  # Inizializzazione globale
current_season = datetime.datetime.now().year

def reset_year():
    global current_season
    current_season = datetime.datetime.now().year

import random
import datetime

# Lista dei piloti svincolati
nomi_piloti_svincolati_iniziali = [
    "Logan Sargeant", "Franco Colapinto", "Kevin Magnussen", "Daniel Ricciardo", "Guanyu Zhou",
    "Sergio Perez", "Valtteri Bottas"
]
piloti_svincolati = []
scuderie = []
piloti = []

# Scuderie e piloti
scuderie_piloti = {
    "red-bull": ["Max Verstappen", "Liam Lawson"],
    "ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    "mclaren": ["Lando Norris", "Oscar Piastri"],
    "racing-bulls": ["Yuki Tsunoda", "Isack Hadjar"],
    "haas": ["Oliver Bearman", "Esteban Ocon"],
    "mercedes": ["George Russell", "Kimi Antonelli"],
    "alpine": ["Pierre Gasly", "Jack Doohan"],
    "williams": ["Carlos Sainz", "Alexander Albon"],
    "sauber": ["Gabriel Bortoleto", "Nico Hulkenberg"],
    "aston-martin": ["Fernando Alonso", "Lance Stroll"]
}

posizione_giocatore = 0

probabilita_offerta = [
    1, 0.95, 0.90, 0.85, 0.80,
    0.75, 0.70, 0.65, 0.06, 0.55,
    0.50, 0.45, 0.40, 0.35, 0.30,
    0.25, 0.20, 0.15, 0.10, 0.05,
]

# Sistema di punteggio F1
sistema_punti = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]


# Classe per gestire i dati del pilota
class Pilota:
    def __init__(self, nome, scuderia, image, punti=0, punti_gara=0, race_wins=0, rating=randint(50, 100), wdc=None, wcc=None):
        self.nome = nome
        self.image = image
        self.scuderia = scuderia
        self.punti_gara = punti_gara
        self.punti = punti
        self.race_wins = race_wins
        self.rating = rating  # Aggiunto il rating
        self.temp_rating = 0
        self.wdc = []
        self.wcc = []
        self.posizione_finale = None

    def to_dict(self):
        return {
            'nome': self.nome,
            'image': self.image,
            'scuderia': self.scuderia.nome if isinstance(self.scuderia, Scuderia) else self.scuderia,  # Assumendo che scuderia sia un oggetto, prendi il nome
            'punti_gara': self.punti_gara,
            'punti': self.punti,
            'race_wins': self.race_wins,
            'rating': self.rating,
            'temp_rating': self.temp_rating,
            'wdc': self.wdc,
            'wcc': self.wcc,
            'posizione_finale': self.posizione_finale
        }


    def add_temp_rating(self, temp_rating):
        """Aggiunge un bonus o malus per simulare la performance in gara"""
        self.temp_rating = temp_rating
        self.rating += temp_rating

    def guadagna_punti(self, position):
        """Calcola i punti assegnati in base alla posizione finale della gara."""
        points_distribution = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        self.punti_gara = points_distribution.get(position, 0)  # 0 punti per oltre la 10° posizione
        self.punti += self.punti_gara

    def aggiorna_rating(self, posizione):
        # Modifica del rating in base alla posizione finale
        incremento = 0
        if posizione == 1:
            incremento = 3
        elif posizione == 2:
            incremento = 2
        elif posizione == 3:
            incremento = 1
        elif 4 <= posizione <= 15:
            incremento = 0
        elif 16 <= posizione <= 18:
            incremento = -1
        elif posizione == 19:
            incremento = -2
        elif posizione == 20:
            incremento = -3
        # Aggiorna il rating
        self.rating += incremento
        self.rating -= self.temp_rating
        # Il rating non può andare sotto 50 o sopra 100
        self.rating = max(50, min(self.rating, 100))

    def resetta_punti(self):
        self.punti = 0


# Classe per la scuderia
class Scuderia:
    def __init__(self, nome, piloti):
        self.nome = nome
        self.piloti = piloti
        self.wcc = []

    def calcola_punti(self):
        return sum([pilota.punti for pilota in self.piloti])


# Classe per il giocatore
class Giocatore(Pilota):
    def __init__(self, nome, scuderia, image):
        super().__init__(nome, scuderia, image)

    def scegli_squadra(self, offerte):
        if not offerte:
            print("Nessuna offerta disponibile.")
            return None

        print("\nHai ricevuto offerte dalle seguenti scuderie:")
        for idx, scuderia in enumerate(offerte):
            print(f"{idx + 1}. {scuderia.nome}")

        if self.scuderia != "Svincolato":
            print(f"{len(offerte) + 1}. Rimanere in {self.scuderia}")

        try:
            scelta = int(input("Scegli un'opzione: ")) - 1
            if (scelta >= len(offerte) or scelta == "") and self.scuderia == "Svincolato":
                return offerte[0]
            elif (scelta >= len(offerte) or scelta == "") and self.scuderia != "Svincolato":
                return None
            elif 0 <= scelta < len(offerte):  # Verifica che la scelta sia valida
                return offerte[scelta]
            else:
                print("Scelta non valida.")
                return None
        except (ValueError, IndexError):
            print("Scelta non valida, rimani nella scuderia attuale.")
            return None

giocatore = Giocatore("", "", "tbd")

# Funzione per calcolare i trofei del pilota
def calcola_trofei_pilota(pilota):
    return len(pilota.wdc), len(pilota.wcc)


# Funzione per calcolare i trofei della scuderia
def calcola_trofei_scuderia(scuderia):
    return scuderia.wcc


# Funzione per simulare una gara
def simula_gara(piloti, gp_name, giocatore):
    # Aggiungiamo casualità ai rating
    # Ogni pilota riceve un fattore casuale che modifica leggermente il suo rating
    for pilota in piloti:
        variazione_random = random.randint(-3, 3)  # Piccola variazione per simulare imprevedibilità
        pilota.rating += variazione_random

    # Ordina i piloti in base al rating modificato, i migliori avranno un vantaggio
    piloti.sort(key=lambda p: p.rating, reverse=True)

    # Simula la gara con un po' di casualità per ogni posizione
    for posizione, pilota in enumerate(piloti, 1):
        pilota.posizione_finale = posizione
        pilota.guadagna_punti(posizione)
        pilota.aggiorna_rating(posizione)  # Aggiorna il rating dopo la gara

    # Aggiorna il vincitore della gara
    piloti[0].race_wins +=1
    races[gp_names[current_race_count]] = {
        "winner_name": piloti[0].nome,
        "winner_image": piloti[0].image,
        "winner_team": piloti[0].scuderia,
    }

    # Restituisce i piloti ordinati per posizione finale
    return sorted(piloti, key=lambda x: x.posizione_finale)


def crea_offerte(giocatore, probabilita_offerta_giocatore):
    """Genera offerte per ogni scuderia (max 2 offerte per scuderia)"""
    offerte_scuderie = {}

    for scuderia in scuderie:
        offerte_scuderie[scuderia] = []
        # Offerta al giocatore, anche se la scuderia ha già 2 piloti
        if random.random() <= probabilita_offerta_giocatore and giocatore not in scuderia.piloti:
            offerte_scuderie[scuderia].append(giocatore)  # Offerta al giocatore

        # Offerte a piloti di altre scuderie (massimo due offerte totali)
        while len(offerte_scuderie[scuderia]) < 2:
            pilota = random.choice(
                [p for p in piloti if p.scuderia != scuderia and p.scuderia is not None and p not in scuderia.piloti])
            offerte_scuderie[scuderia].append(pilota)

    return offerte_scuderie


def mercato_piloti_ai(offerte_scuderie, notizie_mercato, giocatore, piloti_svincolati):
    # Altri piloti decidono se accettare
    for scuderia, offerte in offerte_scuderie.items():
        for pilota in offerte:
            if pilota.nome != giocatore.nome and random.random() < 0.5:  # 50% probabilità di accettare
                if pilota in piloti_svincolati:
                    piloti_svincolati.remove(pilota)
                # Rimuovere il pilota dalla sua attuale scuderia
                scuderia_attuale_pilota = None
                for scuderia_attuale in scuderie:
                    if pilota in scuderia_attuale.piloti:
                        scuderia_attuale_piloti = scuderia_attuale.nome
                        if pilota in scuderia_attuale.piloti:  # Verifica doppia
                            scuderia_attuale.piloti.remove(pilota)
                        break
                if not scuderia_attuale_pilota:
                    scuderia_attuale_pilota = "Svincolato"
                # Aggiungere alla nuova scuderia o sostituire un pilota
                if len(scuderia.piloti) < 2:
                    scuderia.piloti.append(pilota)
                    pilota.scuderia = scuderia.nome
                    notizie_mercato[pilota.nome] = {
                        "driver": pilota.nome,
                        "oldteam": scuderia_attuale_pilota,
                        "newteam": scuderia.nome,
                    }
                else:
                    pilota_da_sostituire = random.choice(scuderia.piloti)
                    pilota_da_sostituire.scuderia = "Svincolato"
                    scuderia.piloti.remove(pilota_da_sostituire)
                    if pilota_da_sostituire in piloti:
                        piloti.remove(pilota_da_sostituire)
                    piloti_svincolati.append(pilota_da_sostituire)
                    scuderia.piloti.append(pilota)
                    pilota.scuderia = scuderia.nome
                    notizie_mercato[pilota.nome] = {
                        "driver": pilota.nome,
                        "oldteam": scuderia_attuale.nome,
                        "newteam": scuderia.nome,
                        "subsituted": pilota_da_sostituire.nome
                    }

                # Rimuovi tutte le altre offerte per il pilota
                for altra_scuderia, altre_offerte in offerte_scuderie.items():
                    if pilota in altre_offerte:
                        altre_offerte.remove(pilota)
                break  # Uscire dal ciclo, il pilota ha accettato


def mercato_giocatore(scuderia, notizie_mercato, giocatore, piloti_svincolati):
    # Scelta del giocatore
    if scuderia != None and giocatore.scuderia != scuderia.nome:
            if giocatore in piloti_svincolati:
                piloti_svincolati.remove(giocatore)
            nuova_scuderia = scuderia  # nuova_scuderia ora è un oggetto Scuderia
            scuderia_attuale = giocatore.scuderia
            if len(nuova_scuderia.piloti) < 2:  # Se c'è spazio, si aggiunge
                for scuderia in scuderie:
                    if scuderia.nome == giocatore.scuderia:
                        scuderia.piloti.remove(giocatore)
                        giocatore.scuderia = "Svincolato"
                        scuderia_attuale = scuderia.nome
                        break
                giocatore.scuderia = nuova_scuderia.nome
                nuova_scuderia.piloti.append(giocatore)
                notizie_mercato[giocatore.nome] = {
                    "driver": giocatore.nome,
                    "oldteam": scuderia_attuale,
                    "newteam": nuova_scuderia.nome,
                }
            else:  # Se la scuderia è piena, sostituisce un pilota casuale
                scuderia_attuale = giocatore.scuderia
                pilota_da_sostituire = random.choice(nuova_scuderia.piloti)
                nuova_scuderia.piloti.remove(pilota_da_sostituire)
                if pilota_da_sostituire in piloti:
                    piloti.remove(pilota_da_sostituire)
                piloti_svincolati.append(pilota_da_sostituire)
                giocatore.scuderia = nuova_scuderia.nome
                nuova_scuderia.piloti.append(giocatore)
                notizie_mercato[giocatore.nome] = {
                    "driver": giocatore.nome,
                    "oldteam": scuderia_attuale,
                    "newteam": nuova_scuderia.nome,
                    "subsituted": pilota_da_sostituire.nome
                }

    if giocatore in piloti_svincolati and giocatore not in piloti:
        piloti_svincolati.remove(giocatore)
        scuderia = random.choice([scuderia for scuderia in scuderie if len(scuderia.piloti) < 2])
        scuderia.piloti.append(giocatore)
        giocatore.scuderia = scuderia.nome
        scuderia_attuale = "Svincolato"
        notizie_mercato[giocatore.nome] = {
            "driver": giocatore.nome,
            "oldteam": "Svincolato",
            "newteam": scuderia.nome
        }
    elif giocatore in piloti_svincolati:
        piloti_svincolati.remove(giocatore)

    if giocatore in piloti_svincolati and giocatore in piloti:
        piloti_svincolati.remove(giocatore)


def riempi_scuderie(notizie_mercato):
    """
    Riempi le scuderie incomplete con piloti svincolati.
    Aggiorna la lista globale dei piloti e notizie mercato.
    """
    for scuderia in scuderie:
        while len(scuderia.piloti) < 2 and piloti_svincolati:
            # Seleziona un pilota svincolato casuale
            pilota_svincolato = random.choice(piloti_svincolati)
            piloti_svincolati.remove(pilota_svincolato)

            # Aggiungi il pilota alla scuderia
            scuderia.piloti.append(pilota_svincolato)
            pilota_svincolato.scuderia = scuderia.nome

            # Registra il movimento nel mercato
            notizie_mercato[pilota_svincolato.nome] = {
                "driver": pilota_svincolato.nome,
                "oldteam": "Svincolato",
                "newteam": scuderia.nome,
            }

    # Debugging: verifica duplicati
    piloti_visti = set()
    for scuderia in scuderie:
        nuovi_piloti = []
        for pilota in scuderia.piloti:
            if pilota not in piloti_visti:
                piloti_visti.add(pilota)
                nuovi_piloti.append(pilota)
            else:
                # Se il pilota è duplicato, rimuovilo e rimpiazzalo
                if piloti_svincolati:
                    nuovo_pilota = random.choice(piloti_svincolati)
                    piloti_svincolati.remove(nuovo_pilota)
                    nuovo_pilota.scuderia = scuderia.nome
                    notizie_mercato[nuovo_pilota.nome] = {
                        "driver": nuovo_pilota.nome,
                        "oldteam": "Svincolato",
                        "newteam": scuderia.nome,
                    }
                    nuovi_piloti.append(nuovo_pilota)
        scuderia.piloti = nuovi_piloti

    # Rimuove piloti in eccesso
    for scuderia in scuderie:
        while len(scuderia.piloti) > 2:
            pilota_da_rimuovere = random.choice(
                [pilota for pilota in scuderia.piloti if pilota != giocatore]
            )
            scuderia.piloti.remove(pilota_da_rimuovere)
            piloti_svincolati.append(pilota_da_rimuovere)
            pilota_da_rimuovere.scuderia = "Svincolato"

            # Registra il movimento nel mercato
            notizie_mercato[pilota_da_rimuovere.nome] = {
                "driver": pilota_da_rimuovere.nome,
                "oldteam": scuderia.nome,
                "newteam": "Svincolato",
            }

    # Debugging finale
    totale_piloti = sum(len(scuderia.piloti) for scuderia in scuderie)
    print(f"Totale piloti assegnati: {totale_piloti}")



def genera_offerte():
    global posizione_giocatore
    # Probabilità di offerte per il giocatore in base alla posizione
    probabilita_offerta_giocatore = probabilita_offerta[posizione_giocatore - 1]

    offerte_scuderie = crea_offerte(giocatore, probabilita_offerta_giocatore)
    offerte_giocatore = {}

    # Aggiungi le offerte per il giocatore in offerte_giocatore e rimuovile da offerte_scuderie
    for scuderia, offerte in offerte_scuderie.items():
        if giocatore in offerte:
            offerte_giocatore[scuderia] = giocatore
            offerte.remove(giocatore)  # Rimuovi il giocatore dalle offerte_scuderie

    return offerte_giocatore, offerte_scuderie

def gestisci_trasferimenti_1(piloti, scuderie, offerte_scuderie):
    global movimenti_mercato, piloti_svincolati
    notizie_mercato = {}

    mercato_piloti_ai(offerte_scuderie, notizie_mercato, giocatore, piloti_svincolati)

    return notizie_mercato


def gestisci_trasferimenti_2(piloti, scuderie, giocatore, scuderia):
    global movimenti_mercato, piloti_svincolati
    notizie_mercato = {}

    mercato_giocatore(scuderia, notizie_mercato, giocatore, piloti_svincolati)

    riempi_scuderie(notizie_mercato)

    # Verifica che nessun pilota sia in più di una scuderia
    piloti_visti = set()

    for scuderia in scuderie:
        piloti_scuderia = set()  # Per verificare duplicati all'interno della stessa scuderia
        for pilota in scuderia.piloti:
            if pilota in piloti_visti:
                print(f"Errore: {pilota.nome} è in più di una scuderia!")
                exit(0)
            piloti_visti.add(pilota)

            if pilota in piloti_scuderia:
                print(f"Errore: {pilota.nome} è duplicato nella scuderia {scuderia.nome}!")
                exit(0)
            piloti_scuderia.add(pilota)

    for pilota in piloti:
        piloti.remove(pilota)
    for scuderia in scuderie:
        for pilota in scuderia.piloti:
            if pilota not in piloti:
                piloti.append(pilota)

    return notizie_mercato


def calculate_points(position):
    """Calcola i punti assegnati in base alla posizione finale della gara."""
    points_distribution = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    return points_distribution.get(position, 0)  # 0 punti per oltre la 10° posizione# Inizializzazione della simulazione


def serializza_notizie_mercato(notizie_mercato):
    notizie_serializzate = {}
    for nome_pilota, trasferimento in notizie_mercato.items():
        # Verifica se esiste la chiave 'driver'
        driver_name = trasferimento.get("driver") if trasferimento.get("driver") else "Pilota sconosciuto"

        # Gestisce il caso in cui non esiste una squadra precedente o nuova
        old_team = trasferimento.get("oldteam") if trasferimento.get("oldteam") else "Svincolato"
        new_team = trasferimento.get("newteam") if trasferimento.get("newteam") else "Svincolato"

        # Serializza le informazioni
        notizie_serializzate[nome_pilota] = {
            "driver": driver_name,
            "oldteam": old_team,
            "newteam": new_team,
            "subsituted": trasferimento["subsituted"] if trasferimento.get("subsituted") else None
        }

    return notizie_serializzate


@lineup_blueprint.route("/lineup")
def lineup():
    global current_race_count
    global current_season
    global first_start
    if current_race_count >= MAX_RACES:
        current_race_count = 0
        current_season += 1
        for scuderia in scuderie:
            for pilota in scuderia.piloti:
                pilota.punti = 0
    return render_template('lineup.html', teams=scuderie, year=current_season)


@lineup_blueprint.route("/race")
def race():
    global current_race_count
    global current_season
    global giocatore

    if current_race_count < MAX_RACES:
        race_results = simula_gara(piloti, gp_names, giocatore)
        race_name = gp_names[current_race_count]

        current_race_count += 1  # Incrementa dopo aver simulato la gara

        return render_template('race.html', race_results=race_results, race_name=race_name,
                               current_race=current_race_count, max_races=MAX_RACES)
    else:
        races_list = list(races.items())
        return render_template('race-wins.html', races=races_list, current_season=current_season)


@lineup_blueprint.route("/simulate-remaining-races")
def simulate_remaining_races():
    global current_race_count
    global current_season
    global piloti

    # Simula tutte le gare rimanenti
    while current_race_count < MAX_RACES:
        simula_gara(piloti, gp_names, giocatore)
        current_race_count += 1  # Incrementa dopo ogni simulazione

    drivers_sorted = sorted(piloti, key=lambda d: d.punti, reverse=True)

    return render_template('wdc-leaderboard.html', drivers_sorted=drivers_sorted)


@lineup_blueprint.route("/wdc-leaderboard")
def wdc_leaderboard():
    global piloti

    # Ordina i piloti in base ai punti
    drivers_sorted = sorted(piloti, key=lambda d: d.punti, reverse=True)

    return render_template('wdc-leaderboard.html', drivers_sorted=drivers_sorted)


@lineup_blueprint.route("/wcc-leaderboard")
def wcc_leaderboard():
    punti_scuderie = {scuderia: scuderia.calcola_punti() for scuderia in scuderie}

    # Ordinamento delle scuderie per punti
    scuderie_ordinate = sorted(punti_scuderie.items(), key=lambda s: s[1], reverse=True)

    return render_template('wcc-leaderboard.html', teams=scuderie_ordinate)


@lineup_blueprint.route("/season-winners")
def season_winners():
    global market1
    global market2
    global posizione_giocatore
    # Ordina i piloti in base ai punti in ordine decrescente
    classifica_piloti = sorted(piloti, key=lambda d: d.punti, reverse=True)

    # Trova il pilota con il punteggio massimo (vincitore)
    driver_winner = classifica_piloti[0]

    # Trova la posizione del giocatore nella classifica
    for index, pilota in enumerate(classifica_piloti, start=1):
        if pilota.nome == giocatore.nome:
            posizione_giocatore = index
            break

    punti_scuderie = {scuderia: scuderia.calcola_punti() for scuderia in scuderie}
    scuderie_ordinate = sorted(punti_scuderie.items(), key=lambda s: s[1], reverse=True)
    team_winner = scuderie_ordinate[0][0]

    # Aggiungi il titolo WDC al pilota vincitore, evitando duplicati
    if not any(wdc['anno'] == current_season for wdc in driver_winner.wdc):
        driver_winner.wdc.append({'scuderia': driver_winner.scuderia, 'anno': current_season})

    # Aggiungi il titolo WCC alla scuderia vincitrice, evitando duplicati
    if current_season not in team_winner.wcc:
        team_winner.wcc.append(current_season)
        # Aggiorna anche i piloti della scuderia, evitando duplicati
        for driver in team_winner.piloti:
            if not any(wcc['anno'] == current_season for wcc in driver.wcc):
                driver.wcc.append({'scuderia': team_winner.nome, 'anno': current_season})

    market1 = True
    market2 = True

    return render_template('season-winners.html',
                           driver_winner=driver_winner,
                           driver_team=driver_winner.scuderia,
                           team_winner=team_winner,
                           team_winner_points=team_winner.calcola_punti(),
                           year=current_season)


@lineup_blueprint.route("/transfers", methods=['POST'])
def transfers():
    global market2
    global notizie_mercato
    global notizie_serializzate
    if(market2):
        scuderia = None
        if request.form.get('team'):
            nome_scuderia = request.form['team'].lower().replace(" ", "-")
            for s in scuderie:
                if s.nome == nome_scuderia and (s.nome != None or s.nome != ""):
                    scuderia = s
        # Recupera notizie_mercato dalla sessione
        notizie_mercato = session.get('notizie_mercato', {})
        notizie_mercato.update(gestisci_trasferimenti_2(piloti, scuderie, giocatore, scuderia))
        # Serializza notizie_mercato prima di salvarlo nella sessione
        notizie_serializzate = serializza_notizie_mercato(notizie_mercato)
        session['notizie_mercato'] = notizie_serializzate
        market2 = False
    return render_template('transfers.html', notizie_mercato=notizie_serializzate)


@lineup_blueprint.route("/offers")
def offerte_mercato():
    global market1
    global notizie_mercato
    global notizie_serializzate
    global offerte_giocatore
    if market1:
        offerte_giocatore = None
        offerte_giocatore, offerte_scuderia = genera_offerte()
        notizie_mercato = gestisci_trasferimenti_1(piloti, scuderie, offerte_scuderia)
        if giocatore.scuderia is not "Svicolato":
            for scuderia in scuderie:
                if scuderia.nome == giocatore.scuderia:
                    offerte_giocatore.setdefault(scuderia, []).append(giocatore)
        notizie_serializzate = serializza_notizie_mercato(notizie_mercato)
        session['notizie_mercato'] = notizie_serializzate
        market1 = False
    if offerte_giocatore is not None:
        return render_template('offers.html', offerte_giocatore=offerte_giocatore, notizie_mercato=notizie_mercato)
    else:
        return render_template('no-offers.html', notizie_mercato=notizie_mercato)

@lineup_blueprint.route('/team/<team_name>')
def team_info(team_name):
    global scuderie
    # Trova le informazioni del team
    team = next((t for t in scuderie if t.nome == team_name), None)
    if not team:
        return "Team non trovato", 404
    return render_template('team-info.html', team=team)

@lineup_blueprint.route('/hof-wdc')
def hof_wdc():
    global piloti, piloti_svincolati
    wdc_list = sorted([
        {'pilota': pilota, 'scuderia': wdc['scuderia'], 'anno': wdc['anno']}
        for pilota in piloti + piloti_svincolati if pilota.wdc
        for wdc in pilota.wdc
    ],
        key=lambda x: x['anno']
    )
    return render_template('hof-wdc.html', wdc_list=wdc_list)

@lineup_blueprint.route('/hof-wcc')
def hof_wcc():
    global scuderie
    wcc_list = sorted([
        {'scuderia': scuderia.nome, 'anno': anno}
        for scuderia in scuderie
        for anno in scuderia.wcc
    ],
        key=lambda x: x['anno']
    )
    return render_template('hof-wcc.html', wcc_list=wcc_list)

@lineup_blueprint.route('/wdc-titles-leaderboard')
def wdc_titles_leaderboard():
    global scuderie
    wdc_list = sorted([
        {
            'pilota': pilota,
            'scuderia': pilota.wdc[-1]['scuderia'] if pilota.wdc else None,  # Ultima scuderia di WDC
            'titoli': len(pilota.wdc)
        }
        for pilota in piloti + piloti_svincolati if pilota.wdc

    ],
        key=lambda x: x['titoli'],
        reverse=True
    )
    return render_template('wdc-titles-leaderboard.html', wdc_list=wdc_list)

@lineup_blueprint.route('/wcc-titles-leaderboard')
def wcc_titles_leaderboard():
    global scuderie
    wcc_list = sorted([
        {
            'scuderia': scuderia,
            'titoli': len(scuderia.wcc)
        }
        for scuderia in scuderie if scuderia.wcc
    ],
        key=lambda x: x['titoli'],
        reverse=True
    )
    return render_template('wcc-titles-leaderboard.html', wcc_list=wcc_list)
