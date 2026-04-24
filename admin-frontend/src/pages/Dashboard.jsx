import { useEffect, useState } from "react"
import API from "../api/axios"

import {
  PieChart, Pie, Cell, Tooltip,
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  BarChart, Bar
} from "recharts"

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload

    return (
      <div style={{
        background: "#0f172a",
        border: "1px solid #1e3a8a",
        padding: "8px",
        borderRadius: "6px",
        fontSize: "12px",
        color: "white"
      }}>
        <div><strong>Disease:</strong> {data.disease}</div>
        <div><strong>Confidence:</strong> {data.confidence}%</div>
      </div>
    )
  }

  return null
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [activity, setActivity] = useState([])
  const [activeUsers, setActiveUsers] = useState([])
  const [trendMode, setTrendMode] = useState("daily")
  const [searchPatient, setSearchPatient] = useState("")

  useEffect(() => { fetchAll() }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      API.post("/auth/heartbeat")
    }, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchAll = async () => {
    try {
      const statsRes = await API.get("/admin/stats")
      setStats(statsRes.data)
    } catch (err) {
      console.error("Stats failed", err)
      setStats({})
    }

    try {
      const activityRes = await API.get(
        `/admin/activity${searchPatient ? `?patient_id=${searchPatient}` : ""}`
      )
      setActivity(activityRes.data.data || [])
    } catch (err) {
      console.error("Activity failed", err)
      setActivity([])
    }

    try {
      const activeRes = await API.get("/admin/active-users")

      console.log("ACTIVE USERS RESPONSE:", activeRes.data)

      if (Array.isArray(activeRes.data)) {
        setActiveUsers(activeRes.data)
      } else if (Array.isArray(activeRes.data.data)) {
        setActiveUsers(activeRes.data.data)
      } else {
        setActiveUsers([])
      }
    } catch (err) {
      console.error("Active users failed", err)
      setActiveUsers([])
    }
  }

  useEffect(() => {
    fetchAll()
  }, [searchPatient])

  if (stats === null) return <p>Loading...</p>

  const diseaseData = Object.values(
    activity.reduce((acc, a) => {
      const disease = a.prediction || "unknown"
      acc[disease] = acc[disease] || { name: disease, value: 0 }
      acc[disease].value++
      return acc
    }, {})
  )

  const trendMap = {}
  activity.forEach(a => {
    const date = new Date(a.time)
    let key

    if (trendMode === "weekly") {
      const firstDay = new Date(date.setDate(date.getDate() - date.getDay()))
      key = firstDay.toLocaleDateString()
    } else {
      key = date.toLocaleDateString()
    }

    trendMap[key] = (trendMap[key] || 0) + 1
  })

  const trendData = Object.keys(trendMap).map(date => ({
    time: date,
    scans: trendMap[date]
  }))

  const filteredActivity = searchPatient
    ? activity.filter(a => String(a.patient_id) === searchPatient)
    : activity

  const confidenceData = filteredActivity.map(a => ({
    time: new Date(a.time).toLocaleTimeString(),
    confidence: Math.round((a.confidence || 0) * 100),
    disease: a.prediction
  }))

  const confidenceDataLimited = confidenceData.slice(-10)

  const buckets = {
    "0-20": 0,
    "20-40": 0,
    "40-60": 0,
    "60-80": 0,
    "80-100": 0
  }

  activity.forEach(a => {
    const c = (a.confidence || 0) * 100

    if (c <= 20) buckets["0-20"]++
    else if (c <= 40) buckets["20-40"]++
    else if (c <= 60) buckets["40-60"]++
    else if (c <= 80) buckets["60-80"]++
    else buckets["80-100"]++
  })

  const confidenceDistribution = Object.keys(buckets).map(key => ({
    range: key,
    count: buckets[key]
  }))

  const COLORS = ["#00C3FF", "#004F9E", "#22c55e", "#ef4444"]

  return (
    <div className="page fade-in">
      <h1 style={{ marginBottom: "20px" }}>Admin Dashboard</h1>

      <div className="grid4">
        <Card title="Users" value={stats.total_users} />
        <Card title="Scans" value={stats.total_scans} />
        <Card
          title="Active Users"
          value={new Set(activeUsers.map(u => u.user_id)).size}
        />
        <Card title="Activity" value={activity.length} />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => setTrendMode("daily")} className="btn-primary">
          Daily
        </button>
        <button onClick={() => setTrendMode("weekly")} className="btn-primary" style={{ marginLeft: "10px" }}>
          Weekly
        </button>
      </div>

      <div className="grid2">
        <div className="glass card">
          <h3>Disease Distribution</h3>
          <PieChart width={250} height={250}>
            <Pie data={diseaseData} dataKey="value" outerRadius={80}>
              {diseaseData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>

        <div className="glass card">
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "10px"
          }}>
            <h3>Model Confidence</h3>

            <input
              type="text"
              placeholder="Patient ID"
              value={searchPatient}
              onChange={(e) => setSearchPatient(e.target.value)}
              style={{
                width: "180px",
                padding: "6px 10px",
                borderRadius: "6px",
                border: "1px solid #1e3a8a",
                background: "#0f172a",
                color: "white",
                fontSize: "12px"
              }}
            />
          </div>

          <LineChart width={400} height={250} data={confidenceDataLimited}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="confidence"
              stroke="#22c55e"
              dot={{ r: 3 }}
            />
          </LineChart>
        </div>
      </div>

      <div className="grid2">
        <div className="glass card">
          <h3>Confidence Distribution</h3>
          <BarChart data={confidenceDistribution} width={400} height={250}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />

            <XAxis
              dataKey="range"
              stroke="#94a3b8"
              label={{ value: "Confidence Range (%)", position: "insideBottom", offset: -5 }}
            />

            <YAxis
              stroke="#94a3b8"
              label={{ value: "Number of Predictions", angle: -90, position: "insideLeft" }}
            />

            <Tooltip formatter={(value) => `${value} predictions`} />

            <Bar dataKey="count" fill="#22c55e" />
          </BarChart>
        </div>

        <div className="glass card">
          <h3>Recent Activity</h3>
          {activity.map(a => (
            <div key={a.id} className="row">
              <div>
                <strong>Patient {a.patient_id}</strong>
                <p style={{ fontSize: "12px" }}>
                  {new Date(a.time).toLocaleString()}
                </p>
              </div>
              <span className="badge">{a.prediction}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid2">
        <div className="glass card">
          <h3>Active Users</h3>
          {activeUsers.map((u, i) => (
            <div key={i} className="row">
              <div>
                <strong>User {u.user_id}</strong>
                <p style={{ fontSize: "12px" }}>
                  {new Date(u.login_time).toLocaleString()}
                </p>
              </div>
              <span style={{ color: "#22c55e" }}>● Online</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function Card({ title, value }) {
  return (
    <div className="glass card">
      <p>{title}</p>
      <h2>{value}</h2>
    </div>
  )
}