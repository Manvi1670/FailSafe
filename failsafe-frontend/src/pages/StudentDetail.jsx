import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/NavBar'
import API from '../api/axios'
import styles from './StudentDetail.module.css'

export default function StudentDetail() {
  const { id }                  = useParams()
  const [student, setStudent]   = useState(null)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')

  useEffect(() => {
    fetchStudent()
  }, [id])

  const fetchStudent = async () => {
    try {
      const res = await API.get(`/students/${id}`)
      setStudent(res.data)
    } catch (err) {
      setError('Could not load student details.')
    } finally {
      setLoading(false)
    }
  }

  const updateIntervention = async (interventionId, newStatus) => {
    try {
      await API.patch(`/interventions/${interventionId}`, {
        status: newStatus
      })
      // Refresh student data to reflect the change
      fetchStudent()
    } catch (err) {
      console.error('Failed to update intervention:', err)
    }
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <Navbar />
        <div className={styles.loading}>Loading student details...</div>
      </div>
    )
  }

  if (error || !student) {
    return (
      <div className={styles.page}>
        <Navbar />
        <div className={styles.content}>
          <div className="alert alert-error">{error || 'Student not found'}</div>
          <Link to="/dashboard" className={styles.backBtn}>← Back to Dashboard</Link>
        </div>
      </div>
    )
  }

  // Use the most recent prediction
  const pred = student.predictions?.[0]
  if (!pred) return null

  const riskPct = (pred.risk_probability * 100).toFixed(1)

  // Find max SHAP value for bar scaling
  const maxShap = Math.max(...pred.top_shap_values.map(s => Math.abs(s.shap)))

  return (
    <div className={styles.page}>
      <Navbar />

      <div className={styles.content}>

        {/* Back button */}
        <Link to="/dashboard" className={styles.backBtn}>
          ← Back to Dashboard
        </Link>

        {/* Student header */}
        <div className={styles.studentHeader}>
          <div>
            <h1 className={styles.studentName}>{student.student_name}</h1>
            {student.student_roll && (
              <p className={styles.studentRoll}>Roll: {student.student_roll}</p>
            )}
          </div>
          <div className={styles.riskInfo}>
            <div className={styles.riskProb}>{riskPct}%</div>
            <span className={`${styles.riskBadge} ${styles['badge' + pred.risk_tier]}`}>
              {pred.risk_tier} RISK
            </span>
            <p className={styles.checkpoint}>
              {pred.checkpoint === 'mid_semester' ? 'Mid-Semester Model' : 'Early Model'}
            </p>
          </div>
        </div>

        {/* Summary box */}
        <div className={styles.summaryBox}>
          ⚠️ This student has a <strong>{riskPct}% probability of failure</strong>.
          Primary concern: <strong>{pred.top_risk_drivers?.[0] || 'N/A'}</strong>.
          {pred.risk_tier === 'HIGH'
            ? ' Immediate action required.'
            : pred.risk_tier === 'MEDIUM'
            ? ' Intervention recommended within 2 weeks.'
            : ' Monitor over the next month.'}
        </div>

        {/* SHAP chart + Protective factors */}
        <div className={styles.grid}>

          {/* SHAP explanation */}
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>
              🔍 Why was this student flagged?
            </h2>
            {pred.top_shap_values.map((item, i) => (
              <div key={i} className={styles.shapRow}>
                <div className={styles.shapFeature}>{item.feature}</div>
                <div className={styles.shapBarWrap}>
                  {item.shap >= 0 ? (
                    <div
                      className={styles.shapBarPos}
                      style={{ width: `${(Math.abs(item.shap) / maxShap) * 100}%` }}
                    />
                  ) : (
                    <div
                      className={styles.shapBarNeg}
                      style={{ width: `${(Math.abs(item.shap) / maxShap) * 100}%` }}
                    />
                  )}
                </div>
                <span
                  className={styles.shapVal}
                  style={{ color: item.shap >= 0 ? '#dc2626' : '#16a34a' }}
                >
                  {item.shap > 0 ? '+' : ''}{item.shap.toFixed(3)}
                </span>
              </div>
            ))}
            <div className={styles.shapLegend}>
              <span>
                <span className={styles.dot} style={{ background: '#dc2626' }} />
                Increases risk
              </span>
              <span>
                <span className={styles.dot} style={{ background: '#16a34a' }} />
                Decreases risk
              </span>
            </div>
          </div>

          {/* Protective factors */}
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>
              🛡️ Protective Factors
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#6b7280', marginBottom: '12px' }}>
              These factors are currently reducing this student's risk.
              Preserve and strengthen them.
            </p>
            {pred.interventions
              .filter(iv => iv.status === 'resolved')
              .slice(0, 3)
              .length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: '#9ca3af', textAlign: 'center', padding: '20px' }}>
                No resolved interventions yet.
                Mark interventions as resolved as you act on them.
              </div>
            ) : null}
            {/* Top risk drivers as reference */}
            <div style={{ marginTop: '8px' }}>
              {pred.top_shap_values
                .filter(s => s.shap < 0)
                .slice(0, 4)
                .map((item, i) => (
                  <div key={i} className={styles.protectiveItem}>
                    <span className={styles.protIcon}>✓</span>
                    <div>
                      <strong>{item.feature}</strong>
                      <div style={{ fontSize: '0.72rem', color: '#6b7280' }}>
                        Reducing risk by {Math.abs(item.shap).toFixed(3)}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

        </div>

        {/* Intervention plans */}
        <div className={styles.fullCard}>
          <h2 className={styles.cardTitle}>
            📋 Intervention Plan ({pred.interventions.length} actions)
          </h2>
          {pred.interventions.map((iv) => (
            <div
              key={iv.intervention_id}
              className={`${styles.interventionItem} ${styles[iv.status]}`}
            >
              <div className={styles.interventionTop}>
                <div className={styles.interventionLabel}>
                  #{iv.intervention_id} — {iv.driver_label}
                </div>
                <select
                  className={styles.statusSelect}
                  value={iv.status}
                  onChange={(e) => updateIntervention(iv.intervention_id, e.target.value)}
                  style={{
                    color: iv.status === 'resolved' ? '#15803d'
                         : iv.status === 'in_progress' ? '#b45309'
                         : '#6b7280'
                  }}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
              <p className={styles.interventionAction}>{iv.action_text}</p>
              <div className={styles.referral}>📍 Refer to: {iv.referral}</div>
              <div className={styles.shap}>
                SHAP impact: +{iv.feature} drove risk up
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}