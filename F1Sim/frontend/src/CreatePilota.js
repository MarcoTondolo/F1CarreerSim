import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const CreatePilota = () => {
    const LINEUP = '/lineup';

    const history = useNavigate();
    const [teams, setTeams] = useState([]);
    const [selectedTeam, setSelectedTeam] = useState("");

    useEffect(() => {
        const init = async () => {
            try {
                const response = await fetch("http://localhost:5000/crea-pilota");
                const json = await response.json();
                setTeams(json.teams);
                console.log(json);
            } catch (error) {
                console.error("Errore nel recupero dei dati:", error);
            }
        };

        init();
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault(); // Previene il comportamento predefinito del form

        if (!selectedTeam) {
            alert("Seleziona un team!");
            return;
        }

        try {
            const response = await fetch("http://localhost:5000/aggiungi_pilota", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    team: selectedTeam,  // Passa il team selezionato
                }).toString(),
            });

            if (response.ok) {
                // Se la risposta è ok, puoi fare il redirect
                history(LINEUP);
            } else {
                console.error("Errore nel creare il pilota.");
            }
        } catch (error) {
            console.error("Errore nella richiesta:", error);
        }
    };

    const formattedTeamName = (nome) => {
        return nome.replace(/-/g, ' ')  // Sostituisce trattini con spazi
            .toLowerCase()  // Converte tutto in minuscolo
            .replace(/(?:^|\s)\S/g, (match) => match.toUpperCase());
    }

    return (
        <div className="crea_pilota">
            <h1>Crea il tuo pilota</h1>

            <form>
                <h2>Seleziona un team</h2>
                <div className="teams-selection">
                    {teams.map((team, index) => {
                        const imageUrl = require(`./public/static/images/logos/${team.nome.replace(/ /g, '-')}.png`);
                        return (
                            <div key={index} className="team-option">
                                <input
                                    type="radio"
                                    id={`team_${index}`}
                                    name="team"
                                    value={team.nome}
                                    required
                                    onChange={(e) => setSelectedTeam(e.target.value)}
                                />
                                <label htmlFor={`team_${index}`}>
                                    <img
                                        src={imageUrl}
                                        alt={`${team.nome} logo`}
                                        className={"team-image"}
                                    />
                                    <div className="team-name">{formattedTeamName(team.nome)}</div>
                                </label>
                            </div>
                        );
                    })}
                </div>

                <div className="footer-bar">
                    <button onClick={handleSubmit} type="button" className="next-button" id="redirect-button">
                        <div className="next-button-text">
                            Crea Pilota
                        </div>
                    </button>
                </div>
            </form>
        </div>
    );
}

export default CreatePilota;
