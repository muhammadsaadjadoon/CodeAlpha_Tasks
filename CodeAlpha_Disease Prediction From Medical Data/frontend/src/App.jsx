import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import { SessionProvider } from './context/SessionContext.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import AppShell from './components/AppShell.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Overview from './pages/Overview.jsx'
import Assessment from './pages/Assessment.jsx'
import Result from './pages/Result.jsx'
import Cases from './pages/Cases.jsx'
import ModelCenter from './pages/ModelCenter.jsx'
import DatasetLab from './pages/DatasetLab.jsx'
import ClinicalGuide from './pages/ClinicalGuide.jsx'
import Reports from './pages/Reports.jsx'
import SystemHealth from './pages/SystemHealth.jsx'
import Profile from './pages/Profile.jsx'
import Settings from './pages/Settings.jsx'

export default function App() {
  return (
    <AuthProvider>
      <SessionProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<Register />} />
          <Route path="/app" element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
            <Route index element={<Overview />} />
            <Route path="assessment" element={<Assessment />} />
            <Route path="assessment/result" element={<Result />} />
            <Route path="cases" element={<Cases />} />
            <Route path="models" element={<ModelCenter />} />
            <Route path="dataset" element={<DatasetLab />} />
            <Route path="guide" element={<ClinicalGuide />} />
            <Route path="reports" element={<Reports />} />
            <Route path="system" element={<SystemHealth />} />
            <Route path="profile" element={<Profile />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="/" element={<Navigate to="/app" replace />} />
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </SessionProvider>
    </AuthProvider>
  )
}
