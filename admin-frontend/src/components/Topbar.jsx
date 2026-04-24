import { useState, useEffect, useRef } from "react"
import { Sun, Moon, User, LogOut } from "lucide-react"
import { toast } from "react-toastify"
import { useNavigate } from "react-router-dom"

export default function Topbar() {
  const [dark, setDark] = useState(true)
  const [open, setOpen] = useState(false)
  const dropdownRef = useRef()
  const navigate = useNavigate()

  useEffect(() => {
    document.body.classList.toggle("light", !dark)
  }, [dark])

  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  const logout = () => {
    localStorage.clear()
    toast.success("Logged out")
    navigate("/")
  }

  const iconBtn = {
    background: "rgba(14, 26, 56, 0.9)",
    border: "1px solid rgba(0,195,255,0.25)",
    cursor: "pointer",
    color: "#F5F7FA",
    padding: "8px",
    borderRadius: "10px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  }

  return (
    <div
      style={{
        height: "70px",
        padding: "0 20px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",

        // 🔥 GLASS BAR
        background: "rgba(7, 18, 43, 0.9)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",

        borderRadius: "16px",
        border: "1px solid rgba(0,195,255,0.35)",

        boxShadow: "0 0 25px rgba(0,195,255,0.25)"
      }}
    >
      {/* LEFT */}
      <h3
        style={{
          margin: 0,
          fontWeight: "700",
          letterSpacing: "0.4px"
        }}
      >
        Admin Panel
      </h3>

      {/* RIGHT */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>

        {/* THEME */}
        <button style={iconBtn} onClick={() => setDark(!dark)}>
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* PROFILE */}
        <div style={{ position: "relative" }} ref={dropdownRef}>
          <button style={iconBtn} onClick={() => setOpen(!open)}>
            <User size={18} />
          </button>

          {open && (
            <div
              style={{
                position: "absolute",
                right: 0,
                top: "45px",
                width: "170px",
                padding: "14px",

                // 🔥 DROPDOWN GLASS
                background: "rgba(9, 20, 45, 0.95)",
                backdropFilter: "blur(18px)",
                WebkitBackdropFilter: "blur(18px)",

                borderRadius: "14px",
                border: "1px solid rgba(0,195,255,0.25)",
                boxShadow: "0 0 20px rgba(0,195,255,0.2)"
              }}
            >
              <p
                style={{
                  marginBottom: "12px",
                  fontSize: "14px",
                  opacity: 0.85
                }}
              >
                Admin
              </p>

              <button
                onClick={logout}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",

                  border: "none",
                  cursor: "pointer",

                  padding: "10px",
                  borderRadius: "10px",

                  color: "#fff",

                  // 🔥 KEEP RED BUT POLISHED
                  background: "linear-gradient(135deg, #ef4444, #b91c1c)",

                  boxShadow: "0 0 10px rgba(239,68,68,0.4)"
                }}
              >
                <LogOut size={14} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}