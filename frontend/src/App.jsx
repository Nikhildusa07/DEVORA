import { useState } from "react";
import "./App.css";

function App() {
  const [requirement, setRequirement] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runDevora = async () => {
    if (!requirement.trim()) {
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "https://devora-ah49.onrender.com/api/autonomous-workflow/autonomous/execute",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_path: ".",
            requirement: requirement,
            code: `
def example():
    return True
            `.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "DEVORA workflow failed"
        );
      }

      setResult(data);
    } catch (error) {
      setResult({
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatus = (section) => {
    if (!result || result.error) {
      return "WAITING";
    }

    if (section === "testing") {
      return result.test_execution?.status === "passed"
        ? "PASSED"
        : "FAILED";
    }

    if (section === "security") {
      return result.security_analysis?.status ===
        "security_check_passed"
        ? "PASSED"
        : "REVIEW";
    }

    if (section === "deployment") {
      return result.deployment?.status ===
        "deployment_ready"
        ? "READY"
        : "REVIEW";
    }

    if (section === "monitoring") {
      return result.monitoring?.status === "healthy"
        ? "HEALTHY"
        : "REVIEW";
    }

    if (section === "regression") {
      return result.regression_detection
        ?.regression_detected
        ? "DETECTED"
        : "CLEAR";
    }

    return "COMPLETED";
  };

  const testOutput =
    result?.test_execution?.output || "";

  const testError =
    result?.test_execution?.error || "";

  const regressionDetails =
    result?.regression_detection || null;

  return (
    <div className="devora-app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">D</div>

          <div>
            <h1>DEVORA</h1>

            <span>
              Autonomous AI Software Engineering
            </span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>
      </header>

      <main className="dashboard">
        <section className="hero-section">
          <div className="hero-badge">
            AUTONOMOUS ENGINEERING SYSTEM
          </div>

          <h2>
            Build software with
            <span> autonomous intelligence.</span>
          </h2>

          <p>
            DEVORA understands requirements, analyzes
            repositories, discovers architecture, generates
            implementation plans, tests software, diagnoses
            failures, reviews security and prepares systems
            for deployment.
          </p>
        </section>

        <section className="requirement-card">
          <div className="section-header">
            <div>
              <span className="section-label">
                REQUIREMENT INPUT
              </span>

              <h3>
                What should DEVORA build?
              </h3>
            </div>

            <span className="phase">
              AUTONOMOUS
            </span>
          </div>

          <textarea
            value={requirement}
            onChange={(event) =>
              setRequirement(event.target.value)
            }
            placeholder="Example: Add a student attendance feature with API endpoints and database storage."
          />

          <button
            onClick={runDevora}
            disabled={
              loading ||
              !requirement.trim()
            }
          >
            {loading
              ? "DEVORA IS EXECUTING..."
              : "START AUTONOMOUS WORKFLOW"}
          </button>
        </section>

        <section className="pipeline">
          <div className="section-header">
            <div>
              <span className="section-label">
                ENGINEERING PIPELINE
              </span>

              <h3>
                Autonomous development lifecycle
              </h3>
            </div>
          </div>

          <div className="pipeline-grid">
            {[
              "AI Reasoning",
              "Requirement",
              "Repository",
              "Architecture",
              "Dependencies",
              "Code Generation",
              "Testing",
              "Debugging",
              "Code Review",
              "Security",
              "Performance",
              "Deployment",
              "Monitoring",
              "Regression",
            ].map((item, index) => (
              <div
                className="pipeline-item"
                key={item}
              >
                <span>
                  {String(index + 1).padStart(2, "0")}
                </span>

                <strong>{item}</strong>
              </div>
            ))}
          </div>
        </section>

        {result && !result.error && (
          <section className="result-card">
            <div className="section-header">
              <div>
                <span className="section-label">
                  AUTONOMOUS WORKFLOW
                </span>

                <h3>
                  Engineering Status
                </h3>
              </div>

              <span className="phase">
                {result.next_stage?.toUpperCase()}
              </span>
            </div>

            <div className="result-grid">
              <div className="result-item">
                <span>AI REASONING</span>
                <strong>COMPLETED</strong>
              </div>

              <div className="result-item">
                <span>TESTING</span>
                <strong>
                  {getStatus("testing")}
                </strong>
              </div>

              <div className="result-item">
                <span>CODE REVIEW</span>
                <strong>
                  {result.code_review?.status ===
                  "approved"
                    ? "APPROVED"
                    : "REVIEW"}
                </strong>
              </div>

              <div className="result-item">
                <span>SECURITY</span>
                <strong>
                  {getStatus("security")}
                </strong>
              </div>

              <div className="result-item">
                <span>PERFORMANCE</span>
                <strong>
                  {result.performance_analysis
                    ?.status ===
                  "performance_check_passed"
                    ? "PASSED"
                    : "REVIEW"}
                </strong>
              </div>

              <div className="result-item">
                <span>DEPLOYMENT</span>
                <strong>
                  {getStatus("deployment")}
                </strong>
              </div>

              <div className="result-item">
                <span>MONITORING</span>
                <strong>
                  {getStatus("monitoring")}
                </strong>
              </div>

              <div className="result-item">
                <span>REGRESSION</span>
                <strong>
                  {getStatus("regression")}
                </strong>
              </div>
            </div>

            <div className="workflow-summary">
              <span>WORKFLOW STATUS</span>

              <strong>
                {result.status?.toUpperCase()}
              </strong>
            </div>

            {result.test_execution?.status ===
              "failed" && (
              <div className="diagnostic-panel">
                <div className="section-header">
                  <div>
                    <span className="section-label">
                      FAILURE DIAGNOSIS
                    </span>

                    <h3>
                      Test execution details
                    </h3>
                  </div>
                </div>

                <div className="diagnostic-item">
                  <span>COMMAND</span>

                  <pre>
                    {result.test_execution?.command ||
                      "pytest"}
                  </pre>
                </div>

                <div className="diagnostic-item">
                  <span>TEST OUTPUT</span>

                  <pre>
                    {testOutput ||
                      "No test output returned."}
                  </pre>
                </div>

                <div className="diagnostic-item">
                  <span>TEST ERROR</span>

                  <pre>
                    {testError ||
                      "No test error returned."}
                  </pre>
                </div>

                {result.debugging && (
                  <div className="diagnostic-item">
                    <span>AI FAILURE DIAGNOSIS</span>

                    <pre>
                      {JSON.stringify(
                        result.debugging,
                        null,
                        2
                      )}
                    </pre>
                  </div>
                )}

                {result.auto_fix && (
                  <div className="diagnostic-item">
                    <span>AUTO-FIX ANALYSIS</span>

                    <pre>
                      {JSON.stringify(
                        result.auto_fix,
                        null,
                        2
                      )}
                    </pre>
                  </div>
                )}

                {regressionDetails && (
                  <div className="diagnostic-item">
                    <span>REGRESSION ANALYSIS</span>

                    <pre>
                      {JSON.stringify(
                        regressionDetails,
                        null,
                        2
                      )}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {result?.error && (
          <section className="result-card">
            <div className="section-header">
              <div>
                <span className="section-label">
                  WORKFLOW ERROR
                </span>

                <h3>
                  DEVORA could not complete the workflow
                </h3>
              </div>
            </div>

            <div className="error">
              {result.error}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;