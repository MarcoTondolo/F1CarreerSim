from random import randint
from flask import Blueprint, render_template, request, session
import datetime
import json

lineup_blueprint = Blueprint('lineup', __name__)

market1 = True
market2 = True
notizie_mercato = {}
notizie_serializzate = {}
offerte_giocatore = None
regulation_changes = 4

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


def set_year(year):
    global current_season
    current_season = year

import random
import datetime

# Lista dei piloti svincolati
nomi_piloti_svincolati_iniziali = [
    "Logan Sargeant", "Jack Doohan", "Kevin Magnussen", "Daniel Ricciardo", "Guanyu Zhou",
    "Sergio Perez", "Valtteri Bottas"
]
piloti_svincolati = []
scuderie = []
piloti = []

# Scuderie e piloti
scuderie_piloti = {
    "red-bull": ["Max Verstappen", "Yuki Tsunoda"],
    "ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    "mclaren": ["Lando Norris", "Oscar Piastri"],
    "racing-bulls": ["Liam Lawson", "Isack Hadjar"],
    "haas": ["Oliver Bearman", "Esteban Ocon"],
    "mercedes": ["George Russell", "Kimi Antonelli"],
    "alpine": ["Pierre Gasly", "Franco Colapinto"],
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
    def __init__(self, nome, scuderia, image, punti=0, punti_gara=0, race_wins=0, rating=randint(50, 100),
                 temp_rating=0, wdc=None, wcc=None):
        self.nome = nome
        self.image = image
        self.scuderia = scuderia
        self.punti_gara = punti_gara
        self.punti = punti
        self.race_wins = race_wins
        self.rating = rating  # Aggiunto il rating
        self.temp_rating = temp_rating
        self.wdc = [] if wdc is None else wdc
        self.wcc = [] if wcc is None else wcc
        self.posizione_finale = None
        self.last_position = None
        self.last_race_position = None
        self.leaderboard_change = None

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
        """Aggiunge un bonus o malus per simulare la performance in gara, influenzata dal rating della scuderia."""
        scuderia_rating = 0

        for scuderia in scuderie:
            if self.scuderia == scuderia.nome:
                scuderia_rating = scuderia.rating

        if scuderia_rating >= 90:
            effetto_scuderia = random.randint(-1, 3)
        elif scuderia_rating >= 70:
            effetto_scuderia = random.randint(-1, 2)
        else:
            effetto_scuderia = random.randint(-1, 1)

        # Il bonus/malus viene aggiunto al `temp_rating`
        self.temp_rating = temp_rating + effetto_scuderia

        # Aggiorna il rating del pilota
        self.rating += self.temp_rating

    def guadagna_punti(self, position):
        """Calcola i punti assegnati in base alla posizione finale della gara."""
        points_distribution = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        self.punti_gara = points_distribution.get(position, 0)  # 0 punti per oltre la 10° posizione
        self.punti += self.punti_gara

    def aggiorna_rating(self, posizione):
        incremento = 0
        if posizione <= 3:
            incremento += random.randint(-1, 3)
        elif posizione <= 10:
            incremento += random.randint(-1, 2)
        else:
            incremento -= random.randint(-2, 1)

        # BONUS per i piloti che migliorano molto rispetto alla gara precedente
        if self.last_race_position:
            miglioramento = self.last_race_position - posizione  # Se positivo, significa che è migliorato
            if miglioramento > 5:
                incremento += random.randint(2, 4)  # Ricompensa extra se ha guadagnato molte posizioni
            elif miglioramento > 2:
                incremento += random.randint(1, 3)

        self.rating += incremento

        self.rating -= self.temp_rating

        # Il rating non può andare sotto 50 o sopra 100
        self.rating = max(80, min(self.rating, 100))

    def resetta_punti(self):
        self.punti = 0


# Classe per la scuderia
class Scuderia:
    def __init__(self, nome, piloti, rating = randint(50, 100)):
        self.nome = nome
        self.piloti = piloti
        self.rating = rating
        self.wcc = []
        self.last_position = None
        self.leaderboard_change = None

    def calcola_punti(self):
        return sum([pilota.punti for pilota in self.piloti])

    def reset_rating_scuderia(self):
        self.rating = randint(50, 100)

    def aggiorna_rating_scuderia(self, posizione, piloti):
        """Bilancia il rating della scuderia in base ai risultati della gara, suddividendo le squadre in fasce."""
        punteggio = 0
        miglioramento = 0

        # Suddivisione delle fasce: Alta (1-3), Media (4-7), Bassa (8-10)
        if posizione <= 3:
            fascia = "alta"
        elif 4 <= posizione <= 7:
            fascia = "media"
        else:
            fascia = "bassa"

        # Somma le posizioni dei piloti con bilanciamento
        for pilota in piloti:
            last_position_int = int(pilota.posizione_finale)
            if last_position_int == 1:
                punteggio += 18  # Ridotto per evitare sbilanciamenti
            elif last_position_int == 2:
                punteggio += 14
            elif last_position_int == 3:
                punteggio += 12
            elif 4 <= last_position_int <= 7:
                punteggio += 8
            elif 8 <= last_position_int <= 10:
                punteggio += 5
            elif 11 <= last_position_int <= 15:
                punteggio += 3
            elif 16 <= last_position_int <= 20:
                punteggio += 1

        # Bonus per miglioramento con bilanciamento delle fasce
        if self.last_position:
            miglioramento = self.last_position - posizione  # Se positivo, significa che è migliorato
            if miglioramento > 5:
                if fascia == "bassa":
                    punteggio += random.randint(3, 5)  # Più alto per team bassi
                elif fascia == "media":
                    punteggio += random.randint(2, 4)
                else:
                    punteggio += random.randint(1, 3)
            elif miglioramento > 2:
                if fascia == "bassa":
                    punteggio += random.randint(2, 4)
                elif fascia == "media":
                    punteggio += random.randint(1, 3)
                else:
                    punteggio += random.randint(1, 2)

        # Penalità per peggioramento con scalature bilanciate
        if miglioramento < -5:
            if fascia == "alta":
                punteggio -= 10  # Penalità più severa per i top team
            elif fascia == "media":
                punteggio -= 7
            else:
                punteggio -= 5  # Penalità più leggera per team bassi
        elif miglioramento < -2:
            if fascia == "alta":
                punteggio -= 7
            elif fascia == "media":
                punteggio -= 5
            else:
                punteggio -= 3

        # Assicurati che il punteggio sia nei limiti
        self.rating = max(50, min(self.rating + punteggio, 100))


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


def salva_dati(scuderie, giocatore, filename="dati_f1.json"):
    """Salva i dati delle scuderie, dei piloti e del giocatore in un file JSON."""
    print("Salvataggio...")
    dati = {
        "scuderie": [
            {
                "nome": scuderia.nome,
                "piloti": [pilota.to_dict() for pilota in scuderia.piloti],
                "wcc": scuderia.wcc,
                "last_position": scuderia.last_position,
                "leaderboard_change": scuderia.leaderboard_change,
                "rating": scuderia.rating
            }
            for scuderia in scuderie
        ],
        "piloti_svincolati": [pilota.to_dict() for pilota in piloti_svincolati],
        "giocatore": giocatore.to_dict(),
        "current_season": current_season
    }

    print(dati)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dati, file, indent=4, ensure_ascii=False)
    print("Dati salvati con successo.")

# Funzione per calcolare i trofei del pilota
def calcola_trofei_pilota(pilota):
    return len(pilota.wdc), len(pilota.wcc)


# Funzione per calcolare i trofei della scuderia
def calcola_trofei_scuderia(scuderia):
    return scuderia.wcc


# Funzione per simulare una gara
def simula_gara(piloti, gp_name):
    # Aggiungiamo casualità ai rating
    # Ogni pilota riceve un fattore casuale che modifica leggermente il suo rating
    for pilota in piloti:
        variazione_random = random.randint(-5, 5)
        pilota.add_temp_rating(variazione_random)

    # Ordina i piloti in base al rating modificato, i migliori avranno un vantaggio
    piloti.sort(key=lambda p: p.rating, reverse=True)

    # Simula la gara con un po' di casualità per ogni posizione
    for posizione, pilota in enumerate(piloti, 1):
        pilota.posizione_finale = posizione
        pilota.guadagna_punti(posizione)
        pilota.aggiorna_rating(posizione)  # Aggiorna il rating dopo la gara
        pilota.last_race_position = posizione

    # Aggiorna il vincitore della gara
    piloti[0].race_wins +=1
    races[gp_name] = {
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
            offerte_scuderie[scuderia].append(giocatore)

        # Offerte a piloti di altre scuderie (massimo due offerte totali)
        while len(offerte_scuderie[scuderia]) < 2:
            candidati = [p for p in piloti if p.scuderia != scuderia and p.scuderia is not None and p not in scuderia.piloti]
            if not candidati:
                break
            pilota = random.choice(candidati)
            offerte_scuderie[scuderia].append(pilota)

    return offerte_scuderie


def mercato_piloti_ai(offerte_scuderie, notizie_mercato, giocatore, piloti_svincolati):
    """
    Gestisce le offerte rivolte ai piloti (escluso il giocatore) e la loro eventuale accettazione.
    Per ciascuna offerta, c'è il 50% di probabilità che il pilota accetti.
    """
    for scuderia, offerte in offerte_scuderie.items():
        for pilota in offerte:
            if pilota.nome != giocatore.nome and random.random() < 0.5:  # 50% probabilità di accettare
                if pilota in piloti_svincolati:
                    piloti_svincolati.remove(pilota)
                # Rimuove il pilota dalla scuderia attuale (se presente)
                scuderia_attuale = None
                for s in scuderie:
                    if pilota in s.piloti:
                        s.piloti.remove(pilota)
                        scuderia_attuale = s.nome
                        break
                if not scuderia_attuale:
                    scuderia_attuale = "Svincolato"

                # Se la nuova scuderia ha spazio, aggiunge il pilota, altrimenti sostituisce un pilota esistente
                if len(scuderia.piloti) < 2:
                    scuderia.piloti.append(pilota)
                    pilota.scuderia = scuderia.nome
                    notizie_mercato[pilota.nome] = {
                        "driver": pilota.nome,
                        "oldteam": scuderia_attuale,
                        "newteam": scuderia.nome,
                    }
                else:
                    pilota_da_sostituire = random.choice(scuderia.piloti)
                    scuderia.piloti.remove(pilota_da_sostituire)
                    pilota_da_sostituire.scuderia = "Svincolato"
                    if pilota_da_sostituire in piloti:
                        piloti.remove(pilota_da_sostituire)
                    piloti_svincolati.append(pilota_da_sostituire)
                    scuderia.piloti.append(pilota)
                    pilota.scuderia = scuderia.nome
                    notizie_mercato[pilota.nome] = {
                        "driver": pilota.nome,
                        "oldteam": scuderia_attuale,
                        "newteam": scuderia.nome,
                        "subsituted": pilota_da_sostituire.nome
                    }

                # Rimuove il pilota da eventuali altre offerte nelle altre scuderie
                for altre_scuderia, altre_offerte in offerte_scuderie.items():
                    if pilota in altre_offerte:
                        altre_offerte.remove(pilota)
                break  # Il pilota ha accettato, passa alla prossima offerta


def mercato_giocatore(scuderia, notizie_mercato, giocatore, piloti_svincolati):
    """
    Gestisce il trasferimento del giocatore:
    - Se il giocatore sceglie una nuova scuderia, lo trasferisce sostituendo un pilota se necessario.
    - Se il giocatore è svincolato, lo inserisce in una scuderia disponibile.
    """
    if scuderia and giocatore.scuderia != scuderia.nome:
        if giocatore in piloti_svincolati:
            piloti_svincolati.remove(giocatore)

        scuderia_attuale = giocatore.scuderia

        # Se c'è spazio, trasferisce il giocatore
        if len(scuderia.piloti) < 2:
            # Rimuove il giocatore dalla scuderia precedente, se presente
            for s in scuderie:
                if s.nome == giocatore.scuderia and giocatore in s.piloti:
                    s.piloti.remove(giocatore)
                    scuderia_attuale = s.nome
                    break
            giocatore.scuderia = scuderia.nome
            scuderia.piloti.append(giocatore)
            notizie_mercato[giocatore.nome] = {
                "driver": giocatore.nome,
                "oldteam": scuderia_attuale,
                "newteam": scuderia.nome,
            }
        else:
            # Se la scuderia è piena, sostituisce un pilota esistente
            pilota_da_sostituire = random.choice(scuderia.piloti)
            scuderia.piloti.remove(pilota_da_sostituire)
            if pilota_da_sostituire in piloti:
                piloti.remove(pilota_da_sostituire)
            piloti_svincolati.append(pilota_da_sostituire)
            giocatore.scuderia = scuderia.nome
            scuderia.piloti.append(giocatore)
            notizie_mercato[giocatore.nome] = {
                "driver": giocatore.nome,
                "oldteam": scuderia_attuale,
                "newteam": scuderia.nome,
                "subsituted": pilota_da_sostituire.nome
            }

    # Se il giocatore risulta ancora svincolato e non è presente nella lista principale,
    # viene assegnato ad una scuderia disponibile
    if giocatore in piloti_svincolati and giocatore not in piloti:
        piloti_svincolati.remove(giocatore)
        scuderia_disponibile = random.choice([s for s in scuderie if len(s.piloti) < 2])
        scuderia_disponibile.piloti.append(giocatore)
        giocatore.scuderia = scuderia_disponibile.nome
        notizie_mercato[giocatore.nome] = {
            "driver": giocatore.nome,
            "oldteam": "Svincolato",
            "newteam": scuderia_disponibile.nome
        }
    elif giocatore in piloti_svincolati:
        piloti_svincolati.remove(giocatore)


def riempi_scuderie(notizie_mercato):
    global piloti_svincolati
    """
    Riempi le scuderie incomplete con piloti svincolati.
    Aggiorna la lista globale dei piloti e registra le notizie di mercato.
    """

    duplicati_presenti = True
    while duplicati_presenti:
        duplicati_presenti = False

        # Controllo duplicati nelle scuderie (confronto tramite p.nome)
        piloti_visti = set()
        for s in scuderie:
            piloti_validi = []
            for p in s.piloti:
                if p.nome in piloti_visti:
                    print(f"Rimosso duplicato: {p.nome} dalla scuderia {s.nome}")
                    # Aggiunge il pilota duplicato ai piloti svincolati, se non già presente
                    if all(p.nome != ps.nome for ps in piloti_svincolati):
                        piloti_svincolati.append(p)
                    duplicati_presenti = True
                else:
                    piloti_visti.add(p.nome)
                    piloti_validi.append(p)
            s.piloti = piloti_validi

        # Controllo duplicati nella lista dei piloti svincolati (confronto tramite p.nome)
        piloti_svincolati_validi = []
        piloti_visti_svincolati = set()
        for p in piloti_svincolati:
            if p.nome in piloti_visti_svincolati:
                print(f"Rimosso duplicato: {p.nome} dalla lista dei piloti svincolati")
                duplicati_presenti = True
            else:
                piloti_visti_svincolati.add(p.nome)
                piloti_svincolati_validi.append(p)
        piloti_svincolati = piloti_svincolati_validi

    # Rimuove eventuali piloti in eccesso (oltre il limite di 2 per scuderia)
    for scuderia in scuderie:
        while len(scuderia.piloti) > 2:
            pilota_da_rimuovere = random.choice([p for p in scuderia.piloti if p != giocatore])
            scuderia.piloti.remove(pilota_da_rimuovere)
            piloti_svincolati.append(pilota_da_rimuovere)
            pilota_da_rimuovere.scuderia = "Svincolato"
            notizie_mercato[pilota_da_rimuovere.nome] = {
                "driver": pilota_da_rimuovere.nome,
                "oldteam": scuderia.nome,
                "newteam": "Svincolato",
            }
        # Assegna i piloti svincolati alle scuderie incomplete
        for scuderia in scuderie:
            while len(scuderia.piloti) < 2 and piloti_svincolati:
                pilota_svincolato = random.choice(piloti_svincolati)
                piloti_svincolati.remove(pilota_svincolato)
                scuderia.piloti.append(pilota_svincolato)
                pilota_svincolato.scuderia = scuderia.nome
                notizie_mercato[pilota_svincolato.nome] = {
                    "driver": pilota_svincolato.nome,
                    "oldteam": "Svincolato",
                    "newteam": scuderia.nome,
                }

    print(f"Totale piloti assegnati: {sum(len(s.piloti) for s in scuderie)}")


def genera_offerte():
    global posizione_giocatore
    probabilita_offerta_giocatore = probabilita_offerta[posizione_giocatore - 1]

    offerte_scuderie = crea_offerte(giocatore, probabilita_offerta_giocatore)
    offerte_giocatore = {}

    # Estrae le offerte rivolte al giocatore e le rimuove dalle offerte per le scuderie
    for s, offerte in offerte_scuderie.items():
        if giocatore in offerte:
            offerte_giocatore.setdefault(s, []).append(giocatore)
            offerte.remove(giocatore)

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

    # Verifica che ogni pilota sia assegnato a una sola scuderia
    piloti_visti = set()
    for s in scuderie:
        for p in s.piloti:
            if p in piloti_visti:
                print(f"Errore: {p.nome} è in più di una scuderia!")
                exit(0)
            piloti_visti.add(p)

    # Aggiorna la lista globale dei piloti in base alle assegnazioni nelle scuderie
    piloti.clear()
    for s in scuderie:
        for p in s.piloti:
            if p not in piloti:
                piloti.append(p)

    return notizie_mercato


def serializza_notizie_mercato(notizie_mercato):
    """Serializza il dizionario delle notizie di mercato per la sessione"""
    notizie_serializzate = {}
    for nome_pilota, trasferimento in notizie_mercato.items():
        driver = trasferimento.get("driver", "Pilota sconosciuto")
        old_team = trasferimento.get("oldteam", "Svincolato")
        new_team = trasferimento.get("newteam", "Svincolato")
        substituted = trasferimento.get("subsituted", None)

        notizie_serializzate[nome_pilota] = {
            "driver": driver,
            "oldteam": old_team,
            "newteam": new_team,
            "subsituted": substituted
        }
    return notizie_serializzate


def calculate_points(position):
    """Calcola i punti assegnati in base alla posizione finale della gara."""
    points_distribution = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    return points_distribution.get(position, 0)  # 0 punti per oltre la 10° posizione# Inizializzazione della simulazione


@lineup_blueprint.route("/lineup")
def lineup():
    global current_race_count, current_season, regulation_changes
    if current_race_count >= MAX_RACES:
        current_race_count = 0
        current_season += 1
        if regulation_changes == 4:
            regulation_changes = 0
            for scuderia in scuderie:
                scuderia.reset_rating_scuderia()
            print("New Regulations")
        regulation_changes += 1
        for scuderia in scuderie:
            for pilota in scuderia.piloti:
                pilota.punti = 0
                pilota.last_position = None
                pilota.leaderboard_change = None
                pilota.last_race_position = None
    salva_dati(scuderie, giocatore)
    return render_template('lineup.html', teams=scuderie, year=current_season)


@lineup_blueprint.route("/race")
def race():
    global current_race_count
    global current_season
    global giocatore

    if current_race_count < MAX_RACES:
        race_name = gp_names[current_race_count]
        race_results = simula_gara(piloti, race_name)

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
        race_name = gp_names[current_race_count]
        simula_gara(piloti, race_name)
        current_race_count += 1  # Incrementa dopo ogni simulazione

    drivers_sorted = sorted(piloti, key=lambda d: d.punti, reverse=True)

    return render_template('wdc-leaderboard.html', drivers_sorted=drivers_sorted)


@lineup_blueprint.route("/wdc-leaderboard")
def wdc_leaderboard():
    global piloti

    # Ordina i piloti in base ai punti
    drivers_sorted = sorted(piloti, key=lambda d: d.punti, reverse=True)
    for posizione, pilota in enumerate(drivers_sorted, 1):
        if pilota.last_position:
            pilota.leaderboard_change = "up" if posizione < pilota.last_position else \
                                        "down" if posizione > pilota.last_position else None
        pilota.last_position = posizione

    return render_template('wdc-leaderboard.html', drivers_sorted=drivers_sorted)


@lineup_blueprint.route("/wcc-leaderboard")
def wcc_leaderboard():
    punti_scuderie = {scuderia: scuderia.calcola_punti() for scuderia in scuderie}

    # Ordinamento delle scuderie per punti
    scuderie_ordinate = sorted(punti_scuderie.items(), key=lambda s: s[1], reverse=True)
    for posizione, (scuderia, _) in enumerate(scuderie_ordinate, 1):
        if scuderia.last_position:
            scuderia.leaderboard_change = "up" if posizione < scuderia.last_position else \
                                        "down" if posizione > scuderia.last_position else None
        scuderia.last_position = posizione
        for scuderiaReal in scuderie:
            if scuderiaReal.nome == scuderia.nome:
                scuderiaReal.aggiorna_rating_scuderia(posizione, piloti)

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
    global market2, notizie_mercato, notizie_serializzate
    if market2:
        scuderia_selezionata = None
        if request.form.get('team'):
            nome_scuderia = request.form['team'].lower().replace(" ", "-")
            for s in scuderie:
                if s.nome == nome_scuderia and s.nome:
                    scuderia_selezionata = s
                    break

        notizie_mercato = session.get('notizie_mercato', {})
        notizie_mercato.update(gestisci_trasferimenti_2(piloti, scuderie, giocatore, scuderia_selezionata))
        notizie_serializzate = serializza_notizie_mercato(notizie_mercato)
        session['notizie_mercato'] = notizie_serializzate
        market2 = False
    return render_template('transfers.html', notizie_mercato=notizie_serializzate)


@lineup_blueprint.route("/offers")
def offerte_mercato():
    global market1, notizie_mercato, notizie_serializzate, offerte_giocatore
    if market1:
        offerte_giocatore = {}
        offerte_giocatore, offerte_scuderia = genera_offerte()
        notizie_mercato = gestisci_trasferimenti_1(piloti, scuderie, offerte_scuderia)
        # Se il giocatore è già assegnato, lo aggiunge alle offerte della sua scuderia
        if giocatore.scuderia != "Svincolato":
            for s in scuderie:
                if s.nome == giocatore.scuderia:
                    offerte_giocatore.setdefault(s, []).append(giocatore)
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
    visti = set()
    wdc_list = []
    for pilota in piloti + piloti_svincolati:
        for wdc in pilota.wdc:
            chiave = (pilota.nome, wdc['anno'])
            if chiave not in visti:
                visti.add(chiave)
                wdc_list.append({
                    'pilota': pilota,
                    'scuderia': wdc['scuderia'],
                    'anno': wdc['anno']
                })
    wdc_list.sort(key=lambda x: x['anno'], reverse=True)
    return render_template('hof-wdc.html', wdc_list=wdc_list)

@lineup_blueprint.route('/hof-wcc')
def hof_wcc():
    global scuderie
    visti = set()
    wcc_list = []

    for scuderia in scuderie:
        for anno in scuderia.wcc:
            chiave = (scuderia.nome, anno)
            if chiave not in visti:
                visti.add(chiave)
                wcc_list.append({
                    'scuderia': scuderia.nome,
                    'anno': anno
                })

    wcc_list.sort(key=lambda x: x['anno'], reverse=True)
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
