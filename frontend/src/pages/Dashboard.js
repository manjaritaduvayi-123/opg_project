import axios from "axios";
import { useEffect, useState } from "react";

function Dashboard() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState([]);
  const [history, setHistory] = useState([]);
  const [shareEmail, setShareEmail] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);

  const [detectedImage, setDetectedImage] = useState(null);
  const [pdf, setPdf] = useState(null);
  const [topDefect, setTopDefect] = useState("");
  const [loading, setLoading] = useState(false);

  const email = localStorage.getItem("email");

  // 🎯 Helpers
  const getColor = (conf) => {
    if (conf > 0.8) return "#2e7d32";
    if (conf > 0.5) return "#ed6c02";
    return "#d32f2f";
  };

  const getSeverity = (conf) => {
    if (conf > 0.8) return "High";
    if (conf > 0.5) return "Medium";
    return "Low";
  };

  // 🔍 Upload & Analyze
  const handleUpload = async () => {
    if (!file) return alert("Select a file first");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("email", email);

    try {
      setLoading(true);

      const res = await axios.post("http://127.0.0.1:5000/upload", formData);

      setResult(res.data.predictions || []);

      const img = `http://127.0.0.1:5000/uploads/det_${res.data.file}`;
      setDetectedImage(img);

      setPdf(`http://127.0.0.1:5000/uploads/${res.data.pdf}`);
      setTopDefect(res.data.top_defect);

      setLoading(false);
      loadHistory();
    } catch (err) {
      console.error(err);
      setLoading(false);
      alert("Upload failed ❌");
    }
  };

  // 📧 Share Report (🔥 FINAL FIX)
  const handleShare = async () => {
    if (!shareEmail) return alert("Enter email");
    if (!detectedImage) return alert("Analyze first");

    try {
      // 🔥 Convert URL → local backend path
      const imagePath = detectedImage.replace(
        "http://127.0.0.1:5000/",
        ""
      );

      console.log("Sending path:", imagePath);

      const res = await axios.post("http://127.0.0.1:5000/share", {
        email: shareEmail,
        image_path: imagePath,
      });

      console.log(res.data);

      alert("Report sent successfully ✅");
    } catch (error) {
      console.error(error);
      alert("Failed ❌");
    }
  };

  // 📜 History
  const loadHistory = async () => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:5000/history/${email}`
      );
      setHistory(res.data.reverse());
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const logout = () => {
    localStorage.removeItem("email");
    window.location = "/";
  };

  return (
    <div style={styles.container}>
      <h1>🦷 Dental AI Dashboard</h1>

      {/* Upload */}
      <div style={styles.card}>
        <h3>Upload X-ray</h3>

        <input
          type="file"
          onChange={(e) => {
            const selected = e.target.files[0];
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult([]);
            setDetectedImage(null);
          }}
        />

        {preview && <img src={preview} style={styles.image} />}

        <button style={styles.primaryBtn} onClick={handleUpload}>
          Analyze
        </button>

        {loading && <p>Processing...</p>}

        <input
          type="email"
          placeholder="Enter email"
          value={shareEmail}
          onChange={(e) => setShareEmail(e.target.value)}
          style={styles.input}
        />

        <button style={styles.secondaryBtn} onClick={handleShare}>
          Share Report
        </button>
      </div>

      {/* Detection */}
      {detectedImage && (
        <div style={styles.card}>
          <h3>Detection Result</h3>
          <img
            src={detectedImage}
            style={styles.image}
            onClick={() => setSelectedImage(detectedImage)}
          />
        </div>
      )}

      {/* Diagnosis */}
      {topDefect && (
        <div style={styles.summary}>
          <h3>Diagnosis</h3>
          <p><b>{topDefect}</b></p>
        </div>
      )}

      {/* Results */}
      <div style={styles.card}>
        <h3>Analysis</h3>

        {result.length === 0 ? (
          <p style={{ color: "green" }}>No major issues</p>
        ) : (
          result.map((r, i) => (
            <div key={i} style={styles.resultBox}>
              <h4>{r.class}</h4>
              <p style={{ color: getColor(r.confidence) }}>
                {(r.confidence * 100).toFixed(1)}%
              </p>
              <p>{getSeverity(r.confidence)}</p>
              <p style={{ color: "#2e7d32" }}>{r.suggestion}</p>
            </div>
          ))
        )}
      </div>

      {/* PDF */}
      {pdf && (
        <div style={styles.card}>
          <a href={pdf} target="_blank" rel="noreferrer">
            Download Report
          </a>
        </div>
      )}

      {/* History */}
      <div style={styles.card}>
        <h3>Previous Reports</h3>

        {history.length === 0 ? (
          <p>No history</p>
        ) : (
          history.map((h, i) => (
            <div key={i} style={styles.historyCard}>
              <p><b>Report {i + 1}</b></p>

              <p
                style={styles.link}
                onClick={() =>
                  setSelectedImage(
                    `http://127.0.0.1:5000/uploads/det_${h.file}`
                  )
                }
              >
                View Image
              </p>

              <p style={{ color: "#d32f2f" }}>
                {h.top_defect || "No Detection"}
              </p>
            </div>
          ))
        )}
      </div>

      {/* Modal */}
      {selectedImage && (
        <div style={styles.modal} onClick={() => setSelectedImage(null)}>
          <img src={selectedImage} style={styles.modalImg} />
        </div>
      )}

      <button style={styles.logout} onClick={logout}>
        Logout
      </button>
    </div>
  );
}

const styles = {
  container: {
    textAlign: "center",
    background: "#f4f6f8",
    minHeight: "100vh",
    padding: "20px",
  },
  card: {
    background: "#fff",
    padding: "20px",
    margin: "20px auto",
    maxWidth: "550px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  },
  image: {
    width: "100%",
    borderRadius: "10px",
    marginTop: "10px",
    cursor: "pointer",
  },
  modal: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: "rgba(0,0,0,0.8)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  modalImg: {
    maxWidth: "90%",
    maxHeight: "90%",
  },
  primaryBtn: {
    marginTop: "10px",
    padding: "10px",
    background: "#1976d2",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    width: "100%",
  },
  secondaryBtn: {
    marginTop: "10px",
    padding: "10px",
    background: "#4caf50",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    width: "100%",
  },
  input: {
    marginTop: "10px",
    padding: "8px",
    width: "100%",
    borderRadius: "6px",
    border: "1px solid #ccc",
  },
  summary: {
    background: "#fff3e0",
    padding: "15px",
    margin: "20px auto",
    maxWidth: "550px",
    borderRadius: "10px",
  },
  resultBox: {
    border: "1px solid #eee",
    padding: "10px",
    marginTop: "10px",
    borderRadius: "8px",
    textAlign: "left",
  },
  historyCard: {
    border: "1px solid #eee",
    padding: "10px",
    marginTop: "10px",
    borderRadius: "8px",
    textAlign: "left",
  },
  link: {
    color: "#1976d2",
    cursor: "pointer",
  },
  logout: {
    marginTop: "20px",
    background: "#d32f2f",
    color: "#fff",
    padding: "10px",
    border: "none",
    borderRadius: "6px",
  },
};

export default Dashboard;