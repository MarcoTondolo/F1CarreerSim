import React, { useState, useEffect } from "react";
import {Link, useNavigate} from "react-router-dom";

const Lineup = () => {
    const RACE = '/race'
    const RESET = '/'

    const [anno, setAnno] = useState(2025);
    const [teams, setTeams] = useState([]);
    const history = useNavigate();

    useEffect(() => {
        const init = async () => {
            try {
                const response = await fetch("http://localhost:5000/lineup");
                const json = await response.json();
                setAnno(json.year);
                setTeams(json.teams);
            } catch (error) {
                console.error("Errore nel recupero dei dati:", error);
            }
        };

        init();
    }, []);

    const handleRedirectBack = () => {
        history(RESET);
    };

    const handleRedirectNext = () => {
        history(RACE);
    };

    const teamFileName = (nome) => {
        return nome.replace(/ /g, '-');
    }

    const driverFileName = (nome) => {
        return nome.split(' ').pop().toLowerCase();
    }

    return (
        <body>
        <h1 id={"title"}>Lineup {anno}</h1>

        <div className="main-container">
            <div className="grid-container">
                {teams.map((team) => {
                    const teamLogo = require(`./public/static/images/logos/${teamFileName(team.nome)}.png`);
                    const teamJacket = require(`./public/static/images/jackets/${teamFileName(team.nome)}-jacket.png`);
                    return (
                    <Link to={`/team/${team.nome}`} className={"team-container"}>
                        <div className={`grid-item ${ team.nome }`} id={`team-${ team.nome }`}>
                            <div className="team-logo">
                                <img src={`${teamLogo}`}
                                     alt={`${team.nome}`}
                                     draggable="false"/>
                            </div>
                            <div className="driver-info" id={`driver-info-${ team.nome }`} draggable="false">
                                {team.piloti.map((driver) => {
                                    const driverFace = require(`./public/static/images/drivers/${driverFileName(driver.image)}.png`);
                                    return (
                                    <div className="driver" id={`driver-${ team.nome }-${ driver.image }`} draggable="false"
                                         data-team={`${ team.nome }`}>
                                        <img src={`${driverFace}`}
                                             alt={`${ driver.image }`} className="driver-image"/>
                                        <div className="jacket">
                                            <img
                                                src={`${teamJacket}`}
                                                alt={`${ team.nome }`} className="driver-jacket" draggable="false"/>
                                        </div>
                                        <div className="driver-name">
                                            <div className="driver-name-wrapper">{driver.nome}</div>
                                        </div>
                                    </div>
                                )})}
                            </div>
                        </div>
                    </Link>
                )})}
                <div className="footer-bar">
                    <button onClick={handleRedirectNext} className="next-button" id="redirect-button-next">
                        <div className="next-button-text">
                            Next
                        </div>
                    </button>
                    <button onClick={handleRedirectBack} className="back-button" id="redirect-button-back">
                        <div className="back-button-text">
                            Reset
                        </div>
                    </button>
                </div>
            </div>
        </div>
        </body>
    );
}

export default Lineup;
