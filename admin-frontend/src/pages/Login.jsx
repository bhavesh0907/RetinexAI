import { useState } from "react"
import { useNavigate } from "react-router-dom"
import API from "../api/axios"

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const login = async () => {
    if (!email || !password) {
      alert("Enter credentials")
      return
    }

    setLoading(true)

    try {
      const res = await API.post("/auth/login", { email, password })

      localStorage.setItem("token", res.data.access_token)
      localStorage.setItem("role", res.data.role)

      if (res.data.role === "admin") {
        navigate("/dashboard")
      } else {
        alert("Not admin")
      }

    } catch {
      alert("Invalid credentials")
    }

    setLoading(false)
  }

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "radial-gradient(circle at top left, #0AA1DD, #0C4B8E, #000000)"
      }}
    >
      <div
        className="glass"
        style={{
          padding: "40px",
          borderRadius: "18px",
          width: "320px",
          display: "flex",
          flexDirection: "column",
          gap: "15px",
          boxShadow: "0 0 30px rgba(0,195,255,0.3)"
        }}
      >
        <h2 style={{ textAlign: "center" }}>RetinexAI Admin</h2>

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="btn-primary" onClick={login}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </div>
    </div>
  )
}