import React, {useState} from "react";
import {useNavigate} from "react-router-dom";
import {useLocation} from "react-router-dom";
import {loginUser} from "./Api";
import AuthForm from "./AuthForm";

function Login({setToken}) {
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogin = async ({username, password}) => {
        try {
            const response = await loginUser(username, password);
            const token = response.data.access_token;
            setToken(token);
            localStorage.setItem("token", token);
            navigate("/solve");
        } catch (err) {
            setError("Přihlášení se nezdařilo, zkuste to prosím znovu." || err.response?.data?.error);
        }
    };

    return (
        <div>
            <AuthForm
                type="login"
                onSubmit={handleLogin}
                error={error}
                message={location.state?.message}
            />

        </div>
    );
}

export default Login;
