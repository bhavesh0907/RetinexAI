import { useEffect, useMemo, useState } from "react"
import API from "../api/axios"

export default function Files() {
  const [files, setFiles] = useState([])
  const [search, setSearch] = useState("")
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [filterDisease, setFilterDisease] = useState("All")
  const [filterDate, setFilterDate] = useState("")
  const [page, setPage] = useState(1)
  const [reportUrl, setReportUrl] = useState(null)
  const perPage = 16

  const diseaseOptions = ["All", "normal", "cataract", "glaucoma", "diabetic_retinopathy"]

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

  const loadFiles = async () => {
    try {
      setLoading(true)
      const res = await API.get(`/admin/files?search=${search}`)
      setFiles(res.data.data || [])
    } catch (err) {
      console.log("Fetch error:", err)
      setFiles([])
    } finally {
      setLoading(false)
    }
  }

  const viewReport = async (id) => {
    try {
      const res = await API.get(`/admin/report/${id}`, {
        responseType: "blob"
      })

      const blob = new Blob([res.data], { type: "application/pdf" })
      const url = window.URL.createObjectURL(blob)

      setReportUrl(url)
    } catch {
      alert("Failed to load report")
    }
  }

  useEffect(() => {
    loadFiles()
  }, [search])

  useEffect(() => {
    setPage(1)
  }, [search, filterDisease, filterDate])

  const filtered = useMemo(() => {
    return files.filter((f) => {
      const matchesSearch = (f.filename || "").toLowerCase().includes(search.toLowerCase())
      const matchesDisease =
        filterDisease === "All" || (f.prediction || "").toLowerCase() === filterDisease.toLowerCase()
      const matchesDate = !filterDate || f.created_at?.startsWith(filterDate)
      return matchesSearch && matchesDisease && matchesDate
    })
  }, [files, search, filterDisease, filterDate])

  const paginated = useMemo(() => {
    return filtered.slice((page - 1) * perPage, page * perPage)
  }, [filtered, page])

  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage))

  return (
    <div style={{ padding: "30px", color: "var(--text)" }}>
      <h2>Files Management</h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "15px", marginTop: "20px" }}>
        <div style={{ display: "flex", gap: "15px", alignItems: "end" }}>
          <input
            placeholder="Search filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid var(--border)",
              background: "var(--card)",
              color: "var(--text)",
              width: "300px"
            }}
          />

          <select
            value={filterDisease}
            onChange={(e) => setFilterDisease(e.target.value)}
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid var(--border)",
              background: "var(--card)",
              color: "var(--text)",
              width: "300px"
            }}
          >
            {diseaseOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid var(--border)",
              background: "var(--card)",
              color: "var(--text)"
            }}
          />
        </div>
      </div>

      {loading && <p>Loading...</p>}

      {!loading && (
        <div
          style={{
            marginTop: "20px",
            background: "var(--card)",
            borderRadius: "12px",
            overflow: "hidden"
          }}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "var(--border)" }}>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Patient ID</th>
                <th style={thStyle}>Patient Name</th>
                <th style={thStyle}>Eye</th>
                <th style={thStyle}>Filename</th>
                <th style={thStyle}>Preview</th>
                <th style={thStyle}>Disease</th>
                <th style={thStyle}>Confidence</th>
                <th style={thStyle}>Action</th>
              </tr>
            </thead>

            <tbody>
              {paginated.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: "center", padding: "20px" }}>
                    No files found
                  </td>
                </tr>
              ) : (
                paginated.map((f, index) => (
                  <tr key={f.id}>
                    <td style={tdCenter}>
                      {(page - 1) * perPage + index + 1}
                    </td>
                    <td style={tdCenter}>{f.patient_id || "N/A"}</td>
                    <td style={tdLeft}>{f.name || "N/A"}</td>
                    <td style={tdCenter}>
                      {f.eye_side ? (
                        <span
                          style={{
                            padding: "4px 8px",
                            borderRadius: "6px",
                            background: f.eye_side.toLowerCase() === "left" ? "#3b82f6" : "#22c55e",
                            color: "white",
                            display: "inline-block",
                            minWidth: "54px"
                          }}
                        >
                          {f.eye_side}
                        </span>
                      ) : (
                        "N/A"
                      )}
                    </td>

                    <td
                      style={{ ...tdLeft, cursor: "pointer", color: "var(--primary)" }}
                      onClick={() => navigator.clipboard.writeText(f.filename)}
                      title="Click to copy"
                    >
                      {f.filename || "N/A"}
                    </td>

                    <td style={tdCenter}>
                      <img
                        src={`http://127.0.0.1:8000/uploads/${f.filename}`}
                        width="60"
                        style={{
                          cursor: "pointer",
                          borderRadius: "6px"
                        }}
                        onClick={() => setPreview(f.filename)}
                        onError={(e) => {
                          e.target.src = "https://via.placeholder.com/60"
                        }}
                        alt={f.filename || "file preview"}
                      />
                    </td>

                    <td style={tdCenter}>{f.prediction || "N/A"}</td>

                    <td style={tdCenter}>
                      {f.confidence
                        ? (f.confidence <= 1 ? f.confidence * 100 : f.confidence).toFixed(2) + "%"
                        : "N/A"}
                    </td>

                    <td style={tdCenter}>
                      <button
                        onClick={() => viewReport(f.id)}
                        style={{
                          background: "#22c55e",
                          border: "none",
                          padding: "6px 12px",
                          borderRadius: "6px",
                          cursor: "pointer",
                          color: "white"
                        }}
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div style={{ marginTop: "15px", padding: "15px", textAlign: "center" }}>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                style={{ padding: "8px 16px", margin: "0 5px", borderRadius: "6px", border: "1px solid var(--border)" }}
              >
                Prev
              </button>
              <span style={{ margin: "0 10px", fontWeight: "bold" }}>
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                style={{ padding: "8px 16px", margin: "0 5px", borderRadius: "6px", border: "1px solid var(--border)" }}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}

      {preview && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.8)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1000
          }}
          onClick={() => setPreview(null)}
        >
          <div
            style={{
              background: "#111",
              padding: "20px",
              borderRadius: "10px"
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={`http://127.0.0.1:8000/uploads/${preview}`}
              style={{ maxWidth: "100%" }}
              alt="preview"
            />

            <button
              onClick={() => setPreview(null)}
              style={{
                marginTop: "10px",
                padding: "6px 12px",
                borderRadius: "6px",
                border: "none",
                background: "#6366f1",
                color: "white",
                cursor: "pointer"
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {reportUrl && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.8)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center"
          }}
        >
          <div
            style={{
              width: "80%",
              height: "80%",
              background: "white",
              borderRadius: "10px",
              overflow: "hidden"
            }}
          >
            <button
              onClick={() => setReportUrl(null)}
              style={{
                float: "right",
                padding: "10px",
                border: "none",
                background: "red",
                color: "white"
              }}
            >
              Close
            </button>

            <iframe
              src={reportUrl}
              width="100%"
              height="100%"
              title="Report"
            />
          </div>
        </div>
      )}
    </div>
  )
}