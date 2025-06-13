import React from "react";

const History = ({ formulas, onSelect }) => {
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
                                style={{ cursor: "pointer" }}
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
