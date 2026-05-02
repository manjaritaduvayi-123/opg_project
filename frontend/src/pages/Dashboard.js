import { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState([]);
  const [history, setHistory] = useState([]);
  const [shareEmail, setShareEmail] = useState("");
  const [pdf, setPdf] = useState("");
  const [loading, setLoading] = useState(false); // 🔥 NEW

  const email = localStorage.getItem("email");

  useEffect(() => {
    if (!email) return;

    axios
      .get(`http://127.0.0.1:5000/history/${email}`)
      .then((res) => setHistory(res.data))
      .catch(() => console.log("No history"));
  }, [email]);

  // 🔥 UPLOAD WITH LOADER
  const handleUpload = async () => {
    if (!file) return alert("Select file first");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("email", email);

    try {
      setLoading(true); // 🔥 START

      const res = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData
      );

      setPreview(res.data.image);
      setResult(res.data.predictions || []);
      setPdf(res.data.pdf);

    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false); // 🔥 STOP
    }
  };

  // 📧 SHARE
  const handleShare = async () => {
    if (!preview) return alert("No image to share");
    if (!shareEmail) return alert("Enter email first");

    try {
      const res = await fetch("http://localhost:5000/share", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: shareEmail,
          file: preview.replace("det_", "")
        })
      });

      const data = await res.json();

      if (!res.ok) return alert(data.error);

      alert("✅ Report shared successfully");
    } catch (err) {
      console.error(err);
      alert("Network error");
    }
  };

  const styles = {
    container: {
      padding: "30px",
      background: "#f8fafc",
      minHeight: "100vh",
      fontFamily: "Segoe UI, sans-serif",
    },
    title: { marginBottom: "20px", fontWeight: "600" },
    card: {
      background: "white",
      padding: "20px",
      borderRadius: "12px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
      marginBottom: "20px",
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "20px",
    },
    image: { width: "100%", borderRadius: "10px" },
    placeholder: { color: "#6b7280" },

    loaderContainer: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "200px",
    },

    spinner: {
      width: "40px",
      height: "40px",
      border: "4px solid #e5e7eb",
      borderTop: "4px solid #2563eb",
      borderRadius: "50%",
      animation: "spin 1s linear infinite",
    },

    resultItem: {
      display: "flex",
      justifyContent: "space-between",
      background: "#f1f5f9",
      padding: "10px",
      borderRadius: "6px",
      marginTop: "8px",
    },
    input: {
      width: "100%",
      padding: "10px",
      marginTop: "10px",
      borderRadius: "6px",
      border: "1px solid #ccc",
    },
    buttonRow: {
      display: "flex",
      gap: "10px",
      marginTop: "10px",
    },
    primaryBtn: {
      marginLeft: "10px",
      background: "#2563eb",
      color: "white",
      padding: "10px 16px",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
    },
    shareBtn: {
      background: "#16a34a",
      color: "white",
      padding: "10px",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
    },
    downloadBtn: {
      background: "#2563eb",
      color: "white",
      padding: "10px",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
    },
    historyItem: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      background: "#f3f4f6",
      padding: "12px",
      borderRadius: "6px",
      marginTop: "10px",
    },
    link: {
      color: "#2563eb",
      textDecoration: "none",
      fontWeight: "bold",
    },
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🦷 Dental AI Dashboard</h1>

      {/* Upload */}
      <div style={styles.card}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button
          style={styles.primaryBtn}
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {/* Main */}
      <div style={styles.grid}>
        <div style={styles.card}>
          {loading ? (
            <div style={styles.loaderContainer}>
              <div style={styles.spinner}></div>
              <p>Analyzing image...</p>
            </div>
          ) : preview ? (
            <img
              src={`http://127.0.0.1:5000/uploads/${preview}`}
              alt="result"
              style={styles.image}
            />
          ) : (
            <p style={styles.placeholder}>Upload an image to analyze</p>
          )}
        </div>

        <div style={styles.card}>
          <h3>Detected Issues</h3>

          {result.length === 0 ? (
            <p style={{ color: "#16a34a" }}>No major issues</p>
          ) : (
            result.map((r, i) => (
              <div key={i} style={styles.resultItem}>
                <span>{r.class}</span>
                <span>{(r.confidence * 100).toFixed(1)}%</span>
              </div>
            ))
          )}

          <input
            type="email"
            placeholder="Enter email"
            value={shareEmail}
            onChange={(e) => setShareEmail(e.target.value)}
            style={styles.input}
          />

          <div style={styles.buttonRow}>
            <button style={styles.shareBtn} onClick={handleShare}>
              Share Report
            </button>

            <a href={`http://127.0.0.1:5000/uploads/${pdf}`} download>
              <button style={styles.downloadBtn}>Download</button>
            </a>
          </div>
        </div>
      </div>

      {/* History */}
      <div style={styles.card}>
        <h2>Previous Reports</h2>

        {history.map((h, i) => (
          <div key={i} style={styles.historyItem}>
            <div>
              <b>Report {i + 1}</b>
              <p style={{ color: "#ef4444" }}>{h.top_defect}</p>
            </div>

            <a
              href={`http://127.0.0.1:5000/uploads/det_${h.file}`}
              target="_blank"
              rel="noreferrer"
              style={styles.link}
            >
              View
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;