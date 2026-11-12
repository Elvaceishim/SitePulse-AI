import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Clock3,
  CloudSun,
  Factory,
  FileText,
  Flame,
  LayoutDashboard,
  MapPin,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  ThermometerSun,
  Users,
  Wind,
} from "lucide-react";
import "./App.css";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

const API_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const PRIORITY_ORDER = ["critical", "high", "moderate", "low"];

function formatDate(value) {
  if (!value) return "Unknown";
  return new Date(value).toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatCategory(category = "") {
  return category.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (char) =>
    char.toUpperCase()
  );
}

function getRiskIcon(category) {
  const icons = {
    heat: ThermometerSun,
    air_quality: Wind,
    occupational: ShieldAlert,
    cold: CloudSun,
    outbreak: AlertTriangle,
  };

  return icons[category?.toLowerCase()] || Activity;
}

function getUrgencyLabel(urgency = "") {
  return urgency.replaceAll("_", " ").replace(/\b\w/g, (char) =>
    char.toUpperCase()
  );
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");

  const [reviews, setReviews] = useState({});
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  const [selectedSite, setSelectedSite] = useState(null);
  const [reviewerName, setReviewerName] = useState("");
  const [reviewComment, setReviewComment] = useState("");
  const [reviewStatus, setReviewStatus] = useState("reviewed");
  const [savingReview, setSavingReview] = useState(false);
  const [reviewError, setReviewError] = useState("");

  async function loadDashboard(isRefresh = false) {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");

    try {
      const response = await fetch(`${API_URL}/briefings/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(
          errorBody.detail || `Request failed with status ${response.status}`
        );
      }

      const result = await response.json();
      setDashboard(result);

      const reviewsResponse = await fetch(
        `${API_URL}/interventions/reviews`
      );

      if (!reviewsResponse.ok) {
        throw new Error("Could not retrieve saved intervention reviews.");
      }

      const savedReviews = await reviewsResponse.json();

      const reviewMap = Object.fromEntries(
        savedReviews.map((review) => [
          review.assessment_id,
          review,
        ])
      );

      setReviews(reviewMap);
    } catch (err) {
      setError(
        `${err.message}. Check that your FastAPI backend is running on port 8000.`
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  async function submitReview() {
    if (!selectedIntervention) return;

    if (!reviewerName.trim()) {
      setReviewError("Enter the supervisor's name.");
      return;
    }

    const assessmentId = selectedIntervention.risk.assessment.id;

    setSavingReview(true);
    setReviewError("");

    try {
      const response = await fetch(
        `${API_URL}/interventions/${assessmentId}/review`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: reviewStatus,
            reviewer_name: reviewerName.trim(),
            comment: reviewComment.trim(),
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Could not save the review.");
      }

      setReviews((previous) => ({
        ...previous,
        [assessmentId]: result,
      }));

      setSelectedIntervention(null);
      setReviewerName("");
      setReviewComment("");
      setReviewStatus("reviewed");
    } catch (err) {
      setReviewError(err.message);
    } finally {
      setSavingReview(false);
    }
  }

  function exportBriefingPdf() {
    if (!dashboard) return;

    const doc = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 15;

    const generatedDate = new Date(dashboard.generated_at);

    const formatPdfDate = (date) =>
      new Date(date).toLocaleString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });

    const addSectionTitle = (title, y) => {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(13);
      doc.setTextColor(24, 61, 75);
      doc.text(title, margin, y);
      return y + 8;
    };

    // ------------------------------------------------
    // REPORT HEADER
    // ------------------------------------------------

    doc.setFillColor(17, 42, 59);
    doc.rect(0, 0, pageWidth, 43, "F");

    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(21);
    doc.text("SitePulse AI", margin, 19);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text("Multi-Site Risk Intelligence Report", margin, 27);

    doc.setFontSize(8);
    doc.text(
      `Generated: ${formatPdfDate(generatedDate)}`,
      margin,
      35
    );

    doc.setTextColor(190, 220, 215);
    doc.text(
      "SYNTHETIC DATA DEMONSTRATION",
      pageWidth - margin,
      35,
      { align: "right" }
    );

    let y = 55;

    // ------------------------------------------------
    // EXECUTIVE SUMMARY
    // ------------------------------------------------

    y = addSectionTitle("Executive Summary", y);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(65, 83, 96);

    const summaryLines = doc.splitTextToSize(
      dashboard.briefing.executive_summary,
      pageWidth - margin * 2
    );

    doc.text(summaryLines, margin, y);

    y += summaryLines.length * 5 + 9;

    // ------------------------------------------------
    // DASHBOARD OVERVIEW
    // ------------------------------------------------

    y = addSectionTitle("Risk Overview", y);

    const risks = dashboard.prioritized_risks || [];

    const priorityCounts = {
      Critical: 0,
      High: 0,
      Moderate: 0,
      Low: 0,
    };

    risks.forEach((risk) => {
      const band =
        risk.priority_band.charAt(0).toUpperCase() +
        risk.priority_band.slice(1).toLowerCase();

      if (priorityCounts[band] !== undefined) {
        priorityCounts[band] += 1;
      }
    });

    autoTable(doc, {
      startY: y,
      head: [[
        "Monitored sites",
        "Assessments",
        "Critical",
        "High",
        "Moderate",
        "Low",
      ]],
      body: [[
        dashboard.sites.length,
        risks.length,
        priorityCounts.Critical,
        priorityCounts.High,
        priorityCounts.Moderate,
        priorityCounts.Low,
      ]],
      theme: "grid",
      styles: {
        fontSize: 8,
        halign: "center",
        cellPadding: 3,
      },
      headStyles: {
        fillColor: [30, 119, 108],
        textColor: 255,
      },
    });

    y = doc.lastAutoTable.finalY + 12;

    // ------------------------------------------------
    // SITE SUMMARIES
    // ------------------------------------------------

    y = addSectionTitle("Site Intelligence", y);

    dashboard.sites.forEach((site) => {
      const siteRisks = risks.filter(
        (risk) => risk.site.id === site.id
      );

      const siteSummary = dashboard.briefing.site_summaries.find(
        (item) => item.site_id === site.id
      );

      if (y > pageHeight - 45) {
        doc.addPage();
        y = 20;
      }

      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.setTextColor(35, 65, 81);
      doc.text(site.name, margin, y);

      y += 5;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(105, 122, 133);

      doc.text(
        `${site.location} | ${site.industry} | ${site.workforce_size} workers`,
        margin,
        y
      );

      y += 5;

      if (siteSummary) {
        const lines = doc.splitTextToSize(
          siteSummary.summary,
          pageWidth - margin * 2
        );

        doc.text(lines, margin, y);
        y += lines.length * 4 + 3;
      }

      autoTable(doc, {
        startY: y,
        head: [[
          "Category",
          "Score",
          "Priority",
          "Freshness",
          "Review status",
        ]],
        body: siteRisks.map((risk) => {
          const assessment = risk.assessment;
          const savedReview = reviews[assessment.id];

          return [
            formatCategory(assessment.category),
            `${assessment.score}/100`,
            risk.priority_band.toUpperCase(),
            risk.is_stale ? "Stale" : "Current",
            savedReview
              ? savedReview.status === "requires_follow_up"
                ? "Follow-up required"
                : "Reviewed"
              : "Pending review",
          ];
        }),
        theme: "grid",
        styles: {
          fontSize: 7,
          cellPadding: 2.5,
        },
        headStyles: {
          fillColor: [30, 119, 108],
          textColor: 255,
        },
      });

      y = doc.lastAutoTable.finalY + 10;
    });

    // ------------------------------------------------
    // PRIORITISED INTERVENTIONS
    // ------------------------------------------------

    if (y > pageHeight - 55) {
      doc.addPage();
      y = 20;
    }

    y = addSectionTitle("Prioritised Interventions", y);

    const interventionRows = [...dashboard.interventions]
      .sort(
        (a, b) =>
          b.risk.assessment.score - a.risk.assessment.score
      )
      .map((item) => {
        const assessment = item.risk.assessment;
        const savedReview = reviews[assessment.id];

        return [
          item.risk.site.name,
          formatCategory(assessment.category),
          `${assessment.score}/100`,
          item.risk.priority_band.toUpperCase(),
          item.urgency.replaceAll("_", " "),
          savedReview
            ? savedReview.status === "requires_follow_up"
              ? `Follow-up: ${savedReview.reviewer_name}`
              : `Reviewed: ${savedReview.reviewer_name}`
            : "Pending review",
        ];
      });

    autoTable(doc, {
      startY: y,
      head: [[
        "Site",
        "Risk",
        "Score",
        "Priority",
        "Urgency",
        "Review",
      ]],
      body: interventionRows,
      theme: "grid",
      styles: {
        fontSize: 7,
        cellPadding: 2.5,
        overflow: "linebreak",
      },
      headStyles: {
        fillColor: [30, 119, 108],
        textColor: 255,
      },
      columnStyles: {
        0: { cellWidth: 36 },
        1: { cellWidth: 24 },
        2: { cellWidth: 17 },
        3: { cellWidth: 22 },
        4: { cellWidth: 29 },
        5: { cellWidth: 45 },
      },
    });

    // ------------------------------------------------
    // INTERVENTION DETAILS
    // ------------------------------------------------

    y = doc.lastAutoTable.finalY + 12;

    y = addSectionTitle("Recommended Actions", y);

    dashboard.interventions.forEach((item) => {
      if (y > pageHeight - 45) {
        doc.addPage();
        y = 20;
      }

      const assessment = item.risk.assessment;

      doc.setFont("helvetica", "bold");
      doc.setFontSize(9);
      doc.setTextColor(35, 65, 81);

      doc.text(
        `${item.risk.site.name} | ${formatCategory(assessment.category)} | ${assessment.score}/100`,
        margin,
        y
      );

      y += 5;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(80, 98, 110);

      const actionLines = doc.splitTextToSize(
        item.recommended_action,
        pageWidth - margin * 2
      );

      doc.text(actionLines, margin, y);
      y += actionLines.length * 4 + 5;

      if (item.data_warning) {
        doc.setTextColor(170, 105, 35);

        const warningLines = doc.splitTextToSize(
          `DATA WARNING: ${item.data_warning}`,
          pageWidth - margin * 2
        );

        doc.text(warningLines, margin, y);
        y += warningLines.length * 4 + 5;
      }
    });

    // ------------------------------------------------
    // SUPERVISOR REVIEW RECORDS
    // ------------------------------------------------

    if (y > pageHeight - 45) {
      doc.addPage();
      y = 20;
    }

    y = addSectionTitle("Supervisor Review Records", y);

    const reviewRows = Object.values(reviews).map((review) => [
      review.reviewer_name,
      review.status === "requires_follow_up"
        ? "Requires follow-up"
        : "Reviewed",
      review.comment || "No comment provided",
      formatPdfDate(review.reviewed_at),
    ]);

    autoTable(doc, {
      startY: y,
      head: [[
        "Reviewer",
        "Decision",
        "Comment",
        "Reviewed at",
      ]],
      body: reviewRows.length
        ? reviewRows
        : [["No reviews submitted", "-", "-", "-"]],
      theme: "grid",
      styles: {
        fontSize: 7,
        cellPadding: 2.5,
        overflow: "linebreak",
      },
      headStyles: {
        fillColor: [30, 119, 108],
        textColor: 255,
      },
    });

    // ------------------------------------------------
    // FOOTERS AND PAGE NUMBERS
    // ------------------------------------------------

    const pageCount = doc.internal.getNumberOfPages();

    for (let page = 1; page <= pageCount; page++) {
      doc.setPage(page);

      doc.setDrawColor(225, 232, 235);
      doc.line(
        margin,
        pageHeight - 13,
        pageWidth - margin,
        pageHeight - 13
      );

      doc.setFont("helvetica", "normal");
      doc.setFontSize(7);
      doc.setTextColor(135, 150, 159);

      doc.text(
        "Independent prototype | Synthetic demonstration data only",
        margin,
        pageHeight - 8
      );

      doc.text(
        `Page ${page} of ${pageCount}`,
        pageWidth - margin,
        pageHeight - 8,
        { align: "right" }
      );
    }

    doc.save("SitePulse-AI-Supervisor-Briefing.pdf");
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const stats = useMemo(() => {
    if (!dashboard) return null;

    const risks = dashboard.prioritized_risks || [];

    const distribution = PRIORITY_ORDER.reduce((result, level) => {
      result[level] = risks.filter(
        (risk) => risk.priority_band?.toLowerCase() === level
      ).length;
      return result;
    }, {});

    return {
      sites: dashboard.sites?.length || 0,
      assessments: dashboard.risk_assessments?.length || 0,
      critical: distribution.critical,
      stale: risks.filter((risk) => risk.is_stale).length,
      distribution,
    };
  }, [dashboard]);

  const interventions = useMemo(() => {
    if (!dashboard) return [];

    const notes = dashboard.briefing?.intervention_notes || [];

    return [...(dashboard.interventions || [])]
      .sort(
        (a, b) =>
          (b.risk?.assessment?.score || 0) -
          (a.risk?.assessment?.score || 0)
      )
      .map((intervention) => {
        const assessmentId = intervention.risk?.assessment?.id;
        const note = notes.find(
          (item) => item.assessment_id === assessmentId
        );

        return {
          ...intervention,
          priorityExplanation: note?.priority_explanation,
        };
      });
  }, [dashboard]);

  const filteredInterventions = useMemo(() => {
    if (activeFilter === "all") return interventions;

    return interventions.filter(
      (item) =>
        item.risk?.priority_band?.toLowerCase() === activeFilter
    );
  }, [interventions, activeFilter]);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-mark">
          <Activity size={28} />
        </div>
        <h2>Preparing your risk intelligence dashboard</h2>
        <p>Analysing site assessments and generating intervention briefings.</p>
        <div className="loading-track">
          <div />
        </div>
      </div>
    );
  }

  if (error && !dashboard) {
    return (
      <div className="error-screen">
        <div className="error-icon">
          <AlertCircle size={28} />
        </div>
        <h2>We couldn't load SitePulse AI</h2>
        <p>{error}</p>
        <button className="primary-button" onClick={() => loadDashboard()}>
          <RefreshCw size={16} />
          Try again
        </button>
      </div>
    );
  }

  const topIntervention = interventions[0];
  const topRisk = topIntervention?.risk?.assessment;
  const topSite = topIntervention?.risk?.site;
  const briefing = dashboard?.briefing;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={22} strokeWidth={2.4} />
          </div>
          <div>
            <div className="brand-name">SitePulse<span>AI</span></div>
            <div className="brand-caption">RISK INTELLIGENCE</div>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>
        <nav className="side-nav">
          <a className="nav-item active" href="#overview">
            <LayoutDashboard size={18} />
            Overview
          </a>
          <a className="nav-item" href="#sites">
            <Factory size={18} />
            Sites
          </a>
          <a className="nav-item" href="#interventions">
            <ShieldCheck size={18} />
            Interventions
          </a>
          <a className="nav-item" href="#briefing">
            <FileText size={18} />
            AI Briefing
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="status-dot" />
            <span>Prototype environment</span>
          </div>
          <p>Independent demonstration project</p>
          <div className="sidebar-version">SITEPULSE AI · V0.1</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Overview</strong>
          </div>
          <div className="topbar-actions">
            <div className="demo-badge">
              <span />
              SYNTHETIC DATA
            </div>

            <button
              className="export-button"
              onClick={exportBriefingPdf}
              disabled={!dashboard}
              title="Export supervisor briefing as PDF"
            >
              <FileText size={15} />
              <span>Export PDF</span>
            </button>

            <button
              className="icon-button"
              aria-label="Refresh dashboard"
              onClick={() => loadDashboard(true)}
              disabled={refreshing}
            >
              <RefreshCw size={17} className={refreshing ? "spin" : ""} />
            </button>
            <div className="avatar">SP</div>
          </div>
        </header>

        <div className="page-content" id="overview">
          <section className="page-heading">
            <div>
              <div className="eyebrow">MULTI-SITE RISK MONITORING</div>
              <h1>Risk overview</h1>
              <p>
                A consolidated view of environmental and occupational risks
                across monitored sites.
              </p>
            </div>
            <div className="updated-label">
              <Clock3 size={14} />
              Updated {formatDate(dashboard?.generated_at)}
            </div>
          </section>

          {error && (
            <div className="inline-error">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <section className="stats-grid">
            <StatCard
              label="MONITORED SITES"
              value={stats?.sites ?? 0}
              detail="Across all locations"
              icon={<Factory size={19} />}
              tone="blue"
            />
            <StatCard
              label="RISK ASSESSMENTS"
              value={stats?.assessments ?? 0}
              detail="Available assessments"
              icon={<Activity size={19} />}
              tone="purple"
            />
            <StatCard
              label="CRITICAL RISKS"
              value={stats?.critical ?? 0}
              detail="Require immediate review"
              icon={<Flame size={19} />}
              tone="red"
            />
            <StatCard
              label="STALE ASSESSMENTS"
              value={stats?.stale ?? 0}
              detail="Require data verification"
              icon={<Clock3 size={19} />}
              tone="amber"
            />
          </section>

          <section className="overview-grid">
            <div className="panel distribution-panel">
              <div className="panel-heading">
                <div>
                  <h2>Risk distribution</h2>
                  <p>Assessments by calculated priority band</p>
                </div>
                <span className="panel-icon">
                  <Activity size={18} />
                </span>
              </div>

              <div className="distribution-total">
                <strong>{stats?.assessments ?? 0}</strong>
                <span>Total assessments</span>
              </div>

              <div className="distribution-bar">
                {PRIORITY_ORDER.map((level) => {
                  const count = stats?.distribution[level] || 0;
                  const percentage = stats?.assessments
                    ? (count / stats.assessments) * 100
                    : 0;

                  return (
                    <div
                      key={level}
                      className={`distribution-segment ${level}`}
                      style={{ width: `${percentage}%` }}
                    />
                  );
                })}
              </div>

              <div className="legend-list">
                {PRIORITY_ORDER.map((level) => (
                  <div className="legend-item" key={level}>
                    <span className={`legend-dot ${level}`} />
                    <span className="legend-name">
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </span>
                    <strong>{stats?.distribution[level] || 0}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel priority-panel">
              <div className="panel-heading">
                <div>
                  <h2>Highest-priority intervention</h2>
                  <p>Top-ranked item from the current assessment set</p>
                </div>
                <span className="priority-indicator">
                  <ArrowUpRight size={17} />
                </span>
              </div>

              {topIntervention ? (
                <>
                  <div className="priority-site">
                    <div className="priority-site-icon">
                      <MapPin size={17} />
                    </div>
                    <div>
                      <strong>{topSite?.name}</strong>
                      <span>{topSite?.location}</span>
                    </div>
                    <span
                      className={`risk-badge ${topIntervention.risk.priority_band.toLowerCase()}`}
                    >
                      {topIntervention.risk.priority_band}
                    </span>
                  </div>

                  <div className="priority-risk">
                    <div>
                      <span className="mini-label">RISK CATEGORY</span>
                      <h3>{formatCategory(topRisk?.category)}</h3>
                    </div>
                    <div className="score-display">
                      <strong>{topRisk?.score}</strong>
                      <span>/ 100</span>
                    </div>
                  </div>

                  <div className="priority-action">
                    <span className="mini-label">RECOMMENDED ACTION</span>
                    <p>{topIntervention.recommended_action}</p>
                  </div>

                  <div className="priority-footer">
                    <span>
                      <AlertTriangle size={14} />
                      {getUrgencyLabel(topIntervention.urgency)}
                    </span>
                    <span>Human review required</span>
                  </div>
                </>
              ) : (
                <p className="empty-state">No intervention data available.</p>
              )}
            </div>
          </section>

          <section className="section-block" id="sites">
            <div className="section-heading">
              <div>
                <div className="eyebrow">LOCATION INTELLIGENCE</div>
                <h2>Site overview</h2>
                <p>Risk summaries generated for each monitored location.</p>
              </div>
              <span className="section-count">
                {dashboard?.sites?.length || 0} SITES
              </span>
            </div>

            <div className="site-grid">
              {(dashboard?.sites || []).map((site) => {
                const siteRisks = (dashboard.prioritized_risks || []).filter(
                  (risk) => risk.site.id === site.id
                );
                const highest = [...siteRisks].sort(
                  (a, b) => b.assessment.score - a.assessment.score
                )[0];
                const siteSummary = briefing?.site_summaries?.find(
                  (item) => item.site_id === site.id
                );

                return (
                  <article className="site-card" key={site.id}>
                    <div className="site-card-top">
                      <div className="site-avatar">
                        <Factory size={19} />
                      </div>
                      <span className="site-active">
                        <span />
                        Active
                      </span>
                    </div>

                    <h3>{site.name}</h3>
                    <div className="site-location">
                      <MapPin size={13} />
                      {site.location}
                    </div>

                    <div className="site-meta">
                      <span>{site.industry}</span>
                      <span>
                        <Users size={13} />
                        {site.workforce_size} workers
                      </span>
                    </div>

                    <div className="site-divider" />

                    <div className="site-risk-row">
                      <span>Assessments</span>
                      <strong>{siteRisks.length}</strong>
                    </div>
                    <div className="site-risk-row">
                      <span>Highest score</span>
                      <strong>
                        {highest ? `${highest.assessment.score}/100` : "—"}
                      </strong>
                    </div>
                    <div className="site-risk-row">
                      <span>Priority</span>
                      {highest ? (
                        <span
                          className={`risk-badge ${highest.priority_band.toLowerCase()}`}
                        >
                          {highest.priority_band}
                        </span>
                      ) : (
                        <strong>—</strong>
                      )}
                    </div>

                    {siteSummary && (
                      <div className="site-summary">
                        <span className="mini-label">AI SITE SUMMARY</span>
                        <p>{siteSummary.summary}</p>
                      </div>
                    )}
                    <button
                      className="site-details-button"
                      onClick={() => setSelectedSite(site)}
                    >
                      View site details
                      <ArrowUpRight size={14} />
                    </button>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="section-block" id="interventions">
            <div className="section-heading">
              <div>
                <div className="eyebrow">ACTION PRIORITISATION</div>
                <h2>Intervention queue</h2>
                <p>
                  Recommended actions ranked using deterministic risk
                  prioritisation.
                </p>
              </div>
              <span className="section-count">
                {interventions.length} INTERVENTIONS
              </span>
            </div>

            <div className="filter-row">
              {["all", "critical", "high", "moderate", "low"].map((filter) => (
                <button
                  key={filter}
                  className={`filter-button ${
                    activeFilter === filter ? "selected" : ""
                  }`}
                  onClick={() => setActiveFilter(filter)}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                </button>
              ))}
            </div>

            <div className="intervention-list">
              {filteredInterventions.map((item) => {
                const risk = item.risk?.assessment;
                const site = item.risk?.site;
                const RiskIcon = getRiskIcon(risk?.category);

                return (
                  <article
                    className="intervention-card"
                    key={risk?.id}
                  >
                    <div className="intervention-main">
                      <div className={`intervention-icon ${item.risk?.priority_band?.toLowerCase()}`}>
                        <RiskIcon size={20} />
                      </div>
                      <div className="intervention-content">
                        <div className="intervention-title-row">
                          <h3>{formatCategory(risk?.category)}</h3>
                          <span
                            className={`risk-badge ${item.risk?.priority_band?.toLowerCase()}`}
                          >
                            {item.risk?.priority_band}
                          </span>
                          {item.risk?.is_stale && (
                            <span className="stale-badge">
                              <Clock3 size={12} />
                              Stale data
                            </span>
                          )}
                        </div>
                        <div className="intervention-location">
                          {site?.name} · {site?.location}
                        </div>
                        <p className="intervention-description">
                          {risk?.description}
                        </p>

                        <div className="action-block">
                          <span className="mini-label">
                            RECOMMENDED INTERVENTION
                          </span>
                          <p>{item.recommended_action}</p>
                        </div>

                        {item.priorityExplanation && (
                          <div className="ai-explanation">
                            <span>
                              <Activity size={13} />
                              AI PRIORITY EXPLANATION
                            </span>
                            <p>{item.priorityExplanation}</p>
                          </div>
                        )}

                        {item.data_warning && (
                          <div className="data-warning">
                            <AlertTriangle size={14} />
                            {item.data_warning}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="intervention-side">
                      <div className="intervention-score">
                        <strong>{risk?.score}</strong>
                        <span>/100</span>
                      </div>
                      <span className="urgency-label">
                        {getUrgencyLabel(item.urgency)}
                      </span>
                      {(() => {
                        const savedReview = reviews[risk.id];

                        return (
                          <>
                            <span
                              className={`review-status ${
                                savedReview?.status || "pending"
                              }`}
                            >
                              <ShieldCheck size={13} />
                              {savedReview
                                ? savedReview.status === "requires_follow_up"
                                  ? "Follow-up required"
                                  : "Reviewed"
                                : "Pending review"}
                            </span>

                            <button
                              className="review-button"
                              onClick={() => {
                                setSelectedIntervention(item);
                                setReviewerName(savedReview?.reviewer_name || "");
                                setReviewComment(savedReview?.comment || "");
                                setReviewStatus(
                                  savedReview?.status === "requires_follow_up"
                                    ? "requires_follow_up"
                                    : "reviewed"
                                );
                                setReviewError("");
                              }}
                            >
                              {savedReview ? "View / update review" : "Review intervention"}
                            </button>
                          </>
                        );
                      })()}
                    </div>
                  </article>
                );
              })}

              {filteredInterventions.length === 0 && (
                <div className="empty-state">
                  No interventions match this priority filter.
                </div>
              )}
            </div>
          </section>

          <section className="section-block briefing-section" id="briefing">
            <div className="section-heading">
              <div>
                <div className="eyebrow">AI-ASSISTED DECISION SUPPORT</div>
                <h2>Supervisor briefing</h2>
                <p>
                  A concise operational view generated from the supplied risk
                  assessments.
                </p>
              </div>
              <div className="ai-label">
                <Activity size={14} />
                AI GENERATED
              </div>
            </div>

            <div className="briefing-card">
              <div className="briefing-header">
                <div className="briefing-icon">
                  <FileText size={20} />
                </div>
                <div>
                  <h3>Executive summary</h3>
                  <span>Generated from current site assessments</span>
                </div>
              </div>
              <p className="executive-summary">
                {briefing?.executive_summary ||
                  "No executive summary is available."}
              </p>
              <div className="briefing-footer">
                <span>
                  <ShieldCheck size={14} />
                  Risk scores and priorities are calculated by the rules engine.
                </span>
                <span>Supervisor review required</span>
              </div>
            </div>
          </section>

        {selectedSite && (
          <div
            className="modal-overlay"
            onClick={(event) => {
              if (event.target === event.currentTarget) {
                setSelectedSite(null);
              }
            }}
          >
            <section
              className="site-detail-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="site-detail-title"
            >
              {(() => {
                const siteRisks = (dashboard?.prioritized_risks || [])
                  .filter((risk) => risk.site.id === selectedSite.id)
                  .sort(
                    (a, b) =>
                      b.assessment.score - a.assessment.score
                  );

                const siteSummary = dashboard?.briefing?.site_summaries?.find(
                  (item) => item.site_id === selectedSite.id
                );

                return (
                  <>
                    <div className="modal-header">
                      <div>
                        <div className="eyebrow">SITE INTELLIGENCE</div>
                        <h2 id="site-detail-title">{selectedSite.name}</h2>
                        <p>
                          {selectedSite.location} · {selectedSite.industry}
                        </p>
                      </div>

                      <button
                        className="modal-close"
                        onClick={() => setSelectedSite(null)}
                        aria-label="Close site details"
                      >
                        ×
                      </button>
                    </div>

                    <div className="site-detail-meta">
                      <div>
                        <span className="mini-label">LOCATION</span>
                        <strong>{selectedSite.location}</strong>
                      </div>
                      <div>
                        <span className="mini-label">INDUSTRY</span>
                        <strong>{selectedSite.industry}</strong>
                      </div>
                      <div>
                        <span className="mini-label">WORKFORCE</span>
                        <strong>{selectedSite.workforce_size} workers</strong>
                      </div>
                      <div>
                        <span className="mini-label">ASSESSMENTS</span>
                        <strong>{siteRisks.length}</strong>
                      </div>
                    </div>

                    {siteSummary && (
                      <div className="site-detail-summary">
                        <div className="site-detail-summary-heading">
                          <Activity size={16} />
                          AI SITE SUMMARY
                        </div>
                        <p>{siteSummary.summary}</p>
                      </div>
                    )}

                    <div className="site-detail-section-heading">
                      <div>
                        <h3>Risk assessments</h3>
                        <p>
                          Assessments associated with this site, ranked by score.
                        </p>
                      </div>
                      <span className="section-count">
                        {siteRisks.length} ASSESSMENTS
                      </span>
                    </div>

                    <div className="site-assessment-list">
                      {siteRisks.map((risk) => {
                        const assessment = risk.assessment;

                        const intervention = (dashboard.interventions || []).find(
                          (item) =>
                            item.risk.assessment.id === assessment.id
                        );

                        const savedReview = reviews[assessment.id];
                        const RiskIcon = getRiskIcon(assessment.category);

                        return (
                          <article
                            className="site-assessment-card"
                            key={assessment.id}
                          >
                            <div className="site-assessment-top">
                              <div className="site-assessment-title">
                                <div
                                  className={`intervention-icon ${risk.priority_band.toLowerCase()}`}
                                >
                                  <RiskIcon size={18} />
                                </div>

                                <div>
                                  <h4>{formatCategory(assessment.category)}</h4>
                                  <span>
                                    Reported level:{" "}
                                    {formatCategory(assessment.risk_level)}
                                  </span>
                                </div>
                              </div>

                              <div className="site-assessment-score">
                                <strong>{assessment.score}</strong>
                                <span>/100</span>
                              </div>
                            </div>

                            <div className="site-assessment-badges">
                              <span
                                className={`risk-badge ${risk.priority_band.toLowerCase()}`}
                              >
                                {risk.priority_band}
                              </span>

                              {risk.is_stale ? (
                                <span className="stale-badge">
                                  <Clock3 size={12} />
                                  Stale data
                                </span>
                              ) : (
                                <span className="fresh-badge">
                                  <CheckCircle2 size={12} />
                                  Current data
                                </span>
                              )}

                              <span
                                className={`review-status ${
                                  savedReview?.status || "pending"
                                }`}
                              >
                                <ShieldCheck size={12} />
                                {savedReview
                                  ? savedReview.status === "requires_follow_up"
                                    ? "Follow-up required"
                                    : "Reviewed"
                                  : "Pending review"}
                              </span>
                            </div>

                            <p className="site-assessment-description">
                              {assessment.description}
                            </p>

                            <div className="site-assessment-meta">
                              <span>
                                Source: {assessment.source}
                              </span>
                              <span>
                                Observed: {formatDate(assessment.observed_at)}
                              </span>
                            </div>

                            {intervention && (
                              <div className="site-assessment-action">
                                <span className="mini-label">
                                  RECOMMENDED INTERVENTION
                                </span>
                                <p>{intervention.recommended_action}</p>

                                <button
                                  className="site-review-link"
                                  onClick={() => {
                                    setSelectedSite(null);
                                    setSelectedIntervention(intervention);
                                    setReviewerName(
                                      savedReview?.reviewer_name || ""
                                    );
                                    setReviewComment(
                                      savedReview?.comment || ""
                                    );
                                    setReviewStatus(
                                      savedReview?.status === "requires_follow_up"
                                        ? "requires_follow_up"
                                        : "reviewed"
                                    );
                                    setReviewError("");
                                  }}
                                >
                                  {savedReview
                                    ? "View / update review"
                                    : "Review intervention"}
                                  <ArrowUpRight size={13} />
                                </button>
                              </div>
                            )}
                          </article>
                        );
                      })}

                      {siteRisks.length === 0 && (
                        <div className="empty-state">
                          No risk assessments are currently available for this site.
                        </div>
                      )}
                    </div>

                    <div className="site-detail-footer">
                      <span>
                        <ShieldCheck size={14} />
                        Risk scores and priority bands are calculated by the rules engine.
                      </span>

                      <button
                        className="secondary-button"
                        onClick={() => setSelectedSite(null)}
                      >
                        Close site details
                      </button>
                    </div>
                  </>
                );
              })()}
            </section>
          </div>
        )}

          {selectedIntervention && (
            <div
              className="modal-overlay"
              onClick={(event) => {
                if (event.target === event.currentTarget) {
                  setSelectedIntervention(null);
                }
              }}
            >
              <section
                className="review-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="review-modal-title"
              >
                <div className="modal-header">
                  <div>
                    <div className="eyebrow">SUPERVISOR WORKFLOW</div>
                    <h2 id="review-modal-title">Intervention review</h2>
                    <p>Inspect the assessment and record a review decision.</p>
                  </div>

                  <button
                    className="modal-close"
                    onClick={() => setSelectedIntervention(null)}
                    aria-label="Close review"
                  >
                    ×
                  </button>
                </div>

                {(() => {
                  const risk = selectedIntervention.risk.assessment;
                  const site = selectedIntervention.risk.site;
                  const savedReview = reviews[risk.id];

                  return (
                    <>
                      <div className="modal-site">
                        <div>
                          <strong>{site.name}</strong>
                          <span>{site.location} · {site.industry}</span>
                        </div>

                        <span
                          className={`risk-badge ${
                            selectedIntervention.risk.priority_band.toLowerCase()
                          }`}
                        >
                          {selectedIntervention.risk.priority_band}
                        </span>
                      </div>

                      <div className="modal-evidence-grid">
                        <div>
                          <span className="mini-label">RISK CATEGORY</span>
                          <strong>{formatCategory(risk.category)}</strong>
                        </div>

                        <div>
                          <span className="mini-label">RISK SCORE</span>
                          <strong>{risk.score}/100</strong>
                        </div>

                        <div>
                          <span className="mini-label">REPORTED RISK LEVEL</span>
                          <strong>{formatCategory(risk.risk_level)}</strong>
                        </div>

                        <div>
                          <span className="mini-label">DATA FRESHNESS</span>
                          <strong>
                            {selectedIntervention.risk.is_stale
                              ? "Stale"
                              : "Current"}
                          </strong>
                        </div>
                      </div>

                      <div className="modal-section">
                        <span className="mini-label">ASSESSMENT DESCRIPTION</span>
                        <p>{risk.description}</p>
                      </div>

                      <div className="modal-section">
                        <span className="mini-label">ASSESSMENT SOURCE</span>
                        <p>{risk.source}</p>
                        <span className="modal-timestamp">
                          Observed {formatDate(risk.observed_at)}
                        </span>
                      </div>

                      <div className="modal-section action-block">
                        <span className="mini-label">RECOMMENDED ACTION</span>
                        <p>{selectedIntervention.recommended_action}</p>
                        <span className="modal-rationale">
                          {selectedIntervention.rationale}
                        </span>
                      </div>

                      {selectedIntervention.priorityExplanation && (
                        <div className="modal-section">
                          <span className="mini-label">
                            AI PRIORITY EXPLANATION
                          </span>
                          <p>{selectedIntervention.priorityExplanation}</p>
                        </div>
                      )}

                      {selectedIntervention.data_warning && (
                        <div className="data-warning modal-warning">
                          <AlertTriangle size={14} />
                          {selectedIntervention.data_warning}
                        </div>
                      )}

                      <div className="modal-divider" />

                      <div className="modal-form-heading">
                        <h3>Supervisor decision</h3>
                        {savedReview && (
                          <span className="saved-indicator">
                            <CheckCircle2 size={13} />
                            Previously saved
                          </span>
                        )}
                      </div>

                      <label className="form-label" htmlFor="reviewer-name">
                        Reviewer name
                      </label>

                      <input
                        id="reviewer-name"
                        className="review-input"
                        value={reviewerName}
                        onChange={(event) => setReviewerName(event.target.value)}
                        placeholder="Enter supervisor name"
                        maxLength={80}
                      />

                      <label className="form-label" htmlFor="review-status">
                        Review decision
                      </label>

                      <select
                        id="review-status"
                        className="review-input"
                        value={reviewStatus}
                        onChange={(event) => setReviewStatus(event.target.value)}
                      >
                        <option value="reviewed">Reviewed</option>
                        <option value="requires_follow_up">
                          Requires follow-up
                        </option>
                      </select>

                      <label className="form-label" htmlFor="review-comment">
                        Review comment
                      </label>

                      <textarea
                        id="review-comment"
                        className="review-input review-textarea"
                        value={reviewComment}
                        onChange={(event) => setReviewComment(event.target.value)}
                        placeholder="Add observations or follow-up notes..."
                        maxLength={1000}
                        rows={4}
                      />

                      {savedReview && (
                        <p className="previous-review">
                          Last reviewed by {savedReview.reviewer_name} on{" "}
                          {formatDate(savedReview.reviewed_at)}.
                        </p>
                      )}

                      {reviewError && (
                        <div className="review-error">
                          <AlertCircle size={14} />
                          {reviewError}
                        </div>
                      )}

                      <div className="modal-actions">
                        <button
                          className="secondary-button"
                          onClick={() => setSelectedIntervention(null)}
                        >
                          Cancel
                        </button>

                        <button
                          className="primary-button"
                          onClick={submitReview}
                          disabled={savingReview}
                        >
                          {savingReview ? "Saving..." : "Save review"}
                        </button>
                      </div>
                    </>
                  );
                })()}
              </section>
            </div>
          )}

          <footer className="page-footer">
            <div>
              <span className="footer-mark">
                <Activity size={15} />
              </span>
              <strong>SitePulse AI</strong>
              <span>Independent prototype · Version 0.1</span>
            </div>
            <span>
              Demonstration data only. Not an operational safety system.
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function StatCard({ label, value, detail, icon, tone }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <span className={`stat-icon ${tone}`}>{icon}</span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-detail">{detail}</div>
    </article>
  );
}

export default App;