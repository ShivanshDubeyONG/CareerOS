import { useState } from "react";
import {
  ArrowRight,
  Check,
  FileText,
  Sparkles,
  Upload,
  LoaderCircle,
  AlertCircle,
} from "lucide-react";

const API_URL = "http://localhost:8000";

const sources = [
  { name: "Resume", icon: FileText },
  { name: "LinkedIn", icon: LinkedinIcon },
  { name: "GitHub", icon: GithubIcon },
  { name: "LeetCode", icon: CodeIcon },
];

function LinkedinIcon(props) {
  return (
    <span className="code-icon" {...props}>
      in
    </span>
  );
}

function GithubIcon(props) {
  return (
    <span className="code-icon" {...props}>
      GH
    </span>
  );
}

function CodeIcon(props) {
  return (
    <span className="code-icon" {...props}>
      LC
    </span>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    setError(null);
    setAnalysis(null);

    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (!validTypes.includes(selectedFile.type)) {
      setError("Please upload a PDF or DOCX resume.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("Resume must be smaller than 10MB.");
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    handleFile(event.dataTransfer.files?.[0]);
  };

  const handleInput = (event) => {
    handleFile(event.target.files?.[0]);
  };

  const analyzeCareer = async () => {
    if (!file || loading) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/career/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        let message = `Career analysis failed (${response.status})`;

        try {
          const errorData = await response.json();

          if (errorData?.detail) {
            message =
              typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
          }
        } catch {
          // Keep fallback message.
        }

        throw new Error(message);
      }

      const data = await response.json();

      console.log("CAREEROS ANALYSIS:", data);

      setAnalysis(data);
    } catch (err) {
      console.error("CAREEROS API ERROR:", err);

      setError(
        err.message ||
          "Something went wrong while analyzing your resume."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="brand">
          <div className="brand-mark">
            <Sparkles size={15} />
          </div>

          <span>CareerOS</span>
        </div>

        <div className="nav-status">
          <span className="status-dot" />
          Career intelligence
        </div>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="eyebrow">
          <span />
          YOUR PROFESSIONAL FOOTPRINT
          <span />
        </div>

        <h1>
          Understand your
          <br />
          <em>career. Completely.</em>
        </h1>

        <p className="hero-copy">
          Upload your resume once. CareerOS discovers your
          professional footprint and builds an evidence-backed
          career profile across your sources.
        </p>

        {/* UPLOAD */}
        <div className="upload-wrapper">
          {!file ? (
            <label
              className="upload-card"
              onDragOver={(event) => event.preventDefault()}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleInput}
                hidden
              />

              <div className="upload-symbol">
                <Upload size={21} />
              </div>

              <div>
                <h2>Drop your resume here</h2>
                <p>PDF or DOCX · Maximum 10MB</p>
              </div>

              <div className="upload-corner">
                <ArrowRight size={16} />
              </div>
            </label>
          ) : (
            <div className="selected-card">
              <div className="selected-info">
                <div className="file-symbol">
                  <FileText size={20} />
                </div>

                <div className="file-details">
                  <strong>{file.name}</strong>

                  <span>
                    {(file.size / 1024 / 1024).toFixed(2)} MB · Ready
                  </span>
                </div>
              </div>

              <button
                className="analyze-button"
                onClick={analyzeCareer}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoaderCircle
                      size={15}
                      className="spin"
                    />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Analyze career
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* ERROR */}
        {error && (
          <div className="error-message">
            <AlertCircle size={14} />
            {error}
          </div>
        )}

        {/* SOURCES */}
        <div className="source-row">
          {sources.map(({ name, icon: Icon }) => (
            <div
              className="source-pill"
              key={name}
            >
              <span className="source-indicator" />
              <Icon size={14} />
              {name}
            </div>
          ))}
        </div>

        {/* TRUST */}
        <div className="trust-row">
          <span>
            <Check size={13} />
            Resume-first
          </span>

          <span>
            <Check size={13} />
            Evidence-backed
          </span>

          <span>
            <Check size={13} />
            Cross-source analysis
          </span>
        </div>

        {/* TEMPORARY DEBUG OUTPUT */}
        {analysis && (
          <div
            style={{
              marginTop: "40px",
              textAlign: "left",
              padding: "20px",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: "12px",
              maxHeight: "500px",
              overflow: "auto",
            }}
          >
            <div
              style={{
                color: "#43e6aa",
                fontSize: "11px",
                marginBottom: "12px",
                fontWeight: 600,
              }}
            >
              CAREEROS API RESPONSE
            </div>

            <pre
              style={{
                margin: 0,
                color: "#9ba3ae",
                fontSize: "10px",
                lineHeight: 1.6,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </div>
        )}
      </section>

      {/* FOOTER */}
      <footer>
        <span>CAREEROS</span>

        <span>
          Build a career profile, not just a resume.
        </span>
      </footer>
    </main>
  );
}

export default App;