import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, AlertCircle } from 'lucide-react'

const PIE_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#8b5cf6', '#ec4899']

export default function Dashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getDashboard().then((r) => setData(r.data))
  }, [])

  const summary = data ?? {
    total_income: 0, total_expenses: 0, net_cash_flow: 0,
    category_breakdown: {}, monthly_trend: [],
    invoice_summary: { total: 0, unpaid: 0, overdue: 0 },
  }

  const cards = [
    { label: 'Total Income', value: summary.total_income, icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-50' },
    { label: 'Total Expenses', value: summary.total_expenses, icon: TrendingDown, color: 'text-red-500', bg: 'bg-red-50' },
    { label: 'Net Cash Flow', value: summary.net_cash_flow, icon: DollarSign, color: summary.net_cash_flow >= 0 ? 'text-indigo-500' : 'text-red-500', bg: 'bg-indigo-50' },
    { label: 'Overdue Invoices', value: summary.invoice_summary.overdue, icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-50', raw: true },
  ]

  const pieData = Object.entries(summary.category_breakdown).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-800">Dashboard</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map(({ label, value, icon: Icon, color, bg, raw }) => (
          <div key={label} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-500">{label}</span>
              <span className={`${bg} p-1.5 rounded-lg`}>
                <Icon size={16} className={color} />
              </span>
            </div>
            <p className={`text-2xl font-bold ${color}`}>
              {raw ? value : `₹${Number(value).toLocaleString()}`}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Monthly trend bar chart */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-medium text-gray-700 mb-4">Monthly Trend</h3>
          {summary.monthly_trend.length === 0
            ? <Empty text="No data yet — confirm some expenses to see trends." />
            : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={summary.monthly_trend} barGap={4}>
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                  <Tooltip formatter={(v) => `₹${Number(v).toLocaleString()}`} />
                  <Legend />
                  <Bar dataKey="income" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="expenses" name="Expenses" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
        </div>

        {/* Category breakdown pie chart */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-medium text-gray-700 mb-4">Expense by Category</h3>
          {pieData.length === 0
            ? <Empty text="No confirmed expenses yet." />
            : (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => `₹${Number(v).toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
            )}
        </div>
      </div>

      {/* Invoice status strip */}
      <div className="bg-white rounded-xl border border-gray-100 p-5 flex gap-6">
        <Stat label="Total Invoices" value={summary.invoice_summary.total} />
        <div className="w-px bg-gray-100" />
        <Stat label="Unpaid" value={summary.invoice_summary.unpaid} color="text-yellow-600" />
        <div className="w-px bg-gray-100" />
        <Stat label="Overdue" value={summary.invoice_summary.overdue} color="text-red-600" />
      </div>
    </div>
  )
}

function Stat({ label, value, color = 'text-gray-800' }) {
  return (
    <div>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  )
}

function Empty({ text }) {
  return (
    <div className="h-[220px] flex items-center justify-center text-sm text-gray-400">{text}</div>
  )
}
