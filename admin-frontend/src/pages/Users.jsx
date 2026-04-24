import { useEffect, useState } from "react"
import API from "../api/axios"

export default function Users() {
  const [users, setUsers] = useState([])

  const thStyle = {
    textAlign: "center",
    padding: "12px",
    fontWeight: "600"
  }

  const tdCenter = {
    textAlign: "center",
    padding: "12px"
  }

  const tdLeft = {
    textAlign: "left",
    padding: "12px"
  }

  const loadUsers = async () => {
    try {
      const res = await API.get("/admin/users")
      setUsers(res.data)
    } catch {
      setUsers([])
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  return (
    <div className="page">
      <h2>User Management</h2>

      <div className="glass card" style={{ marginTop: "20px" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "var(--border)" }}>
            <tr>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Email</th>
              <th style={thStyle}>Role</th>
              <th style={thStyle}>Status</th>
            </tr>
          </thead>

          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>
                  No users found
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id}>
                  <td style={tdCenter}>{u.id}</td>

                  <td style={tdLeft}>{u.email}</td>

                  <td style={tdCenter}>{u.role}</td>

                  <td style={tdCenter}>
                    <span
                        className="badge"
                        style={{
                          background:
                            u.status === "active"
                              ? "linear-gradient(135deg,#22c55e,#16a34a)"
                              : "linear-gradient(135deg,#ef4444,#dc2626)"
                        }}
                    >
                        {u.status === "active" ? "Active" : "Inactive"}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}