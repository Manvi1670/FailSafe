import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children, roleRequired }) {
  const { user, token } = useAuth()

   if (roleRequired && user.role?.toLowerCase() !== roleRequired.toLowerCase()) {
  return <Navigate to="/dashboard" replace />
}
  if (!token || !user) {
    return <Navigate to="/login" replace />
  }
  
  return children
}