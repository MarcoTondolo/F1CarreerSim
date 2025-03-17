import React from 'react';
import ReactDOM from 'react-dom/client';  // Usa questa importazione per React 18+
import './index.css';  // File CSS globale
import App from './App';  // La tua app principale
import { BrowserRouter } from 'react-router-dom';  // Importa BrowserRouter per il routing

// Se stai usando React 18, usa ReactDOM.createRoot
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <BrowserRouter>
        <App />
    </BrowserRouter>
);
