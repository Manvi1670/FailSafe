// ============================================================
// App.jsx — Route definitions
// ============================================================
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

import Login        from './pages/Login'
import Register     from './pages/Register'
import Dashboard    from './pages/Dashboard'
import Upload       from './pages/Upload'
import StudentDetail from './pages/StudentDetail'
import HodDashboard from './pages/HodDashboard'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes — require login */}
        <Route path="/dashboard" element={
          <ProtectedRoute><Dashboard /></ProtectedRoute>
        }/>
        <Route path="/upload" element={
          <ProtectedRoute><Upload /></ProtectedRoute>
        }/>
        <Route path="/students/:id" element={
          <ProtectedRoute><StudentDetail /></ProtectedRoute>
        }/>
        <Route path="/hod" element={
        <ProtectedRoute roleRequired="hod"><HodDashboard /></ProtectedRoute>
        }/>

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AuthProvider>
  )
}