import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "./Api";
import AuthForm from "./AuthForm";

function Register() {
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async ({ username, password }) => {
    try {
      await registerUser(username, password);
      setError("");
      navigate("/login", { state: { message: "Registrace byla úspěšná! Nyní se můžete přihlásit." } });
    } catch (err) {
      setError( "Registrace selhala, zkuste to prosím znovu." || err.response?.data?.error);
    }
  };

  return (
    <AuthForm type="register" onSubmit={handleRegister} error={error}/>
  );
}

export default Register;
