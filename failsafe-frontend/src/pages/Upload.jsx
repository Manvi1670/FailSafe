
import { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/NavBar'
import API from '../api/axios'
import styles from './Upload.module.css'

export default function Upload() {
  const [file, setFile]         = useState(null)
  const [loading, setLoading]   = useState(false)
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef            = useRef(null)

  const handleFileChange = (selectedFile) => {
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile)
      setError('')
      setResult(null)
    } else {
      setError('Please select a valid CSV file.')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const dropped = e.dataTransfer.files[0]
    handleFileChange(dropped)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await API.post('/predict/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(res.data)
    } catch (err) {
      const msg = err.response?.data?.detail
      setError(msg || 'Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <Navbar />

      <div className={styles.content}>
        <h1 className={styles.pageTitle}>Upload Student Data</h1>
        <p className={styles.pageSubtitle}>
          Upload a CSV file to predict risk for all students at once
        </p>

        {/* Upload card */}
        {!result && (
          <div className={styles.uploadCard}>

            {/* Dropzone */}
            <div
              className={`${styles.dropzone} ${isDragOver ? styles.active : ''} ${file ? styles.hasFile : ''}`}
              onClick={() => fileInputRef.current.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
            >
              <div className={styles.dropIcon}>
                {file ? '✅' : '📂'}
              </div>
              <p className={styles.dropTitle}>
                {file ? 'File selected' : 'Click or drag your CSV file here'}
              </p>
              <p className={styles.dropSubtitle}>
                {file ? file.name : 'Supports student-mat.csv format'}
              </p>

              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                className={styles.fileInput}
                onChange={(e) => handleFileChange(e.target.files[0])}
              />
            </div>

            {/* File name confirmation */}
            {file && (
              <div className={styles.fileName}>
                📄 {file.name} — {(file.size / 1024).toFixed(1)} KB
              </div>
            )}

            {/* Info box */}
            <div className={styles.infoBox}>
              <strong>Which model will be used?</strong><br />
              If your CSV contains a <strong>G1</strong> column (first period grade),
              the mid-semester model (AUC 0.944) will run automatically.
              Otherwise the early model (AUC 0.742) runs — usable from week one.
            </div>

            {error && (
              <div className="alert alert-error" style={{ marginTop: '16px' }}>
                {error}
              </div>
            )}

            {/* Upload button */}
            <button
              className={styles.uploadBtn}
              onClick={handleUpload}
              disabled={loading || !file}
            >
              {loading ? 'Processing students...' : 'Upload & Predict Risk'}
            </button>

            {/* Progress bar while loading */}
            {loading && (
              <div className={styles.progressBar}>
                <div className={styles.progressFill} />
              </div>
            )}

          </div>
        )}

        {/* Result card */}
        {result && (
          <div className={styles.resultCard}>
            <h2 className={styles.resultTitle}>
              ✅ {result.message}
            </h2>

            <div className={styles.resultGrid}>
              <div className={`${styles.resultStat} ${styles.total}`}>
                <div className={styles.val}>{result.total_students}</div>
                <div className={styles.lbl}>Total Students</div>
              </div>
              <div className={`${styles.resultStat} ${styles.high}`}>
                <div className={styles.val}>{result.high_risk}</div>
                <div className={styles.lbl}>High Risk</div>
              </div>
              <div className={`${styles.resultStat} ${styles.medium}`}>
                <div className={styles.val}>{result.medium_risk}</div>
                <div className={styles.lbl}>Medium Risk</div>
              </div>
              <div className={`${styles.resultStat} ${styles.low}`}>
                <div className={styles.val}>{result.low_risk}</div>
                <div className={styles.lbl}>Low Risk</div>
              </div>
            </div>

            <p style={{ fontSize: '0.82rem', color: '#6b7280', marginBottom: '16px' }}>
              Checkpoint used: <strong>{result.checkpoint_used === 'mid_semester' ? 'Mid-Semester (G1 detected)' : 'Early (no grades)'}</strong>
            </p>

            <Link to="/dashboard" className={styles.dashboardBtn}>
              View Dashboard →
            </Link>
          </div>
        )}

      </div>
    </div>
  )
}