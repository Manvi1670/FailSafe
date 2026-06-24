import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import API from '../api/axios'
import styles from './HodDashboard.module.css'

export default function HodDashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSummary()
  }, [])

  const fetchSummary = async () => {
    try {
      const res = await API.get('/dashboard/hod')
      setSummary(res.data)
    } catch (err) {
      console.error('Failed to fetch HOD summary:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <Navbar />
        <div className={styles.loading}>Loading school-wide data...</div>
      </div>
    )
  }

  if (!summary) return null

  const atRiskPct   = summary.total_students > 0
    ? ((summary.at_risk_count / summary.total_students) * 100).toFixed(1)
    : 0
  const highPct     = summary.total_students > 0
    ? ((summary.high_risk_count / summary.total_students) * 100).toFixed(1)
    : 0
  const mediumPct   = summary.total_students > 0
    ? ((summary.medium_risk_count / summary.total_students) * 100).toFixed(1)
    : 0
  const lowPct      = summary.total_students > 0
    ? ((summary.low_risk_count / summary.total_students) * 100).toFixed(1)
    : 0

  // CSS conic-gradient for donut chart
  const donutStyle = {
    background: `conic-gradient(
      #dc2626 0% ${highPct}%,
      #d97706 ${highPct}% ${(parseFloat(highPct) + parseFloat(mediumPct)).toFixed(1)}%,
      #16a34a ${(parseFloat(highPct) + parseFloat(mediumPct)).toFixed(1)}% ${(parseFloat(highPct) + parseFloat(mediumPct) + parseFloat(lowPct)).toFixed(1)}%,
      #e5e7eb ${(parseFloat(highPct) + parseFloat(mediumPct) + parseFloat(lowPct)).toFixed(1)}% 100%
    )`,
    WebkitMask: 'radial-gradient(farthest-side, transparent 55%, black 55%)',
    mask: 'radial-gradient(farthest-side, transparent 55%, black 55%)'
  }

  return (
    <div className={styles.page}>
      <Navbar />

      <div className={styles.content}>

        {/* Header */}
        <div className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>
            HOD Dashboard
            <span className={styles.hodBadge}>School-wide view</span>
          </h1>
          <p className={styles.pageSubtitle}>
            Overview of student risk across all faculty uploads
          </p>
        </div>

        {/* Stats grid */}
        <div className={styles.statsGrid}>
          <div className={`${styles.statCard} ${styles.total}`}>
            <div className={styles.statValue}>{summary.total_students}</div>
            <div className={styles.statLabel}>Total Students</div>
          </div>
          <div className={`${styles.statCard} ${styles.atrisk}`}>
            <div className={styles.statValue}>{summary.at_risk_count}</div>
            <div className={styles.statLabel}>At Risk ({atRiskPct}%)</div>
          </div>
          <div className={`${styles.statCard} ${styles.high}`}>
            <div className={styles.statValue}>{summary.high_risk_count}</div>
            <div className={styles.statLabel}>High Risk</div>
          </div>
          <div className={`${styles.statCard} ${styles.medium}`}>
            <div className={styles.statValue}>{summary.medium_risk_count}</div>
            <div className={styles.statLabel}>Medium Risk</div>
          </div>
          <div className={`${styles.statCard} ${styles.low}`}>
            <div className={styles.statValue}>{summary.low_risk_count}</div>
            <div className={styles.statLabel}>Low Risk</div>
          </div>
        </div>

        {/* Charts row */}
        <div className={styles.grid}>

          {/* Donut chart */}
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>Risk Distribution</h2>
            <div className={styles.donutWrap}>
              <div className={styles.donut} style={donutStyle} />
              <div className={styles.donutLegend}>
                <div className={styles.legendRow}>
                  <div className={styles.legendDot}
                       style={{ background: '#dc2626' }} />
                  <span className={styles.legendLabel}>High Risk</span>
                  <span className={styles.legendVal}>
                    {summary.high_risk_count} ({highPct}%)
                  </span>
                </div>
                <div className={styles.legendRow}>
                  <div className={styles.legendDot}
                       style={{ background: '#d97706' }} />
                  <span className={styles.legendLabel}>Medium Risk</span>
                  <span className={styles.legendVal}>
                    {summary.medium_risk_count} ({mediumPct}%)
                  </span>
                </div>
                <div className={styles.legendRow}>
                  <div className={styles.legendDot}
                       style={{ background: '#16a34a' }} />
                  <span className={styles.legendLabel}>Low Risk</span>
                  <span className={styles.legendVal}>
                    {summary.low_risk_count} ({lowPct}%)
                  </span>
                </div>
                <div className={styles.legendRow}>
                  <div className={styles.legendDot}
                       style={{ background: '#e5e7eb' }} />
                  <span className={styles.legendLabel}>No prediction</span>
                  <span className={styles.legendVal}>
                    {summary.total_students - summary.at_risk_count - summary.low_risk_count}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Risk breakdown bars */}
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>Risk Breakdown</h2>

            <div className={styles.progressRow}>
              <div className={styles.progressLabel}>
                <span className={styles.progressName}>High Risk</span>
                <span className={styles.progressCount}>
                  {summary.high_risk_count} students
                </span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill}
                     style={{ width: `${highPct}%`, background: '#dc2626' }} />
              </div>
            </div>

            <div className={styles.progressRow}>
              <div className={styles.progressLabel}>
                <span className={styles.progressName}>Medium Risk</span>
                <span className={styles.progressCount}>
                  {summary.medium_risk_count} students
                </span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill}
                     style={{ width: `${mediumPct}%`, background: '#d97706' }} />
              </div>
            </div>

            <div className={styles.progressRow}>
              <div className={styles.progressLabel}>
                <span className={styles.progressName}>Low Risk</span>
                <span className={styles.progressCount}>
                  {summary.low_risk_count} students
                </span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill}
                     style={{ width: `${lowPct}%`, background: '#16a34a' }} />
              </div>
            </div>

          </div>
        </div>

        {/* Alert section */}
        <div className={styles.fullCard}>
          <h2 className={styles.cardTitle}>⚠️ Action Required</h2>

          {summary.high_risk_count > 0 && (
            <div className={styles.alertBox}>
              <span className={styles.alertIcon}>🔴</span>
              <div className={styles.alertText}>
                <strong>{summary.high_risk_count} students</strong> are at HIGH risk
                and require immediate intervention. Faculty should be contacted
                to begin academic recovery programmes and counselling referrals.
              </div>
            </div>
          )}

          {summary.medium_risk_count > 0 && (
            <div className={styles.alertBox}
                 style={{ background: '#fffbeb', borderColor: '#fde68a' }}>
              <span className={styles.alertIcon}>🟡</span>
              <div className={styles.alertText}
                   style={{ color: '#92400e' }}>
                <strong>{summary.medium_risk_count} students</strong> are at MEDIUM
                risk. Interventions should be initiated within the next 2 weeks to
                prevent escalation to high risk.
              </div>
            </div>
          )}

          {summary.high_risk_count === 0 && summary.medium_risk_count === 0 && (
            <div className={styles.alertBox}
                 style={{ background: '#f0fdf4', borderColor: '#86efac' }}>
              <span className={styles.alertIcon}>✅</span>
              <div className={styles.alertText} style={{ color: '#14532d' }}>
                No high or medium risk students detected. Continue monitoring.
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}