import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './NavBar.module.css'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className={styles.navbar}>

      {/* Brand */}
      <Link to="/dashboard" className={styles.brand}>
        <span className={styles.brandIcon}>🛡️</span>
        <span className={styles.brandName}>FAILSAFE</span>
      </Link>

      {/* Nav links */}
      <div className={styles.links}>
        <Link to="/dashboard" className={styles.link}>Dashboard</Link>
        <Link to="/upload"    className={styles.link}>Upload Students</Link>
        {user?.role === 'hod' && (
          <Link to="/hod" className={styles.link}>HOD View</Link>
        )}
      </div>

      {/* User info + logout */}
      <div className={styles.right}>
        <div className={styles.userInfo}>
          <span className={styles.userName}>{user?.full_name}</span>
          <span className={`${styles.roleBadge} ${
            user?.role === 'hod' ? styles.roleHod : styles.roleFaculty
          }`}>
            {user?.role}
          </span>
        </div>
        <button className={styles.logoutBtn} onClick={logout}>
          Sign out
        </button>
      </div>

    </nav>
  )
}