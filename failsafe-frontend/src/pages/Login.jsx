import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import API from '../api/axios'
import styles from './Login.module.css'

export default function Login() {
  const { register, handleSubmit, formState: { errors } } = useForm()
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)
  const { login }             = useAuth()
  const navigate              = useNavigate()

const onSubmit = async (data) => {
  setLoading(true)
  setError('')
  try {
    // Step 1: Get token
    const formData = new URLSearchParams()
    formData.append('username', data.email)
    formData.append('password', data.password)

    const tokenRes = await API.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    const token = tokenRes.data.access_token
    console.log('Token received:', token)

    // Step 2: Store token FIRST before calling /auth/me
    localStorage.setItem('token', token)

    // Step 3: Get user details
    const userRes = await API.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    })

    console.log('User received:', userRes.data)

    // Step 4: Complete login
    login(userRes.data, token)

    if (userRes.data.role?.toLowerCase() === 'hod') {
    navigate('/hod')
    } else {
  navigate('/dashboard')
    }
  } catch (err) {
    console.error('Login error:', err.response?.data || err.message)
    setError('Incorrect email or password. Please try again.')
    localStorage.removeItem('token')
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

        <h2 className={styles.formTitle}>Sign in to your account</h2>

        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>

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
              placeholder="••••••••"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 6, message: 'Minimum 6 characters' }
              })}
            />
            {errors.password && (
              <span className="error-text">{errors.password.message}</span>
            )}
          </div>

          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>

        </form>

        <p className={styles.registerLink}>
          Don't have an account?{' '}
          <Link to="/register">Register here</Link>
        </p>

      </div>
    </div>
  )
}