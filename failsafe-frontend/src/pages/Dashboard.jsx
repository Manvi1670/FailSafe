import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Navbar from '../components/NavBar'
import API from '../api/axios'
import styles from './Dashboard.module.css'

export default function Dashboard() {
  const [students, setStudents]   = useState([])
  const [summary, setSummary]     = useState(null)
  const [loading, setLoading]     = useState(true)
  const [riskFilter, setRiskFilter] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchData()
  }, [riskFilter])

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = riskFilter ? `?risk_tier=${riskFilter}` : ''
      const [studentsRes, summaryRes] = await Promise.all([
        API.get(`/students/${params}`),
        API.get('/dashboard/summary')
      ])
      setStudents(studentsRes.data.students || [])
      setSummary(summaryRes.data)
    } catch (err) {
      console.error('Failed to fetch data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (prob) => {
    if (prob >= 0.75) return '#dc2626'
    if (prob >= 0.50) return '#d97706'
    return '#16a34a'
  }

  return (
    <div className={styles.page}>
      <Navbar />

      <div className={styles.content}>

        {/* Page header */}
        <div className={styles.pageHeader}>
          <div>
            <h1 className={styles.pageTitle}>Student Risk Dashboard</h1>
            <p className={styles.pageSubtitle}>
              Monitor at-risk students and track interventions
            </p>
          </div>
          <Link to="/upload" className={styles.uploadBtn}>
            + Upload Students
          </Link>
        </div>

        {/* Stats grid */}
        {summary && (
          <div className={styles.statsGrid}>
            <div className={`${styles.statCard} ${styles.total}`}>
              <div className={styles.statValue}>{summary.total_students}</div>
              <div className={styles.statLabel}>Total Students</div>
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
            <div className={`${styles.statCard} ${styles.pending}`}>
              <div className={styles.statValue}>{summary.interventions_pending}</div>
              <div className={styles.statLabel}>Interventions Pending</div>
            </div>
          </div>
        )}

        {/* Student table */}
        <div className={styles.tableSection}>
          <div className={styles.tableHeader}>
            <h2 className={styles.tableTitle}>All Students</h2>
            <div className={styles.filterGroup}>
              <select
                className={styles.filterSelect}
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
              >
                <option value="">All risk levels</option>
                <option value="HIGH">High risk</option>
                <option value="MEDIUM">Medium risk</option>
                <option value="LOW">Low risk</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className={styles.loading}>Loading students...</div>
          ) : students.length === 0 ? (
            <div className={styles.empty}>
              <h3>No students found</h3>
              <p>Upload a CSV file to start predicting student risk.</p>
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Risk Level</th>
                  <th>Risk Score</th>
                  <th>Top Driver</th>
                  <th>Checkpoint</th>
                  <th>Interventions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.student_id}
                      onClick={() => navigate(`/students/${s.student_id}`)}>
                    <td>
                      <strong>{s.student_name}</strong>
                      {s.student_roll && (
                        <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                          {s.student_roll}
                        </div>
                      )}
                    </td>
                    <td>
                      <span className={`${styles.badge} ${styles['badge' + s.risk_tier]}`}>
                        {s.risk_tier}
                      </span>
                    </td>
                    <td>
                      <div className={styles.riskBar}>
                        <div className={styles.riskBarTrack}>
                          <div
                            className={styles.riskBarFill}
                            style={{
                              width: `${s.risk_probability * 100}%`,
                              background: getRiskColor(s.risk_probability)
                            }}
                          />
                        </div>
                        <span className={styles.riskPct}
                              style={{ color: getRiskColor(s.risk_probability) }}>
                          {(s.risk_probability * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td style={{ color: '#6b7280', fontSize: '0.8rem' }}>
                      {s.top_risk_drivers?.[0] || '—'}
                    </td>
                    <td style={{ fontSize: '0.78rem', color: '#6b7280' }}>
                      {s.checkpoint === 'mid_semester' ? 'Mid-semester' : 'Early'}
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem' }}>
                        {s.interventions_pending} pending /
                        {s.interventions_resolved} resolved
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  )
}