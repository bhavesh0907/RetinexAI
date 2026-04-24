import { useState } from "react"
import API from "../api/axios"

export default function Patient() {
  const [patientId, setPatientId] = useState("")
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(null)
  const [reportUrl, setReportUrl] = useState(null)
  const [previewImage, setPreviewImage] = useState(null)

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

  const getEyeValue = (item) => item?.eye_side || item?.eye || item?.side || "N/A"

  const getEyeBadgeColor = (eye) => {
    const value = (eye || "").toLowerCase()
    if (value === "left") return "#3b82f6"
    if (value === "right") return "#22c55e"
    return "#64748b"
  }

  const searchPatient = async () => {
    if (!patientId) return

    if (!/^\d{1,4}$/.test(patientId)) {
      alert("Patient ID must be max 4 digits")
      return
    }

    setLoading(true)

    try {
      const res = await API.get(`/admin/patient/${patientId}`)
      const payload = res.data?.data || res.data

      const normalized = {
        ...payload,
        records: Array.isArray(payload?.records)
          ? payload.records
          : Array.isArray(payload)
            ? payload
            : []
      }

      setData(normalized)
    } catch (err) {
      const status = err.response?.status
      if (status === 401) alert("Session expired. Login again.")
      else if (status === 403) alert("Admin access required")
      else if (status === 404) alert("Patient not found")
      else alert("Server error")
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async (id) => {
    try {
      setDownloading(id)

      const res = await API.get(`/admin/report/${id}`, {
        responseType: "blob"
      })

      const blob = new Blob([res.data], { type: "application/pdf" })
      const url = window.URL.createObjectURL(blob)

      const link = document.createElement("a")
      link.href = url
      link.download = `report_${id}.pdf`
      link.click()

      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.log(err)
      alert("Download failed")
    } finally {
      setDownloading(null)
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

  return (
    <div style={{ padding: "30px", color: "var(--text)" }}>
      <h2 style={{ marginBottom: "20px" }}>Patient Lookup</h2>

      <div style={{ display: "flex", gap: "10px", marginBottom: "30px" }}>
        <input
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
          placeholder="Enter Patient ID (max 4 digits)"
          style={{
            padding: "10px",
            borderRadius: "8px",
            border: "1px solid var(--border)",
            background: "var(--card)",
            color: "var(--text)",
            width: "250px"
          }}
        />

        <button
          onClick={searchPatient}
          style={{
            padding: "10px 20px",
            borderRadius: "8px",
            background: "#6366f1",
            color: "white",
            border: "none",
            cursor: "pointer"
          }}
        >
          Search
        </button>
      </div>

      {loading && <p>Loading...</p>}

      {!data && !loading && <p>No data</p>}

      {data && (
        <>
          <div
            style={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              padding: "20px",
              borderRadius: "12px",
              marginBottom: "25px"
            }}
          >
            <h3>Patient Info</h3>
            <p><b>ID:</b> {data.patient_id || "N/A"}</p>
            <p><b>Name:</b> {data.name || "N/A"}</p>
            <p><b>Email:</b> {data.email || "N/A"}</p>
            <p><b>Sex:</b> {data.sex || "N/A"}</p>
            <p><b>Age:</b> {data.age || "N/A"}</p>
          </div>

          <h3>Screening Records</h3>

          {Array.isArray(data.records) && data.records.length === 0 ? (
            <p>No history found</p>
          ) : (
            <table
              style={{
                width: "100%",
                marginTop: "20px",
                borderCollapse: "collapse",
                background: "var(--card)",
                borderRadius: "10px",
                overflow: "hidden"
              }}
            >
              <thead style={{ background: "var(--border)" }}>
                <tr>
                  <th style={thStyle}>ID</th>
                  <th style={thStyle}>Filename</th>
                  <th style={thStyle}>Eye</th>
                  <th style={thStyle}>Preview</th>
                  <th style={thStyle}>Disease</th>
                  <th style={thStyle}>Confidence</th>
                  <th style={thStyle}>Date, Time</th>
                  <th style={thStyle}>Report</th>
                </tr>
              </thead>

              <tbody>
                {Array.isArray(data.records) &&
                  data.records.map((item) => {
                    const eyeValue = getEyeValue(item)

                    return (
                      <tr key={item.id}>
                        <td style={tdCenter}>{item.id}</td>
                        <td style={tdLeft}>{item.filename || "N/A"}</td>

                        <td style={tdCenter}>
                          {eyeValue !== "N/A" ? (
                            <span
                              style={{
                                padding: "4px 8px",
                                borderRadius: "6px",
                                background: getEyeBadgeColor(eyeValue),
                                color: "white",
                                display: "inline-block",
                                minWidth: "54px",
                                textTransform: "capitalize"
                              }}
                            >
                              {eyeValue}
                            </span>
                          ) : (
                            "N/A"
                          )}
                        </td>

                        <td style={tdCenter}>
                          <img
                            src={`http://127.0.0.1:8000/uploads/${item.filename}`}
                            width="80"
                            style={{ borderRadius: "6px", cursor: "pointer" }}
                            onClick={() =>
                              setPreviewImage(`http://127.0.0.1:8000/uploads/${item.filename}`)
                            }
                            onError={(e) => {
                              e.target.src = "https://via.placeholder.com/80"
                            }}
                            alt={item.filename || "preview"}
                          />
                        </td>

                        <td style={tdCenter}>{item.prediction || "N/A"}</td>

                        <td style={tdCenter}>
                          {item.confidence
                            ? (item.confidence <= 1
                                ? item.confidence * 100
                                : item.confidence
                              ).toFixed(2) + "%"
                            : "N/A"}
                        </td>

                        <td style={tdCenter}>
                          {item.created_at ? new Date(item.created_at).toLocaleString() : "N/A"}
                        </td>

                        <td style={tdCenter}>
                          <div style={{ display: "flex", justifyContent: "center", gap: "10px" }}>
                            <button
                              onClick={() => viewReport(item.id)}
                              style={{
                                background: "#22c55e",
                                border: "none",
                                padding: "5px 10px",
                                borderRadius: "6px",
                                cursor: "pointer",
                                color: "white"
                              }}
                            >
                              View
                            </button>

                            <button
                              disabled={downloading === item.id}
                              onClick={() => downloadReport(item.id)}
                              style={{
                                background: "#6366f1",
                                border: "none",
                                padding: "5px 10px",
                                borderRadius: "6px",
                                cursor: "pointer",
                                color: "white"
                              }}
                            >
                              {downloading === item.id ? "..." : "Download"}
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
              </tbody>
            </table>
          )}
        </>
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
            alignItems: "center",
            zIndex: 999
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

            <iframe src={reportUrl} width="100%" height="100%" title="Report" />
          </div>
        </div>
      )}

      {previewImage && (
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
            zIndex: 999
          }}
          onClick={() => setPreviewImage(null)}
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
              src={previewImage}
              style={{ maxWidth: "500px", borderRadius: "8px" }}
              alt="preview"
            />

            <div style={{ textAlign: "right", marginTop: "10px" }}>
              <button
                onClick={() => setPreviewImage(null)}
                style={{
                  padding: "6px 12px",
                  border: "none",
                  background: "#6366f1",
                  color: "white",
                  borderRadius: "6px"
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}