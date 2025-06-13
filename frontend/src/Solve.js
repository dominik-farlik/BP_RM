import React, {useState, useEffect, useRef} from 'react';
import './App.css';
import {useNavigate} from 'react-router-dom';
import {solveFormula} from "./Api";
import History from "./History";

const LogicFormulaApp = () => {
    const [formula, setFormula] = useState('');
    const [conclusion, setConclusion] = useState('');
    const [steps, setSteps] = useState([]);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const activeInputRef = useRef(null);


    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        }
    }, [navigate]);

    const handleSelectHistory = (premise, conclusion) => {
        setFormula(premise);
        setConclusion(conclusion);
    };


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
            const response = await solveFormula(formula, conclusion);
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
    const input = activeInputRef.current;
    if (!input) return;

    const start = input.selectionStart;
    const end = input.selectionEnd;

    const isFormula = input.id === 'formula';
    const currentValue = isFormula ? formula : conclusion;
    const newValue = currentValue.substring(0, start) + symbol + currentValue.substring(end);

    if (isFormula) {
      setFormula(newValue);
    } else {
      setConclusion(newValue);
    }

    // Obnovení pozice kurzoru
    setTimeout(() => {
      input.selectionStart = input.selectionEnd = start + symbol.length;
      input.focus();
    }, 0);
    };

    return (
        <div className="container-sm shadow p-3 mb-5 bg-body-tertiary rounded" style={{width: "70%", marginTop: "2%"}}>
            <form onSubmit={handleSubmit}>
                <div className="input-group mb-3">
                    <span className="input-group-text" id="basic-addon1">Předpoklad</span>
                    <input type="text"
                           id="formula"
                           value={formula}
                           onFocus={(e) => (activeInputRef.current = e.target)}
                           onChange={(e) => setFormula(e.target.value)}
                           className="form-control"
                           placeholder="Pro ověření splnitelnosti zadej množinu klauzulí, např.:(p∨q∨r)∧(¬p∨s∨t)∧(¬s∨y)∧(¬p∨x)∧(¬q∨w)∧(¬q∨¬w)"
                           required
                    />
                </div>
                <div className="input-group mb-3">
                    <span className="input-group-text" id="basic-addon1">Závěr</span>
                    <input id="conclusion" type="text"
                           value={conclusion}
                           onFocus={(e) => (activeInputRef.current = e.target)}
                           onChange={(e) => setConclusion(e.target.value)} className="form-control"
                           placeholder="Pro ověření, zda z množiny vyplývá závěr, zadej ho zde"
                           aria-describedby="basic-addon2"/>
                </div>

                <div className="mb-3" style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button type="submit" className="btn btn-success d-flex">Vyřešit</button>
                    <History onSelect={handleSelectHistory} />
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

            {error && <p className="error" style={{ color: "red" }}>{error}</p>}

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
