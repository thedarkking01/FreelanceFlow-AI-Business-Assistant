import { useState } from 'react'
import { getMonthlyReport, exportCSV } from '../api'
import { FileText, Download, Loader2, TrendingUp, TrendingDown, DollarSign } from 'lucide-react'

export default function Reports() {
  const [month, setMonth] = useState(() => new Date().toISOString().slice(0, 7))
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)

  async function handleGenerate() {
    setLoading(true)
    setReport(null)
    try {
      const { data } = await getMonthlyReport(month)
      setReport(data)
    } finally {
      setLoading(false)
    }
  }

  async function handleExport() {
    setDownloading(true)
    try {
      const { data } = await exportCSV(month)
      const url = URL.createObjectURL(new Blob([data], { type: 'text/csv' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `freelanceflow_${month}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Monthly Reports</h2>
        <p className="text-sm text-gray-500 mt-1">AI-generated financial summary and CSV export.</p>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        <input
          type="month"
          value={month}
          onChange={(e) => { setMonth(e.target.value); setReport(null) }}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
          {loading ? 'Generating…' : 'Generate Report'}
        </button>
        <button
          onClick={handleExport}
          disabled={downloading}
          className="flex items-center gap-2 border border-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50"
        >
          {downloading ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
          Export CSV
        </button>
      </div>

      {/* Report output */}
      {report && (
        <div className="space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-3 gap-4">
            <StatCard label="Total Income" value={`₹${Number(report.total_income).toLocaleString()}`} icon={TrendingUp} color="text-green-500" bg="bg-green-50" />
            <StatCard label="Total Expenses" value={`₹${Number(report.total_expenses).toLocaleString()}`} icon={TrendingDown} color="text-red-500" bg="bg-red-50" />
            <StatCard
              label="Net Cash Flow"
              value={`₹${Number(report.net).toLocaleString()}`}
              icon={DollarSign}
              color={report.net >= 0 ? 'text-indigo-500' : 'text-red-500'}
              bg="bg-indigo-50"
            />
          </div>

          {/* AI summary */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <FileText size={14} className="text-indigo-500" /> AI Summary
            </h3>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{report.summary}</p>
          </div>

          {/* Top categories */}
          {report.top_categories.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Top Expense Categories</h3>
              <div className="space-y-2">
                {report.top_categories.map(({ category, amount }) => {
                  const pct = report.total_expenses > 0 ? (amount / report.total_expenses) * 100 : 0
                  return (
                    <div key={category}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-700">{category}</span>
                        <span className="text-gray-500">₹{Number(amount).toLocaleString()} ({pct.toFixed(0)}%)</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Overdue notice */}
          {report.overdue_count > 0 && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
              ⚠ {report.overdue_count} overdue invoice{report.overdue_count > 1 ? 's' : ''} — go to the Invoices tab to follow up.
            </div>
          )}

          <p className="text-xs text-gray-400">
            Report covers {report.expense_count} confirmed expense{report.expense_count !== 1 ? 's' : ''} for {report.month}.
            Use "Export CSV" to download the full transaction list.
          </p>
        </div>
      )}

      {!report && !loading && (
        <div className="bg-white rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
          <p className="text-gray-400 text-sm">Select a month and click "Generate Report".</p>
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value, icon: Icon, color, bg }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500">{label}</span>
        <span className={`${bg} p-1.5 rounded-lg`}>
          <Icon size={16} className={color} />
        </span>
      </div>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  )
}
