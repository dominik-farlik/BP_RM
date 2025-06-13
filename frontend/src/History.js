import React, { useState, useEffect } from 'react';
import { getUserHistory } from "./Api";

const History = ({ onSelect }) => {
    const [formulas, setFormulas] = useState([]);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await getUserHistory();
                console.log("API response:", response);
                setFormulas(response.data.formulas || []);
            } catch (error) {
                console.error("Chyba při načítání historie:", error);
            }
        };
        fetchHistory();
    }, []);

  return (
    <div>
      <div className="dropdown">
        <button
          type="button"
          className="btn btn-secondary dropdown-toggle"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          data-bs-auto-close="outside"
        >
          Historie
        </button>
        <form className="dropdown-menu p-1 custom-dropdown-menu">
          <ul className="list-group list-group-flush">
            {formulas.map((formula, index) => (
              <div
                key={index}
                className="list-group-item custom-dropdown-item"
                onClick={() => onSelect(formula.premise, formula.conclusion)}
                style={{ cursor: 'pointer' }}
              >
                {formula.premise} {formula.conclusion}
              </div>
            ))}
          </ul>
        </form>
      </div>
    </div>
  );
};

export default History;
