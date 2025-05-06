import React, {useState, useEffect} from 'react';
import './App.css';
import {useNavigate} from 'react-router-dom';
import {solveFormula} from "./Api";

const LogicFormulaApp = () => {
    const [formula, setFormula] = useState('');
    const [steps, setSteps] = useState([]);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        }
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSteps([]);
        setResult(null);

        const token = localStorage.getItem('token');
        if (!token) {
            setError('You are not logged in. Please log in to solve formulas.');
            navigate('/login');
            return;
        }

        try {
            const response = await solveFormula(formula, token);
            setSteps(response.data.steps);
            setResult(response.data.result);
        } catch (err) {
            if (err.response && err.response.status === 401) {
                setError('Session expired. Please log in again.');
                localStorage.removeItem('token');
                navigate('/login');
            } else {
                setError('An error occurred while processing the formula. Please try again.');
            }
            console.error(err);
        }
    };

    const insertSymbol = (symbol) => {
        const input = document.getElementById("formula");
        if (!input) return;

        const start = input.selectionStart;
        const end = input.selectionEnd;

        const newFormula = formula.substring(0, start) + symbol + formula.substring(end);
        setFormula(newFormula);

        setTimeout(() => {
            input.selectionStart = input.selectionEnd = start + symbol.length;
            input.focus();
        }, 0);
    };

    return (
        <div className="container-sm shadow p-3 mb-5 bg-body-tertiary rounded" style={{width: "70%", marginTop: "2%"}}>
            <form onSubmit={handleSubmit}>
                <div className="input-group mb-3">
                    <input type="text" id="formula" value={formula} onChange={(e) => setFormula(e.target.value)}
                           className="form-control" placeholder="Sem zadejte formuli" required
                    />
                    <button type="submit" className="btn btn-success">Vyřešit</button>
                </div>
                <div className="input-group mb-3">
                    {["¬", "∧", "∨", "→", "↔", "(", ")"].map((symbol) => (
                        <button key={symbol} type="button" className="btn btn-light btn-outline-success"
                                onClick={() => insertSymbol(symbol)}>
                            {symbol}
                        </button>
                    ))}
                </div>
                <div className="input-group mb-3">
                    {["A", "B", "C", "D", "E", "F", "G"].map((symbol) => (
                        <button key={symbol} type="button" className="btn btn-light btn-outline-success"
                                onClick={() => insertSymbol(symbol)}>
                            {symbol}
                        </button>
                    ))}
                </div>
            </form>

            {error && <p className="error">{error}</p>}

            {steps.length > 0 && (
                <div>
                    <h2 className="sub-header">Postup řešení</h2>
                    <ul className="list-group list-group-flush">
                        {steps.map((step, index) => (
                            <div key={index} className="list-group-item" style={{
                                backgroundColor: index === steps.length - 1 ? (result ? "#198754" : "#dc3545") : "transparent",
                                color: index === steps.length - 1 ? "white" : "black",
                                fontWeight: index === steps.length - 1 && result ? "bold" : "normal"
                            }}>
                                {step}
                            </div>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default LogicFormulaApp;
