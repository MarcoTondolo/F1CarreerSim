import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const TeamInfo = () => {
    const LINEUP = '/lineup';

    const { teamName } = useParams();
    const [team, setTeam] = useState(null);
    const history = useNavigate();

    useEffect(() => {
        if (!teamName) return;  // Evita di eseguire il fetch se teamName non è valido

        const init = async () => {
            try {
                console.log(`Fetching: http://localhost:5000/team/${teamName}`);

                const response = await fetch(`http://localhost:5000/team/${teamName}`);

                console.log(`Response Status: ${response.status}`);

                const json = await response.json();
                setTeam(json.team);
            } catch (error) {
                console.error("Errore nel recupero dei dati:", error);
            }
        };

        init();
    }, [teamName]);

    const handleRedirect = () => {
        history(LINEUP);
    };

    return (
        <div>
            {team ? (
                <>
                    <h1 id={"title"}>{team.nome.replace('-', ' ').toUpperCase()}</h1>
                    <div className="team-info-container">
                        <div className="team-logo-container">
                            <img
                                src={`/static/images/logos/${team.nome}.png`}
                                alt={team.nome}
                                className="team-logo-large"
                            />
                        </div>
                        <div className="team-car-container">
                            <img
                                src={`/static/images/cars/${team.nome}-car.png`}
                                alt={team.nome}
                                className="team-car"
                            />
                        </div>
                        <section className="team-details">
                            {team.wcc && team.wcc.length > 0 && (
                                <>
                                    <h3>WCC ({team.wcc.length})</h3>
                                    {team.wcc.map((anno, index) => (
                                        <div key={index}>{anno}</div>
                                    ))}
                                </>
                            )}
                        </section>
                        <div className={`grid-item ${team.nome}`} id={`team-${team.nome}`}>
                            <div className="driver-info" id={`driver-info-${team.nome}`} draggable="false">
                                {team.piloti.map((driver) => (
                                    <div
                                        key={driver.image}
                                        className="driver"
                                        id={`driver-${team.nome}-${driver.image}`}
                                        draggable="false"
                                        data-team={team.nome}
                                    >
                                        <img
                                            src={`/static/images/drivers/${driver.image}.png`}
                                            alt={driver.image}
                                            className="driver-image"
                                        />
                                        <div className="jacket">
                                            <img
                                                src={`/static/images/jackets/${team.nome.replace(' ', '-')}-jacket.png`}
                                                alt={team.nome}
                                                className="driver-jacket"
                                                draggable="false"
                                            />
                                        </div>
                                        <div className="driver-name">
                                            <div className="driver-name-wrapper">{driver.nome}</div>
                                        </div>
                                        <h3>Race Wins</h3>
                                        <p>{driver.race_wins}</p>

                                        {driver.wdc && driver.wdc.length > 0 && (
                                            <>
                                                <h3>WDC ({driver.wdc.length})</h3>
                                                {driver.wdc.map((wdc, index) => (
                                                    <div key={index}>
                                                        {wdc.scuderia.replace('-', ' ').toUpperCase()} ({wdc.anno})
                                                    </div>
                                                ))}
                                            </>
                                        )}

                                        {driver.wcc && driver.wcc.length > 0 && (
                                            <>
                                                <h3>WCC ({driver.wcc.length})</h3>
                                                {driver.wcc.map((wcc, index) => (
                                                    <div key={index}>
                                                        {wcc.scuderia.replace('-', ' ').toUpperCase()} ({wcc.anno})
                                                    </div>
                                                ))}
                                            </>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <p>Caricamento dati...</p>
            )}

            <div className="footer-bar">
                <button
                    className="next-button"
                    id="redirect-button"
                    onClick={handleRedirect}
                >
                    <div className="next-button-text">Back</div>
                </button>
            </div>
        </div>
    );
};

export default TeamInfo;
