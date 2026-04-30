import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Register() {
  const [data, setData] = useState({
    name: "",
    age: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      if (!data.name || !data.age || !data.email || !data.password) {
        setError("All fields are required");
        return;
      }

      const res = await axios.post(
        "http://127.0.0.1:5000/auth/register",
        data
      );

      alert(res.data.msg || "Registered successfully");
      navigate("/");

    } catch (err) {
      setError(err.response?.data?.error || "Registration failed");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        
        <h1 style={styles.title}>🦷 Dental AI</h1>
        <p style={styles.subtitle}>Create your account</p>

        <input
          style={styles.input}
          placeholder="Full Name"
          onChange={(e) =>
            setData({ ...data, name: e.target.value })
          }
        />

        <input
          style={styles.input}
          type="number"
          placeholder="Age"
          onChange={(e) =>
            setData({ ...data, age: e.target.value })
          }
        />

        <input
          style={styles.input}
          placeholder="Email"
          onChange={(e) =>
            setData({ ...data, email: e.target.value })
          }
        />

        <input
          style={styles.input}
          type="password"
          placeholder="Password"
          onChange={(e) =>
            setData({ ...data, password: e.target.value })
          }
        />

        {error && <p style={styles.error}>{error}</p>}

        <button style={styles.button} onClick={handleRegister}>
          Register
        </button>

        <p style={styles.text}>Already have an account?</p>

        <button
          style={styles.linkBtn}
          onClick={() => navigate("/")}
        >
          Login
        </button>

      </div>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #e3f2fd, #fce4ec)",
  },

  card: {
    padding: "40px",
    borderRadius: "16px",
    width: "340px",
    textAlign: "center",
    backdropFilter: "blur(10px)",
    background: "rgba(255, 255, 255, 0.85)",
    boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
  },

  title: {
    marginBottom: "5px",
    fontSize: "26px",
  },

  subtitle: {
    fontSize: "14px",
    color: "#555",
    marginBottom: "20px",
  },

  input: {
    width: "100%",
    padding: "12px",
    margin: "10px 0",
    borderRadius: "8px",
    border: "1px solid #ccc",
    outline: "none",
    transition: "0.3s",
  },

  button: {
    width: "100%",
    padding: "12px",
    marginTop: "10px",
    background: "#1976d2",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "bold",
  },

  text: {
    marginTop: "15px",
    fontSize: "14px",
  },

  linkBtn: {
    marginTop: "5px",
    background: "none",
    border: "none",
    color: "#1976d2",
    cursor: "pointer",
    fontWeight: "bold",
  },

  error: {
    color: "#d32f2f",
    fontSize: "13px",
    marginTop: "5px",
  },
};

export default Register;