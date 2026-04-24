export default function StatCard({ title, value }) {
  return (
    <div className="glass card card-hover" style={{ textAlign: "center" }}>
      <p style={{ opacity: 0.7 }}>{title}</p>
      <h2 style={{ fontSize: "28px", fontWeight: "700" }}>{value}</h2>
    </div>
  )
}