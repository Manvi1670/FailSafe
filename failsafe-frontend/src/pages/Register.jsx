import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import API from '../api/axios'
import styles from './Register.module.css'

export default function Register() {
  const { register, handleSubmit, formState: { errors } } = useForm()
  const [error, setError]     = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate              = useNavigate()

  const onSubmit = async (data) => {
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      await API.post('/auth/register', {
        email    : data.email,
        password : data.password,
        full_name: data.full_name,
        role     : data.role
      })
      setSuccess('Account created! Redirecting to login...')
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      const msg = err.response?.data?.detail
      setError(msg || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>

        <div className={styles.header}>
          <div className={styles.logo}>🛡️</div>
          <h1 className={styles.title}>FAILSAFE</h1>
          <p className={styles.subtitle}>Student Risk Prediction System</p>
        </div>

        <h2 className={styles.formTitle}>Create your account</h2>

        {error   && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit(onSubmit)}>

          <div className="form-group">
            <label>Full name</label>
            <input
              type="text"
              placeholder="Dr. Ramesh Kumar"
              {...register('full_name', {
                required: 'Full name is required',
                minLength: { value: 3, message: 'At least 3 characters' }
              })}
            />
            {errors.full_name && (
              <span className="error-text">{errors.full_name.message}</span>
            )}
          </div>

          <div className="form-group">
            <label>Email address</label>
            <input
              type="email"
              placeholder="you@school.edu"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^\S+@\S+\.\S+$/,
                  message: 'Enter a valid email'
                }
              })}
            />
            {errors.email && (
              <span className="error-text">{errors.email.message}</span>
            )}
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Minimum 6 characters"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 6, message: 'Minimum 6 characters' }
              })}
            />
            {errors.password && (
              <span className="error-text">{errors.password.message}</span>
            )}
          </div>

          <div className="form-group">
            <label>Role</label>
            <select {...register('role', { required: 'Please select a role' })}>
              <option value="faculty">Faculty</option>
              <option value="hod">Head of Department (HOD)</option>
            </select>
            <p className={styles.roleHint}>
              Faculty can upload students and manage interventions.
              HOD can view school-wide risk trends.
            </p>
            {errors.role && (
              <span className="error-text">{errors.role.message}</span>
            )}
          </div>

          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>

        </form>

        <p className={styles.loginLink}>
          Already have an account?{' '}
          <Link to="/login">Sign in here</Link>
        </p>

      </div>
    </div>
  )
}