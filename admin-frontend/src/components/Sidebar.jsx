import { NavLink } from "react-router-dom"
import { useState, useEffect } from "react"

import {
  LayoutDashboard,
  Folder,
  Eye,
  Users,
  Menu,
  X
} from "lucide-react"

export default function Sidebar() {

  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  // =========================
  // LINK STYLE (FIXED)
  // =========================
  const linkStyle = ({ isActive }) => ({
    display: "flex",
    alignItems: "center",
    gap: collapsed && !isMobile ? "0px" : "10px",
    padding: "12px",
    borderRadius: "12px",
    marginBottom: "10px",
    textDecoration: "none",
    fontWeight: "500",
    justifyContent:
      collapsed && !isMobile ? "center" : "flex-start",

    color: isActive ? "#ffffff" : "#94a3b8",

    background: isActive
      ? "linear-gradient(135deg, #00C3FF, #004F9E)"
      : "transparent",

    boxShadow: isActive
      ? "0 0 15px rgba(0,195,255,0.6)"
      : "none",

    transition: "all 0.25s ease"
  })

  const labelStyle = {
    display: collapsed && !isMobile ? "none" : "inline"
  }

  const handleNavClick = () => {
    if (isMobile) setMobileOpen(false)
  }

  // =========================
  // SIDEBAR CONTENT (GLASS FIX)
  // =========================
  const sidebarContent = (
    <div
      style={{
        width: isMobile ? "240px" : collapsed ? "80px" : "240px",
        height: "100vh",
        padding: "20px 10px",
        display: "flex",
        flexDirection: "column",

        // 🔥 CRITICAL FIX
        background: "rgba(9, 20, 45, 0.75)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",

        borderRight: "1px solid rgba(0,195,255,0.08)",
        boxShadow: "0 0 30px rgba(0,0,0,0.4)"
      }}
    >

      {/* HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent:
            collapsed && !isMobile ? "center" : "space-between",
          alignItems: "center",
          marginBottom: "30px"
        }}
      >
        {!collapsed || isMobile ? (
          <h2 style={{
            fontWeight: "700",
            letterSpacing: "0.5px"
          }}>
            RetinexAI
          </h2>
        ) : null}

        {!isMobile && (
          <Menu
            size={20}
            onClick={() => setCollapsed(!collapsed)}
            style={{ cursor: "pointer" }}
          />
        )}

        {isMobile && (
          <X
            size={20}
            onClick={() => setMobileOpen(false)}
            style={{ cursor: "pointer" }}
          />
        )}
      </div>

      {/* NAV */}
      <NavLink to="/dashboard" style={linkStyle} onClick={handleNavClick}>
        <LayoutDashboard size={18} />
        <span style={labelStyle}>Dashboard</span>
      </NavLink>

      <NavLink to="/files" style={linkStyle} onClick={handleNavClick}>
        <Folder size={18} />
        <span style={labelStyle}>Files</span>
      </NavLink>

      <NavLink to="/patient" style={linkStyle} onClick={handleNavClick}>
        <Eye size={18} />
        <span style={labelStyle}>Patient</span>
      </NavLink>

      <NavLink to="/users" style={linkStyle} onClick={handleNavClick}>
        <Users size={18} />
        <span style={labelStyle}>Users</span>
      </NavLink>

    </div>
  )

  return (
    <>
      {/* MOBILE MENU BUTTON */}
      {isMobile && (
        <div style={{
          position: "fixed",
          top: 10,
          left: 10,
          zIndex: 1100
        }}>
          <Menu
            size={26}
            onClick={() => setMobileOpen(true)}
            style={{ cursor: "pointer", color: "#fff" }}
          />
        </div>
      )}

      {/* OVERLAY */}
      {isMobile && mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            zIndex: 999
          }}
        />
      )}

      {/* SIDEBAR PANEL */}
      <div
        style={{
          position: isMobile ? "fixed" : "relative",
          left: isMobile ? (mobileOpen ? 0 : -260) : 0,
          zIndex: 1000,
          transition: "0.3s"
        }}
      >
        {sidebarContent}
      </div>
    </>
  )
}