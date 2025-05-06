import {Link, useLocation} from "react-router-dom";


const Navbar = ({ token, handleLogout }) => {
  const { pathname } = useLocation();

  return (
    <nav className="navbar bg-body-tertiary sticky-top">
      <div className="container-fluid">
          <h4 className="text-success fw-bold">Kalkulátor logických formulí</h4>
        {!token ? (
          pathname === "/login" ? (
            <Link to="/register" className="btn btn-outline-success me-2">Registrace</Link>
          ) : pathname === "/register" ? (
            <Link to="/login" className="btn btn-outline-success me-2">Přihlášení</Link>
          ) : null
        ) : (
          <>
            <button className="btn btn-outline-danger" onClick={handleLogout}>
              Odhlásit
            </button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;