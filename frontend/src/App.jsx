import { useEffect, useMemo, useState } from "react";
import { supabase } from "./supabase";
import {
  ArrowRight,
  Check,
  FileText,
  Sparkles,
  Upload,
  LoaderCircle,
  AlertCircle,
  Code2,
  ShieldCheck,
  Activity,
  Target,
  Zap,
  ChevronRight,
  ExternalLink,
  Brain,
  Layers3,
  CircleAlert,
} from "lucide-react";

function GithubIcon(props) {
  return (
    <span className="brand-text-icon" {...props}>
      GH
    </span>
  );
}

function LinkedinIcon(props) {
  return (
    <span className="brand-text-icon" {...props}>
      in
    </span>
  );
}

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

const sources = [
  { name: "Resume", key: "resume", icon: FileText },
  { name: "LinkedIn", key: "linkedin", icon: LinkedinIcon },
  { name: "GitHub", key: "github", icon: GithubIcon },
  { name: "LeetCode", key: "leetcode", icon: Code2 },
];

const clamp = (value, min = 0, max = 100) =>
  Math.min(max, Math.max(min, Number(value) || 0));

const titleCase = (value = "") =>
  String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

function scoreColor(score) {
  if (score >= 80) return "excellent";
  if (score >= 60) return "good";
  if (score >= 40) return "watch";
  return "weak";
}

function ScoreRing({ score, label = "READINESS", large = false }) {
  const value = clamp(score);
  const radius = large ? 66 : 46;
  const circumference = 2 * Math.PI * radius;
  const dash = (value / 100) * circumference;

  return (
    <div className={`score-ring ${large ? "score-ring-large" : ""}`}>
      <svg viewBox="0 0 180 180">
        <circle
          className="ring-track"
          cx="90"
          cy="90"
          r={radius}
        />
        <circle
          className={`ring-value ${scoreColor(value)}`}
          cx="90"
          cy="90"
          r={radius}
          strokeDasharray={`${dash} ${circumference - dash}`}
        />
      </svg>

      <div className="ring-content">
        <strong>{Math.round(value)}</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}

function MetricBar({ label, value, suffix = "" }) {
  const score = clamp(value);

  return (
    <div className="metric-bar">
      <div className="metric-bar-head">
        <span>{label}</span>
        <strong>
          {Math.round(score)}
          {suffix}
        </strong>
      </div>

      <div className="metric-track">
        <div
          className={`metric-fill ${scoreColor(score)}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

function SourceCard({ name, icon: Icon, connected, value }) {
  return (
    <div className={`source-card ${connected ? "connected" : ""}`}>
      <div className="source-icon">
        <Icon size={16} />
      </div>

      <div className="source-card-copy">
        <span>{name}</span>
        <strong>{connected ? value : "Unavailable"}</strong>
      </div>

      <div className={`source-check ${connected ? "on" : ""}`}>
        {connected ? <Check size={12} /> : "—"}
      </div>
    </div>
  );
}

function EvidenceCard({ skill }) {
  const status = skill.status || "unknown";

  const sources = [
    ["resume", skill.resume_claimed],
    ["linkedin", skill.linkedin_claimed],
    ["github", skill.github_demonstrated],
    ["leetcode", skill.leetcode_demonstrated],
  ];

  return (
    <div className="evidence-card">
      <div className="evidence-top">
        <div>
          <span className="micro-label">
            {status === "strongly_supported"
              ? "STRONGLY SUPPORTED"
              : status === "demonstrated"
                ? "DEMONSTRATED"
                : status === "claimed_only"
                  ? "CLAIM ONLY"
                  : "NO SIGNAL"}
          </span>

          <h3>{titleCase(skill.skill)}</h3>
        </div>

        <div
          className={`evidence-status ${status}`}
        >
          {status === "strongly_supported"
            ? "4-source"
            : status === "demonstrated"
              ? "Evidence"
              : status === "claimed_only"
                ? "Claimed"
                : "Unknown"}
        </div>
      </div>

      <div className="evidence-sources">
        {sources.map(([source, present]) => (
          <span
            key={source}
            className={present ? "present" : ""}
          >
            {present ? <Check size={10} /> : "·"}
            {source}
          </span>
        ))}
      </div>
    </div>
  );
}

function Radar({ values }) {
  const points = [
    [100, 16],   // Projects
    [176, 92],   // DSA
    [100, 168],  // Skills
    [24, 92],    // GitHub
  ];

  const center = [100, 92];

  const makePolygon = (scale) =>
    points
      .map(([x, y]) => {
        const nx =
          center[0] +
          (x - center[0]) * scale;

        const ny =
          center[1] +
          (y - center[1]) * scale;

        return `${nx},${ny}`;
      })
      .join(" ");

  const valuePoints = points
    .map(([x, y], index) => {
      const value = clamp(values[index]);
      const scale = value / 100;

      const nx =
        center[0] +
        (x - center[0]) * scale;

      const ny =
        center[1] +
        (y - center[1]) * scale;

      return `${nx},${ny}`;
    })
    .join(" ");

  return (
    <svg
      className="radar"
      viewBox="0 0 200 184"
    >
      {[0.25, 0.5, 0.75, 1].map(
        (scale) => (
          <polygon
            key={scale}
            points={makePolygon(scale)}
            className="radar-grid"
          />
        )
      )}

      {points.map(([x, y], index) => (
        <line
          key={index}
          x1="100"
          y1="92"
          x2={x}
          y2={y}
          className="radar-axis"
        />
      ))}

      <polygon
        points={valuePoints}
        className="radar-value"
      />

      {points.map(([x, y], index) => {
        const value = clamp(values[index]);
        const scale = value / 100;

        return (
          <circle
            key={index}
            cx={
              100 +
              (x - 100) * scale
            }
            cy={
              92 +
              (y - 92) * scale
            }
            r="3"
            className="radar-point"
          />
        );
      })}
    </svg>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);

  const [authMode, setAuthMode] = useState("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    const loadSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      setUser(session?.user ?? null);
      setAuthChecking(false);
    };

    loadSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const handleAuth = async (event) => {
    event.preventDefault();

    setAuthLoading(true);
    setAuthError("");

    try {
      if (authMode === "signup") {
        const { data, error } =
          await supabase.auth.signUp({
            email: authEmail,
            password: authPassword,
          });

        if (error) {
          throw error;
        }

        setUser(data.user);
        return;
      }

      const { data, error } =
        await supabase.auth.signInWithPassword({
          email: authEmail,
          password: authPassword,
        });

      if (error) {
        throw error;
      }

      setUser(data.user);
    } catch (error) {
      console.error("AUTH ERROR:", error);

      setAuthError(
        error.message ||
          "Authentication failed."
      );
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisProgress, setAnalysisProgress] =
    useState(0);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  /*
   * --------------------------------------------------
   * CAREER ANALYSIS PROGRESS
   *
   * This is intentionally a "perceived progress"
   * indicator because the backend currently returns
   * one final response rather than streaming stages.
   *
   * It stops at 99% until the real response arrives.
   * --------------------------------------------------
   */
  useEffect(() => {
    if (!loading) {
      setAnalysisProgress(0);
      return;
    }

    setAnalysisProgress(5);

    const stages = [
      {
        progress: 18,
        delay: 900,
      },
      {
        progress: 31,
        delay: 2200,
      },
      {
        progress: 46,
        delay: 4200,
      },
      {
        progress: 61,
        delay: 7000,
      },
      {
        progress: 74,
        delay: 10500,
      },
      {
        progress: 84,
        delay: 15000,
      },
      {
        progress: 92,
        delay: 22000,
      },
      {
        progress: 97,
        delay: 32000,
      },
      {
        progress: 99,
        delay: 42000,
      },
    ];

    const timers = stages.map(
      ({ progress, delay }) =>
        setTimeout(() => {
          setAnalysisProgress((current) =>
            Math.max(current, progress)
          );
        }, delay)
    );

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [loading]);

  const getProgressMessage = (progress) => {
    if (progress < 25) {
      return "Reading your resume";
    }

    if (progress < 45) {
      return "Mapping your experience";
    }

    if (progress < 65) {
      return "Analyzing skills & projects";
    }

    if (progress < 85) {
      return "Connecting career signals";
    }

    if (progress < 97) {
      return "Cross-checking your profile";
    }

    return "Finalizing career intelligence";
  };

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    setError(null);
    setAnalysis(null);

    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (!validTypes.includes(selectedFile.type)) {
      setError(
        "Please upload a PDF or DOCX resume."
      );
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError(
        "Resume must be smaller than 10MB."
      );
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    handleFile(
      event.dataTransfer.files?.[0]
    );
  };

  const handleInput = (event) => {
    handleFile(
      event.target.files?.[0]
    );
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
          const errorData =
            await response.json();

          if (errorData?.detail) {
            message =
              typeof errorData.detail ===
              "string"
                ? errorData.detail
                : JSON.stringify(
                    errorData.detail
                  );
          }
        } catch {
          // fallback
        }

        throw new Error(message);
      }

      const data =
        await response.json();

      console.log(
        "CAREEROS ANALYSIS:",
        data
      );

      /*
       * The actual backend response has arrived,
       * so NOW we are genuinely at 100%.
       */
      setAnalysisProgress(100);
      setAnalysis(data);
    } catch (err) {
      console.error(
        "CAREEROS API ERROR:",
        err
      );

      setError(
        err.message ||
          "Something went wrong while analyzing your resume."
      );
    } finally {
      setLoading(false);
    }
  };

  const model = analysis?.analysis;

  const resume = model?.resume;
  const github = model?.github;
  const linkedin = model?.linkedin;
  const leetcode = model?.leetcode;
  const unified = model?.unified;

  const resumeRating =
    resume?.rating || {};

  const githubAnalysis =
    github?.analysis || {};

  const githubProfile =
    github?.profile || {};

  const leetcodeAnalysis =
    leetcode?.analysis || {};

  const linkedinAnalysis =
    linkedin?.analysis || {};

  const linkedinRating =
    linkedin?.rating || {};

  const unifiedSkills =
    unified?.skill_evidence || [];

  const projectEvidence =
    unified?.project_evidence || [];

  const findings =
    unified?.findings || [];

  const sourceStatus =
    unified?.source_status || {};

  const topSkills = useMemo(() => {
    const priority = {
      strongly_supported: 0,
      demonstrated: 1,
      claimed_only: 2,
      unknown: 3,
    };

    return [...unifiedSkills]
      .sort(
        (a, b) =>
          (priority[a.status] ?? 4) -
          (priority[b.status] ?? 4)
      )
      .slice(0, 12);
  }, [unifiedSkills]);

  const careerReadiness = useMemo(() => {
  const resumeScore =
    Number(resumeRating.overall_score) || 0;

  const projectScore =
    githubAnalysis.projects?.length
      ? githubAnalysis.projects.reduce(
          (sum, item) =>
            sum +
            clamp(
              item.project_score * 10
            ),
          0
        ) / githubAnalysis.projects.length
      : 0;

  const leetcodeScore =
    Number(
      leetcodeAnalysis.problem_solving_score
    ) || 0;

  /*
   * Professional experience is deliberately treated
   * separately from technical projects.
   *
   * Projects demonstrate technical ability.
   * Experience demonstrates exposure to real-world
   * engineering environments.
   */

  const experienceCount =
    Array.isArray(resumeRating.experience)
      ? resumeRating.experience.length
      : Array.isArray(
          resumeRating.experience?.items
        )
      ? resumeRating.experience.items.length
      : Array.isArray(
          resumeRating.experience?.entries
        )
      ? resumeRating.experience.entries.length
      : 0;

  /*
   * If the parsed resume experience is not directly
   * available in the rating object, fall back to the
   * actual resume profile if available.
   */
  const actualExperience =
    Array.isArray(resume?.experience)
      ? resume.experience.length
      : experienceCount;

  let experienceScore = 0;

  if (actualExperience >= 3) {
    experienceScore = 100;
  } else if (actualExperience === 2) {
    experienceScore = 85;
  } else if (actualExperience === 1) {
    experienceScore = 70;
  }

  /*
   * Readiness measures preparedness for the professional
   * job market, not simply technical ability.
   *
   * Strong student:
   * - can score well technically
   * - but lack of professional experience limits readiness
   *
   * Experienced candidate:
   * - receives additional readiness credit for
   *   demonstrated professional exposure
   */

  const technicalScore =
    resumeScore * 0.30 +
    projectScore * 0.30 +
    leetcodeScore * 0.15;

  const experienceContribution =
    experienceScore * 0.15;

  /*
   * Small ceiling for candidates with no professional
   * experience. This prevents a technically strong student
   * from being represented as equally job-ready as someone
   * with substantial real-world experience.
   */
  let readiness =
    technicalScore +
    experienceContribution;

  if (actualExperience === 0) {
    readiness = Math.min(
      readiness,
      68
    );
  }

  return Math.round(
    clamp(readiness)
  );
}, [
  resumeRating,
  resume,
  githubAnalysis,
  leetcodeAnalysis,
]);
  const radarValues = [
  resumeRating.projects?.score ?? 70,

  leetcodeAnalysis.problem_solving_score ??
    0,

  resumeRating.skills?.score ?? 70,

  githubAnalysis.projects?.length
    ? githubAnalysis.projects.reduce(
        (sum, project) =>
          sum +
          clamp(
            project.project_score * 10
          ),
        0
      ) /
      githubAnalysis.projects.length
    : 0,
];

  const sourceCounts = {
    resume: resumeRating.overall_score
      ? `${Math.round(
          resumeRating.overall_score
        )}/100`
      : "Analyzed",

    linkedin:
      linkedinAnalysis.skill_count
        ? `${linkedinAnalysis.skill_count} skills`
        : "Analyzed",

    github:
      githubProfile.public_repository_count !==
      undefined
        ? `${githubProfile.public_repository_count} repos`
        : "Analyzed",

    leetcode:
      leetcodeAnalysis.total_solved !==
      undefined
        ? `${leetcodeAnalysis.total_solved} solved`
        : "Analyzed",
  };

  const strongestSkills =
    unifiedSkills.filter(
      (skill) =>
        skill.status ===
        "strongly_supported"
    );

  const warnings = findings.filter(
    (finding) =>
      finding.severity === "warning" ||
      finding.severity === "low"
  );

  const infoFindings = findings.filter(
    (finding) =>
      finding.severity === "info"
  );

  const dsaCoverage =
    leetcodeAnalysis.dsa_coverage || {};

  if (authChecking) {
    return (
      <main className="app auth-page">
        <div className="ambient ambient-one" />
        <div className="ambient ambient-two" />

        <div className="auth-loading">
          <div className="brand-mark">
            <Sparkles size={18} />
          </div>

          <span>
            Loading CareerOS...
          </span>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="app auth-page">
        <div className="ambient ambient-one" />
        <div className="ambient ambient-two" />

        <nav className="navbar">
          {/* CLICKING CAREEROS ALWAYS RETURNS HOME */}
          <a
            href="/"
            className="brand"
            aria-label="CareerOS home"
          >
            <div className="brand-mark">
              <Sparkles size={15} />
            </div>

            <span>CareerOS</span>
          </a>

          <div className="nav-status">
            <span className="status-dot" />
            Career intelligence
          </div>
        </nav>

        <section className="auth-container">
          <div className="auth-card">
            <div className="auth-icon">
              <Sparkles size={20} />
            </div>

            <div className="auth-heading">
              <span>CAREEROS</span>

              <h1>
                {authMode === "login"
                  ? "Welcome back."
                  : "Build your profile."}
              </h1>

              <p>
                {authMode === "login"
                  ? "Sign in to continue your career analysis."
                  : "Create your CareerOS account."}
              </p>
            </div>

            <form
              className="auth-form"
              onSubmit={handleAuth}
            >
              <label>
                Email

                <input
                  type="email"
                  value={authEmail}
                  onChange={(e) =>
                    setAuthEmail(
                      e.target.value
                    )
                  }
                  placeholder="you@example.com"
                  required
                />
              </label>

              <label>
                Password

                <input
                  type="password"
                  value={authPassword}
                  onChange={(e) =>
                    setAuthPassword(
                      e.target.value
                    )
                  }
                  placeholder="••••••••"
                  minLength={6}
                  required
                />
              </label>

              {authError && (
                <div className="auth-error">
                  {authError}
                </div>
              )}

              <button
                className="auth-submit"
                type="submit"
                disabled={authLoading}
              >
                {authLoading
                  ? "Authenticating..."
                  : authMode === "login"
                    ? "Sign in"
                    : "Create account"}

                <ArrowRight size={16} />
              </button>
            </form>

            <div className="auth-switch">
              {authMode === "login"
                ? "Don't have an account?"
                : "Already have an account?"}

              <button
                type="button"
                onClick={() => {
                  setAuthMode(
                    authMode === "login"
                      ? "signup"
                      : "login"
                  );

                  setAuthError("");
                }}
              >
                {authMode === "login"
                  ? "Create one"
                  : "Sign in"}
              </button>
            </div>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main
      className={`app ${
        analysis ? "has-analysis" : ""
      }`}
    >
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {/* NAVBAR */}
      <nav className="navbar">
        {/* CLICKABLE CAREEROS HOME LOGO */}
        <a
          href="/"
          className="brand"
          aria-label="CareerOS home"
        >
          <div className="brand-mark">
            <Sparkles size={15} />
          </div>

          <span>CareerOS</span>
        </a>

        <div className="nav-right">
          {analysis && (
            <button
              className="new-analysis"
              onClick={() => {
                setAnalysis(null);
                setFile(null);
                setError(null);
              }}
            >
              New analysis
            </button>
          )}

          <div className="nav-status">
            <span className="status-dot" />
            Career intelligence
          </div>
        </div>
      </nav>

      {!analysis ? (
        /* =====================================================
           LANDING
           ===================================================== */
        <section className="hero">
          <div className="eyebrow">
            <span />
            YOUR PROFESSIONAL FOOTPRINT
            <span />
          </div>

          <h1>
            Know your career.
            <br />
            <em>Not just your resume.</em>
          </h1>

          <p className="hero-copy">
            CareerOS connects the work you’ve done across your
            professional profiles and turns it into one clear picture.
          </p>

          <div className="upload-wrapper">
            {!file ? (
              <label
                className="upload-card"
                onDragOver={(event) =>
                  event.preventDefault()
                }
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
                  <h2>
                    Drop your resume here
                  </h2>

                  <p>
                    PDF or DOCX · Maximum
                    10MB
                  </p>
                </div>

                <div className="upload-corner">
                  <ArrowRight size={16} />
                </div>
              </label>
            ) : (
              <div
                className="selected-card"
                style={{
                  position: "relative",
                  minHeight: loading
                    ? "116px"
                    : undefined,
                }}
              >
                <div className="selected-info">
                  <div className="file-symbol">
                    <FileText size={20} />
                  </div>

                  <div className="file-details">
                    <strong>
                      {file.name}
                    </strong>

                    <span>
                      {(
                        file.size /
                        1024 /
                        1024
                      ).toFixed(2)}{" "}
                      MB · Ready
                    </span>
                  </div>
                </div>

                {/*
                 * IMPORTANT:
                 * Fixed width means the Analyze button
                 * does NOT resize or jump when loading.
                 */}
                <button
                  className="analyze-button"
                  onClick={analyzeCareer}
                  disabled={loading}
                  style={{
                    width: "145px",
                    minWidth: "145px",
                    flexShrink: 0,
                    justifyContent:
                      "center",
                  }}
                >
                  {loading ? (
                    <>
                      <LoaderCircle
                        size={15}
                        className="spin"
                      />
                      Analyzing
                    </>
                  ) : (
                    <>
                      Analyze career
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>

                {/*
                 * Quiet secondary progress.
                 * This does NOT replace the button.
                 */}
                <div
                  className="analysis-status"
                  style={{
                    position: "absolute",
                    left: "105px",
                    right: "24px",
                    bottom: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    minHeight: "18px",
                    opacity: loading ? 1 : 0,
                    pointerEvents: "none",
                    transition:
                      "opacity 180ms ease",
                  }}
                >
                  <div
                    style={{
                      flex: 1,
                      height: "3px",
                      borderRadius: "999px",
                      background:
                        "rgba(255,255,255,0.08)",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: `${analysisProgress}%`,
                        borderRadius: "999px",
                        background:
                          "currentColor",
                        transition:
                          "width 500ms ease",
                      }}
                    />
                  </div>

                  <span
                    style={{
                      fontSize: "11px",
                      opacity: 0.52,
                      whiteSpace:
                        "nowrap",
                      letterSpacing:
                        "0.01em",
                    }}
                  >
                    {getProgressMessage(
                      analysisProgress
                    )}
                  </span>

                  <strong
                    style={{
                      fontSize: "12px",
                      fontWeight: 600,
                      minWidth: "28px",
                      textAlign: "right",
                      opacity: 0.75,
                    }}
                  >
                    {analysisProgress}%
                  </strong>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="error-message">
              <AlertCircle size={14} />
              {error}
            </div>
          )}

          <div className="source-row">
            {sources.map(
              ({
                name,
                icon: Icon,
              }) => (
                <div
                  className="source-pill"
                  key={name}
                >
                  <span className="source-indicator" />
                  <Icon size={14} />
                  {name}
                </div>
              )
            )}
          </div>

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
        </section>
      ) : (
        /* =====================================================
           RESULTS
           ===================================================== */
        <div className="dashboard">
          {/* HEADER */}
          <section className="dashboard-hero">
            <div className="dashboard-kicker">
              <span className="live-dot" />
              CAREER INTELLIGENCE COMPLETE
            </div>

            <div className="identity-row">
              <div className="identity-copy">
                <h1>
                  {unified?.name ||
                    resume?.profile?.name ||
                    "Candidate"}
                </h1>

                <p>
                  {unified?.headline ||
                    linkedinAnalysis.headline ||
                    "Professional profile"}
                </p>

                <div className="identity-tags">
                  {(
                    unified?.career_domains ||
                    []
                  )
                    .slice(0, 4)
                    .map((domain) => (
                      <span key={domain}>
                        {titleCase(domain)}
                      </span>
                    ))}
                </div>
              </div>

              <ScoreRing
                score={careerReadiness}
                label="READINESS"
                large
              />
            </div>
          </section>

          {/* SOURCE STRIP */}
          <section className="source-grid">
            {sources.map(
              ({
                name,
                key,
                icon,
              }) => (
                <SourceCard
                  key={key}
                  name={name}
                  icon={icon}
                  connected={
                    sourceStatus[key]
                  }
                  value={
                    sourceCounts[key]
                  }
                />
              )
            )}
          </section>

          {/* CAREER SIGNAL */}
          <section className="section-block signal-section">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  01
                </span>

                <div>
                  <span className="micro-label">
                    CAREEROS SIGNAL
                  </span>

                  <h2>
                    Your career,
                    decoded.
                  </h2>
                </div>
              </div>
            </div>

            <div className="signal-grid">
              <div className="signal-main">
                <div className="signal-icon">
                  <Brain size={20} />
                </div>

                <div>
                  <span className="micro-label">
                    PRIMARY DIRECTION
                  </span>

                  <h3>
                    {(
                      unified?.career_domains ||
                      []
                    ).length
                      ? unified.career_domains
                          .map(
                            titleCase
                          )
                          .join(" · ")
                      : "Software Engineering"}
                  </h3>

                  <p>
                    Your strongest evidence comes from technical
                    projects, programming fundamentals and
                    cross-source skill signals. CareerOS found{" "}
                    <strong>
                      {strongestSkills.length}
                    </strong>{" "}
                    strongly supported skills across the available
                    sources.
                  </p>
                </div>
              </div>

              <div className="signal-quote">
                <span>
                  THE BIGGEST SIGNAL
                </span>

                <strong>
                  Build depth before adding
                  more tools.
                </strong>

                <p>
                  Your profile already has a
                  broad technical stack.
                  The next jump comes from
                  stronger evidence, measurable
                  impact and consistency.
                </p>
              </div>
            </div>
          </section>

          {/* SCORE OVERVIEW */}
          <section className="section-block">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  02
                </span>

                <div>
                  <span className="micro-label">
                    PROFILE HEALTH
                  </span>

                  <h2>
                    Where you stand.
                  </h2>
                </div>
              </div>
            </div>

            <div className="health-grid">
              <div className="health-card featured">
                <div>
                  <span className="micro-label">
                    RESUME
                  </span>

                  <strong className="big-score">
                    {Math.round(
                      resumeRating.overall_score ||
                        0
                    )}
                  </strong>

                  <p>
                    Overall resume strength
                  </p>
                </div>

                <FileText size={19} />
              </div>

              <div className="health-card">
                <span className="micro-label">
                  ATS
                </span>

                <strong>
                  {Math.round(
                    resumeRating.ats
                      ?.score || 0
                  )}
                </strong>

                <MetricBar
                  label="ATS readiness"
                  value={
                    resumeRating.ats
                      ?.score
                  }
                />
              </div>

              <div className="health-card">
                <span className="micro-label">
                  PROJECTS
                </span>

                <strong>
                  {Math.round(
                    resumeRating.projects
                      ?.score || 0
                  )}
                </strong>

                <MetricBar
                  label="Project strength"
                  value={
                    resumeRating.projects
                      ?.score
                  }
                />
              </div>

              <div className="health-card">
                <span className="micro-label">
                  IMPACT
                </span>

                <strong>
                  {Math.round(
                    resumeRating
                      .quantified_impact
                      ?.score || 0
                  )}
                </strong>

                <MetricBar
                  label="Quantified impact"
                  value={
                    resumeRating
                      .quantified_impact
                      ?.score
                  }
                />
              </div>
            </div>
          </section>

          {/* SKILLS */}
          <section className="section-block">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  03
                </span>

                <div>
                  <span className="micro-label">
                    EVIDENCE ENGINE
                  </span>

                  <h2>
                    Your skills, mapped.
                  </h2>
                </div>
              </div>

              <span className="section-count">
                {unifiedSkills.length} skills
              </span>
            </div>

            <div className="skills-layout">
              <div className="skills-feature">
                <div className="skills-feature-top">
                  <div>
                    <span className="micro-label">
                      SKILL INVENTORY
                    </span>

                    <h3>
                      {unifiedSkills.length}
                    </h3>

                    <p>
                      Skills CareerOS found across your resume,
                      LinkedIn, GitHub and LeetCode.
                    </p>
                  </div>

                  <ShieldCheck size={25} />
                </div>

                <div className="skill-summary">
                  <span>
                    <strong>
                      {unifiedSkills.length}
                    </strong>{" "}
                    identified
                  </span>

                  <span>
                    <strong>
                      {strongestSkills.length}
                    </strong>{" "}
                    strong evidence
                  </span>

                  <span>
                    <strong>
                      {
                        unifiedSkills.filter(
                          (skill) =>
                            skill.status ===
                            "demonstrated"
                        ).length
                      }
                    </strong>{" "}
                    demonstrated
                  </span>
                </div>

                <div className="skill-cloud">
                  {unifiedSkills.map(
                    (skill) => (
                      <span
                        className={`skill-chip ${
                        skill.status ===
                        "strongly_supported"
                          ? "strong"
                          : skill.status ===
                              "demonstrated"
                            ? "demonstrated"
                            : "limited"
                      }`}
                        key={skill.skill}
                        title={
                          skill.status ===
                          "strongly_supported"
                            ? "Strong multi-source evidence"
                            : skill.status ===
                                "demonstrated"
                              ? "Demonstrated through project/source evidence"
                              : skill.status ===
                                  "claimed_only"
                                ? "Claimed in a profile or resume"
                                : "Limited evidence"
                        }
                      >
                        {skill.status ===
                          "strongly_supported" && (
                          <Check size={11} />
                        )}

                        {titleCase(
                          skill.skill
                        )}
                      </span>
                    )
                  )}
                </div>
              </div>

              <div className="evidence-list">
                {topSkills
                  .slice(0, 6)
                  .map((skill) => (
                    <EvidenceCard
                      key={skill.skill}
                      skill={skill}
                    />
                  ))}
              </div>
            </div>
          </section>

          {/* GITHUB */}
          <section className="section-block">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  04
                </span>

                <div>
                  <span className="micro-label">
                    CODE INTELLIGENCE
                  </span>

                  <h2>
                    Your GitHub, read.
                  </h2>
                </div>
              </div>

              {githubProfile.profile_url && (
                <a
                  href={
                    githubProfile.profile_url
                  }
                  target="_blank"
                  rel="noreferrer"
                  className="section-link"
                >
                  Open GitHub
                  <ExternalLink size={13} />
                </a>
              )}
            </div>

            <div className="repo-grid">
              {(
                githubAnalysis.projects ||
                []
              ).map((project) => (
                <div
                  className="repo-card"
                  key={project.repository}
                >
                  <div className="repo-card-head">
                    <div className="repo-icon">
                      <GithubIcon />
                    </div>

                    <div>
                      <span className="micro-label">
                        {titleCase(
                          project.project_type
                        )}
                      </span>

                      <h3>
                        {project.repository
                          ?.split("/")
                          .pop()}
                      </h3>
                    </div>

                    <span className="repo-score">
                      {(
                        project.project_score ||
                        0
                      ).toFixed(1)}
                    </span>
                  </div>

                  <p>
                    {project.assessment}
                  </p>

                  <div className="tech-row">
                    {(
                      project.technologies ||
                      []
                    )
                      .slice(0, 7)
                      .map((tech) => (
                        <span key={tech}>
                          {tech}
                        </span>
                      ))}
                  </div>

                  <div className="repo-stage">
                    <Activity size={13} />
                    {titleCase(
                      project.project_stage
                    )}
                  </div>
                </div>
              ))}
            </div>

            {(githubAnalysis.evidence_gaps ||
              []).length > 0 && (
              <div className="gap-panel">
                <div className="gap-panel-icon">
                  <CircleAlert size={16} />
                </div>

                <div>
                  <span className="micro-label">
                    ENGINEERING GAPS
                  </span>

                  <div className="gap-list">
                    {(
                      githubAnalysis.evidence_gaps ||
                      []
                    )
                      .slice(0, 4)
                      .map(
                        (
                          gap,
                          index
                        ) => (
                          <span
                            key={index}
                          >
                            {typeof gap ===
                            "string"
                              ? gap
                              : gap.area}
                          </span>
                        )
                      )}
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* LEETCODE */}
          {leetcodeAnalysis &&
            Object.keys(
              leetcodeAnalysis
            ).length > 0 && (
              <section className="section-block">
                <div className="section-heading">
                  <div>
                    <span className="section-number">
                      05
                    </span>

                    <div>
                      <span className="micro-label">
                        PROBLEM SOLVING
                      </span>

                      <h2>
                        Your DSA footprint.
                      </h2>
                    </div>
                  </div>
                </div>

                <div className="leetcode-hero">
                  <div className="leetcode-stat">
                    <span className="micro-label">
                      SOLVED
                    </span>

                    <strong>
                      {
                        leetcodeAnalysis.total_solved
                      }
                    </strong>

                    <span>
                      problems
                    </span>
                  </div>

                  <div className="leetcode-stat">
                    <span className="micro-label">
                      DSA BREADTH
                    </span>

                    <strong>
                      {Math.round(
                        leetcodeAnalysis
                          .dsa_breadth_score ||
                          0
                      )}
                    </strong>

                    <span>
                      / 100
                    </span>
                  </div>

                  <div className="leetcode-stat">
                    <span className="micro-label">
                      PROBLEM SOLVING
                    </span>

                    <strong>
                      {Math.round(
                        leetcodeAnalysis
                          .problem_solving_score ||
                          0
                      )}
                    </strong>

                    <span>
                      / 100
                    </span>
                  </div>

                  <div className="leetcode-stat">
                    <span className="micro-label">
                      CONSISTENCY
                    </span>

                    <strong className="word-stat">
                      {titleCase(
                        leetcodeAnalysis
                          .activity_consistency ||
                          "Unknown"
                      )}
                    </strong>
                  </div>
                </div>

                <div className="leetcode-layout">
                  <div className="difficulty-card">
                    <div className="card-heading">
                      <span>
                        DIFFICULTY EXPOSURE
                      </span>

                      <strong>
                        {titleCase(
                          leetcodeAnalysis
                            .difficulty_exposure ||
                            "Unknown"
                        )}
                      </strong>
                    </div>

                    {Object.entries(
                      leetcodeAnalysis
                        .difficulty_distribution ||
                        {}
                    ).map(
                      ([
                        difficulty,
                        value,
                      ]) => (
                        <MetricBar
                          key={
                            difficulty
                          }
                          label={titleCase(
                            difficulty
                          )}
                          value={
                            Number(
                              value
                            ) * 100
                          }
                          suffix="%"
                        />
                      )
                    )}
                  </div>

                  <div className="dsa-card">
                    <div className="card-heading">
                      <span>
                        DSA COVERAGE
                      </span>

                      <strong>
                        {
                          Object.keys(
                            dsaCoverage
                          ).length
                        } areas
                      </strong>
                    </div>

                    <div className="dsa-bars">
                      {Object.entries(
                        dsaCoverage
                      )
                        .sort(
                          (
                            [, a],
                            [, b]
                          ) =>
                            (b.problems_solved ||
                              0) -
                            (a.problems_solved ||
                              0)
                        )
                        .slice(0, 8)
                        .map(
                          ([
                            area,
                            data,
                          ]) => (
                            <div
                              className="dsa-row"
                              key={area}
                            >
                              <span>
                                {area}
                              </span>

                              <div>
                                <i
                                  style={{
                                    width: `${Math.min(
                                      100,
                                      ((data.problems_solved ||
                                        0) /
                                        50) *
                                        100
                                    )}%`,
                                  }}
                                />
                              </div>

                              <strong>
                                {
                                  data.problems_solved
                                }
                              </strong>
                            </div>
                          )
                        )}
                    </div>
                  </div>
                </div>
              </section>
            )}

          {/* RADAR */}
          <section className="section-block">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  06
                </span>

                <div>
                  <span className="micro-label">
                    CAREER PROFILE
                  </span>

                  <h2>
                    Your capability shape.
                  </h2>
                </div>
              </div>
            </div>

            <div className="radar-card">
              <div className="radar-wrap">
                <Radar
                  values={radarValues}
                />

                <span className="radar-label top">
                  PROJECTS
                </span>

                <span className="radar-label right">
                  DSA
                </span>

                <span className="radar-label bottom">
                  SKILLS
                </span>

                <span className="radar-label left">
                  GITHUB
                </span>
              </div>

              <div className="radar-copy">
                <span className="micro-label">
                  HOW TO READ THIS
                </span>

                <h3>
                  Breadth is not the bottleneck.
                </h3>

                <p>
                  Your profile already spans
                  software engineering,
                  machine learning and
                  problem solving. The weaker
                  signals are mainly around
                  measurable impact,
                  professional experience and
                  demonstrated engineering
                  depth.
                </p>

                <div className="radar-legend">
                  <span>
                    <i />
                    Strong signal
                  </span>

                  <span>
                    <i />
                    Developing
                  </span>
                </div>
              </div>
            </div>
          </section>

          {/* FINDINGS */}
          <section className="section-block">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  07
                </span>

                <div>
                  <span className="micro-label">
                    CROSS-SOURCE INTELLIGENCE
                  </span>

                  <h2>
                    What CareerOS noticed.
                  </h2>
                </div>
              </div>

              <span className="section-count">
                {findings.length} findings
              </span>
            </div>

            <div className="finding-grid">
              {warnings
                .slice(0, 6)
                .map((finding) => (
                  <div
                    className="finding-card warning"
                    key={`${finding.finding_type}-${finding.subject}`}
                  >
                    <div className="finding-icon">
                      <AlertCircle size={16} />
                    </div>

                    <div>
                      <span className="micro-label">
                        {titleCase(
                          finding.finding_type
                        )}
                      </span>

                      <h3>
                        {titleCase(
                          finding.subject
                        )}
                      </h3>

                      <p>
                        {finding.message}
                      </p>
                    </div>
                  </div>
                ))}

              {infoFindings
                .slice(0, 4)
                .map((finding) => (
                  <div
                    className="finding-card info"
                    key={`${finding.finding_type}-${finding.subject}`}
                  >
                    <div className="finding-icon">
                      <Layers3 size={16} />
                    </div>

                    <div>
                      <span className="micro-label">
                        PROFILE SIGNAL
                      </span>

                      <h3>
                        {titleCase(
                          finding.subject
                        )}
                      </h3>

                      <p>
                        {finding.message}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </section>

          {/* NEXT MOVES */}
          <section className="section-block next-section">
            <div className="section-heading">
              <div>
                <span className="section-number">
                  08
                </span>

                <div>
                  <span className="micro-label">
                    ACTION PLAN
                  </span>

                  <h2>
                    Your next moves.
                  </h2>
                </div>
              </div>

              <Target size={19} />
            </div>

            <div className="recommendation-list">
              {(
                resumeRating.recommendations ||
                []
              )
                .slice(0, 5)
                .map(
                  (
                    recommendation,
                    index
                  ) => (
                    <div
                      className="recommendation"
                      key={`${recommendation.area}-${index}`}
                    >
                      <div className="recommendation-index">
                        0{index + 1}
                      </div>

                      <div className="recommendation-copy">
                        <div className="recommendation-meta">
                          <span
                            className={`priority ${String(
                              recommendation.priority
                            ).toLowerCase()}`}
                          >
                            {
                              recommendation.priority
                            }
                          </span>

                          <span>
                            {
                              recommendation.area
                            }
                          </span>
                        </div>

                        <h3>
                          {
                            recommendation.recommendation
                          }
                        </h3>

                        <p>
                          {
                            recommendation.reason
                          }
                        </p>
                      </div>

                      <ChevronRight
                        size={17}
                      />
                    </div>
                  )
                )}
            </div>
          </section>

          {/* FOOTER */}
          <footer className="dashboard-footer">
            <span>
              CAREEROS / CAREER INTELLIGENCE
            </span>

            <span>
              Build a career profile, not
              just a resume.
            </span>
          </footer>
        </div>
      )}

      {!analysis && (
        <footer>
          <span>CAREEROS</span>

          <span>
            Build a career profile, not just
            a resume.
          </span>
        </footer>
      )}
    </main>
  );
}

export default App;