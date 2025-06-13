import axios from "axios";

const API_URL = "http://127.0.0.1:5000/api";

// Register a new user
export const registerUser = async (username, password) => {
  return axios.post(`${API_URL}/register`, { username, password });
};

// Log in a user and get a JWT token
export const loginUser = async (username, password) => {
  return axios.post(`${API_URL}/login`, { username, password });
};

// Solve the formula (requires JWT token)
export const solveFormula = async (formula, conclusion) => {
  const access_token = localStorage.getItem('token').toString()
  return axios.post(
  `${API_URL}/solve`,
  { formula, conclusion },
  { headers: { Authorization: `Bearer ${access_token}` }});
};

export const getUserHistory = async () => {
  const access_token = localStorage.getItem('token').toString()
  return axios.post(
  `${API_URL}/history`,
      {},
  { headers: { Authorization: `Bearer ${access_token}` }});
};