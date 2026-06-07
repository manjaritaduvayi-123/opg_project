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

      if (email) {
        const historyRes = await axios.get(`http://127.0.0.1:5000/history/${email}`);
        setHistory(historyRes.data);
      }

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
      alert(err.response?.data?.error || "Email sending failed");
    } finally {
      setSharing(false);
    }
  };

  // 🔥 STYLES (SIZES DECREASED HERE)
  const styles = {
    container: {
      padding: "15px 30px", // Decreased vertical padding
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
      marginBottom: "12px", // Tighter margins
    },
    title: {
      fontSize: "22px", // Smaller header font
      margin: 0
    },
    card: {
      background: darkMode ? "#1e293b" : "white",
      padding: "12px 18px", // Reduced padding
      borderRadius: "12px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      marginBottom: "12px"
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "1.2fr 0.8fr", // Optimized proportional split
      gap: "15px"
    },
    imageContainer: {
      display: "flex",
      gap: "10px",
      marginTop: "8px"
    },
    imageWrapper: {
      flex: 1,
      textAlign: "center"
    },
    image: {
      width: "100%",
      maxHeight: "320px", // Restricted height to prevent massive layout scaling
      objectFit: "contain", // Keeps structural aspect ratio intact
      borderRadius: "8px",
      border: "1px solid #ccc",
      background: "#000"
    },
    subHeading: {
      fontSize: "16px", // Compact subsection sizing
      margin: "0 0 5px 0",
    },
    input: {
      width: "100%",
      padding: "8px 12px", // Smaller input fields
      borderRadius: "6px",
      border: "1px solid #ccc",
      marginTop: "10px",
      fontSize: "13px",
      boxSizing: "border-box"
    },
    buttonRow: {
      display: "flex",
      gap: "8px",
      marginTop: "10px"
    },
    btn: {
      padding: "8px 14px", // Tighter downsized buttons
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
      color: "white",
      fontWeight: "bold",
      fontSize: "13px"
    },
    primary: { background: "#2563eb" },
    green: { background: "#16a34a" },
    
    historyItem: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      background: darkMode ? "#334155" : "#f1f5f9",
      padding: "8px 15px", // Shorter list records
      borderRadius: "8px",
      marginTop: "8px"
    },
    historyText: {
      margin: 0,
      fontSize: "14px"
    },
    link: {
      border: "none",
      background: "none",
      cursor: "pointer",
      fontWeight: "bold",
      fontSize: "13px" // Smaller action labels
    },
    resultCard: {
      padding: "8px 12px", // Scaled down issue items
      borderRadius: "8px",
      marginBottom: "8px",
      background: darkMode ? "#334155" : "#f8fafc",
      fontSize: "13px"
    },
    resultTitle: {
      fontSize: "14px",
      margin: "0 0 4px 0"
    }
  };

  return (
    <div style={styles.container}>
      {/* HEADER */}
      <div style={styles.header}>
        <h1 style={styles.title}>🦷 Dental AI Dashboard</h1>
        <button
          onClick={() => setDarkMode(!darkMode)}
          style={{ padding: "6px 12px", borderRadius: "6px", cursor: "pointer", fontSize: "12px" }}
        >
          {darkMode ? "☀️ Light" : "🌙 Dark"}
        </button>
      </div>

      {/* UPLOAD */}
      <div style={styles.card}>
        <input type="file" style={{ fontSize: "13px" }} onChange={(e) => setFile(e.target.files[0])} />
        <button
          onClick={handleUpload}
          disabled={loading}
          style={{ ...styles.btn, ...styles.primary, marginLeft: "10px" }}
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
        {loading && <span style={{ marginLeft: "15px", fontSize: "13px" }}>🔄 Analyzing dental X-ray...</span>}
      </div>

      {/* MAIN CONTENT AREA */}
      <div style={styles.grid}>
        {/* LEFT PANEL: IMAGES side by side to save space */}
        <div style={styles.card}>
          <h2 style={styles.subHeading}>Visual Output Analysis</h2>
          {preview ? (
            <div style={styles.imageContainer}>
              <div style={styles.imageWrapper}>
                <span style={{ fontSize: "11px", fontWeight: "600" }}>Detections</span>
                <img
                  src={`http://127.0.0.1:5000/uploads/${preview}`}
                  alt="Detection"
                  style={styles.image}
                />
              </div>

              {heatmap && (
                <div style={styles.imageWrapper}>
                  <span style={{ fontSize: "11px", fontWeight: "600" }}>Diagnostic Heatmap</span>
                  <img
                    src={`http://127.0.0.1:5000/uploads/${heatmap}`}
                    alt="Heatmap"
                    style={styles.image}
                  />
                </div>
              )}
            </div>
          ) : (
            <p style={{ fontSize: "13px", color: "#666", margin: "10px 0" }}>Upload an X-ray image to initialize panel viewport.</p>
          )}
        </div>

        {/* RIGHT PANEL: METRICS & CONTROLS */}
        <div style={styles.card}>
          <h2 style={styles.subHeading}>Detected Pathology</h2>
          <div style={{ maxHeight: "240px", overflowY: "auto", paddingRight: "4px" }}>
            {result.length === 0 ? (
              <p style={{ fontSize: "13px", color: "#666" }}>No current evaluation metrics loaded.</p>
            ) : (
              result.map((r, i) => (
                <div key={i} style={styles.resultCard}>
                  <h3 style={styles.resultTitle}>{r.class}</h3>
                  <p style={{ margin: "2px 0" }}>Confidence: {(r.confidence * 100).toFixed(1)}%</p>
                  <p style={{ margin: "2px 0", color: "#555" }}>{r.suggestion}</p>
                </div>
              ))
            )}
          </div>

          <input
            type="email"
            placeholder="Enter recipient email string"
            value={shareEmail}
            onChange={(e) => setShareEmail(e.target.value)}
            style={styles.input}
          />

          <div style={styles.buttonRow}>
            <button onClick={handleShare} disabled={sharing} style={{ ...styles.btn, ...styles.green }}>
              {sharing ? "Sharing..." : "Share"}
            </button>

            {pdf && (
              <a href={`http://127.0.0.1:5000/uploads/${pdf}`} target="_blank" rel="noreferrer">
                <button style={{ ...styles.btn, ...styles.primary }}>Download PDF</button>
              </a>
            )}
          </div>
        </div>
      </div>

      {/* HISTORY PANEL */}
      <div style={styles.card}>
        <h2 style={{ ...styles.subHeading, marginBottom: "5px" }}>Previous Records</h2>
        <div style={{ maxHeight: "180px", overflowY: "auto" }}>
          {history.length === 0 ? (
            <p style={{ fontSize: "13px", color: "#666" }}>No historical evaluations mapped to this user key.</p>
          ) : (
            history.map((h, i) => (
              <div key={i} style={styles.historyItem}>
                <div>
                  <h3 style={{ fontSize: "13px", margin: 0 }}>Report Index #{i + 1}</h3>
                  <p style={{ color: "#ef4444", margin: 0, fontSize: "12px" }}>{h.top_defect || "No issues detected"}</p>
                </div>

                <div style={{ display: "flex", gap: "15px" }}>
                  <button
                    style={{ ...styles.link, color: "#16a34a" }}
                    onClick={() => {
                      if (!h.file) return alert("No reference image pointer mapped.");
                      let rawStr = h.file.replace(/\\/g, "/").replace("uploads/", "");
                      const imgMatch = rawStr.match(/^.*?\.(jpg|jpeg|png|webp)/i);
                      let cleanImageName = imgMatch ? imgMatch[0] : rawStr;
                      window.open(`http://127.0.0.1:5000/uploads/det_${cleanImageName}`, "_blank");
                    }}
                  >
                    🖼️ View Image
                  </button>

                  <button
                    style={{ ...styles.link, color: "#2563eb" }}
                    onClick={() => {
                      if (!h.file) return alert("No relational target reference available.");
                      let rawStr = h.file.replace(/\\/g, "/").replace("uploads/", "");
                      let pdfUrl = "";
                      if (rawStr.endsWith("_report.pdf")) {
                        pdfUrl = `http://127.0.0.1:5000/uploads/${rawStr}`;
                      } else {
                        const baseMatch = rawStr.match(/^(.*?)\.[^.]+$/);
                        const baseName = baseMatch ? baseMatch[1] : rawStr;
                        pdfUrl = `http://127.0.0.1:5000/uploads/${baseName}_report.pdf`;
                      }
                      window.open(pdfUrl, "_blank");
                    }}
                  >
                    📄 View PDF
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;