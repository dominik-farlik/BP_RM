import { useState } from "react";

const AuthForm = ({ type, onSubmit, error, message }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ username, password });
  };

  return (
    <div className="container-sm shadow p-3 mb-5 bg-body-tertiary rounded" style={{ width: "40%", marginTop: "2%" }}>
      <h2 className="text-center">{type === "login" ? "Přihlášení" : "Registrace"}</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Login</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="form-control"
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Heslo</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="form-control"
            required
          />
        </div>
        {error && <div className="text-danger mb-3">{error}</div>}
        {message && <div className="text-primary mb-3">{message}</div>}
        <button type="submit" className="btn btn-success d-block mx-auto w-100">
          {type === "login" ? "Přihlásit" : "Registrovat"}
        </button>
      </form>
    </div>
  );
};

export default AuthForm;
