import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import Users from "./pages/Users"
import Files from "./pages/Files"
import Patient from "./pages/Patient"

import Sidebar from "./components/Sidebar"
import Topbar from "./components/Topbar"

// 🔥 GLOBAL THEME WRAPPER
function Layout({ children }) {
  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, #0AA1DD, #0C4B8E, #000000)",
        color: "#F5F7FA",
      }}
    >
      {/* SIDEBAR */}
      <Sidebar />

      {/* MAIN */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* TOPBAR */}
        <div
          style={{
            padding: "16px 20px 0 20px",
          }}
        >
          <Topbar />
        </div>

        {/* PAGE CONTENT */}
        <div
          style={{
            padding: "20px",
            flex: 1,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  )
}

// 🔐 AUTH GUARD
function PrivateRoute({ children }) {
  const token = localStorage.getItem("token")
  return token ? children : <Navigate to="/" />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* LOGIN */}
        <Route path="/" element={<Login />} />

        {/* DASHBOARD */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* USERS */}
        <Route
          path="/users"
          element={
            <PrivateRoute>
              <Layout>
                <Users />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* FILES */}
        <Route
          path="/files"
          element={
            <PrivateRoute>
              <Layout>
                <Files />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* PATIENT */}
        <Route
          path="/patient"
          element={
            <PrivateRoute>
              <Layout>
                <Patient />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* FALLBACK */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}