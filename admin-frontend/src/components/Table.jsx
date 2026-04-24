export default function Table({ columns, data, renderRow }) {
  return (
    <div className="glass card">
      <table>
        <thead>
          <tr>
            {columns.map((col, i) => (
              <th key={i}>{col}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ textAlign: "center", padding: "20px" }}>
                No data found
              </td>
            </tr>
          ) : (
            data.map((row, i) => renderRow(row, i))
          )}
        </tbody>
      </table>
    </div>
  )
}