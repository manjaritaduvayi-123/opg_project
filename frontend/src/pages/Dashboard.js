import { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {

  const [file, setFile] = useState(null);

  const [preview, setPreview] = useState(null);

  const [heatmap, setHeatmap] = useState(null);

  const [result, setResult] = useState([]);

  const [history, setHistory] = useState([]);

  const [shareEmail, setShareEmail] = useState("");

  const [pdf, setPdf] = useState("");

  const [loading, setLoading] = useState(false);

  const [sharing, setSharing] = useState(false);

  const [darkMode, setDarkMode] = useState(false);

  const email = localStorage.getItem("email");

  // 🔥 LOAD HISTORY
  useEffect(() => {

    if (!email) return;

    axios
      .get(`http://127.0.0.1:5000/history/${email}`)
      .then((res) => {

        setHistory(res.data);

      })
      .catch(() => {

        console.log("No history");

      });

  }, [email]);

  // 🔥 UPLOAD
  const handleUpload = async () => {

    if (!file) {

      alert("Select image first");

      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    formData.append("email", email);

    try {

      setLoading(true);

      const res = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData
      );

      setPreview(res.data.image);

      setHeatmap(res.data.heatmap);

      setResult(res.data.predictions || []);

      setPdf(res.data.pdf);

    } catch (err) {

      console.error(err);

      alert("Upload failed");

    } finally {

      setLoading(false);
    }
  };

  // 🔥 SHARE REPORT
  const handleShare = async () => {

  if (!shareEmail) {
    alert("Enter email");
    return;
  }

  if (!preview) {
    alert("No report available");
    return;
  }

  try {

    setSharing(true);

    const response = await axios.post(
      "http://127.0.0.1:5000/share",
      {
        email: shareEmail,
        file: preview.replace("det_", "")
      }
    );

    alert(response.data.msg);

  } catch (err) {

    console.error(err);

    alert(
      err.response?.data?.error ||
      "Email sending failed"
    );

  } finally {

    setSharing(false);

  }
};

  // 🔥 STYLES
  const styles = {

    container: {
      padding: "30px",
      minHeight: "100vh",
      fontFamily: "Segoe UI, sans-serif",
      background: darkMode
        ? "linear-gradient(135deg,#0f172a,#111827,#1e293b)"
        : "linear-gradient(135deg,#dbeafe,#eff6ff,#f8fafc)",
      color: darkMode ? "white" : "black"
    },

    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: "20px"
    },

    card: {
      background: darkMode ? "#1e293b" : "white",
      padding: "20px",
      borderRadius: "16px",
      boxShadow: "0 6px 18px rgba(0,0,0,0.1)",
      marginBottom: "20px"
    },

    grid: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "20px"
    },

    image: {
      width: "100%",
      borderRadius: "12px",
      marginTop: "10px"
    },

    input: {
      width: "100%",
      padding: "12px",
      borderRadius: "8px",
      border: "1px solid #ccc",
      marginTop: "15px"
    },

    buttonRow: {
      display: "flex",
      gap: "10px",
      marginTop: "15px"
    },

    btn: {
      padding: "10px 18px",
      border: "none",
      borderRadius: "8px",
      cursor: "pointer",
      color: "white",
      fontWeight: "bold"
    },

    primary: {
      background: "#2563eb"
    },

    green: {
      background: "#16a34a"
    },

    historyItem: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      background: darkMode ? "#334155" : "#f1f5f9",
      padding: "15px",
      borderRadius: "10px",
      marginTop: "12px"
    },

    link: {
      border: "none",
      background: "none",
      color: "#2563eb",
      cursor: "pointer",
      fontWeight: "bold",
      fontSize: "16px"
    },

    resultCard: {
      padding: "12px",
      borderRadius: "10px",
      marginBottom: "15px",
      background: darkMode ? "#334155" : "#f8fafc"
    }
  };

  return (

    <div style={styles.container}>

      {/* HEADER */}
      <div style={styles.header}>

        <h1>🦷 Dental AI Dashboard</h1>

        <button
          onClick={() => setDarkMode(!darkMode)}
          style={{
            padding: "10px",
            borderRadius: "8px",
            cursor: "pointer"
          }}
        >
          {darkMode ? "☀️ Light" : "🌙 Dark"}
        </button>

      </div>

      {/* UPLOAD */}
      <div style={styles.card}>

        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button
          onClick={handleUpload}
          disabled={loading}
          style={{
            ...styles.btn,
            ...styles.primary,
            marginLeft: "10px"
          }}
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {loading && (
          <p style={{ marginTop: "10px" }}>
            🔄 Analyzing dental X-ray...
          </p>
        )}

      </div>

      {/* MAIN */}
      <div style={styles.grid}>

        {/* LEFT */}
        <div style={styles.card}>

          {preview ? (
            <>

              <h2>Detection Result</h2>

              <img
                src={`http://127.0.0.1:5000/uploads/${preview}`}
                alt="Detection"
                style={styles.image}
              />

              {heatmap && (
                <>
                  <h2 style={{ marginTop: "25px" }}>
                    Diagnostic Heatmap Analysis
                  </h2>

                  <img
                    src={`http://127.0.0.1:5000/uploads/${heatmap}`}
                    alt="Heatmap"
                    style={styles.image}
                  />
                </>
              )}

            </>
          ) : (

            <p>Upload an X-ray image</p>

          )}

        </div>

        {/* RIGHT */}
        <div style={styles.card}>

          <h2>Detected Issues</h2>

          {result.length === 0 ? (

            <p>No predictions yet</p>

          ) : (

            result.map((r, i) => (

              <div
                key={i}
                style={styles.resultCard}
              >

                <h3>{r.class}</h3>

                <p>
                  Confidence:
                  {" "}
                  {(r.confidence * 100).toFixed(1)}%
                </p>

                <p>{r.suggestion}</p>

              </div>
            ))
          )}

          {/* EMAIL */}
          <input
            type="email"
            placeholder="Enter email"
            value={shareEmail}
            onChange={(e) => setShareEmail(e.target.value)}
            style={styles.input}
          />

          {/* BUTTONS */}
          <div style={styles.buttonRow}>

            <button
              onClick={handleShare}
              disabled={sharing}
              style={{
                ...styles.btn,
                ...styles.green
              }}
            >
              {sharing ? "Sharing..." : "Share"}
            </button>

            {pdf && (

              <a
                href={`http://127.0.0.1:5000/uploads/${pdf}`}
                download
              >
                <button
                  style={{
                    ...styles.btn,
                    ...styles.primary
                  }}
                >
                  Download PDF
                </button>
              </a>

            )}

          </div>

        </div>

      </div>

      {/* HISTORY */}
      <div style={styles.card}>

        <h2>Previous Reports</h2>

        {history.length === 0 ? (

          <p>No reports found</p>

        ) : (

          history.map((h, i) => (

            <div
              key={i}
              style={styles.historyItem}
            >

              <div>

                <h3>Report {i + 1}</h3>

                <p style={{ color: "#ef4444" }}>
                  {h.top_defect}
                </p>

              </div>

              <button
                style={styles.link}
                onClick={() => {

                  if (!h.file) {

                    alert("No file found");

                    return;
                  }

                  const url =
                    `http://127.0.0.1:5000/uploads/det_${h.file}`;

                  window.open(url, "_blank");
                }}
              >
                View
              </button>

            </div>
          ))
        )}

      </div>

    </div>
  );
}

export default Dashboard;