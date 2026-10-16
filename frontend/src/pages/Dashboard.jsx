import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react'

export default function Dashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getDashboard().then((res) => setData(res.data))
  }, [])

  const cards = [
    { label: 'Total Income', value: data?.total_income ?? 0, icon: TrendingUp, color: 'text-green-500' },
    { label: 'Total Expenses', value: data?.total_expenses ?? 0, icon: TrendingDown, color: 'text-red-500' },
    { label: 'Net Cash Flow', value: data?.net_cash_flow ?? 0, icon: DollarSign, color: 'text-indigo-500' },
    { label: 'Categories', value: Object.keys(data?.category_breakdown ?? {}).length, icon: Activity, color: 'text-yellow-500' },
  ]

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Dashboard</h2>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-500">{label}</span>
              <Icon size={18} className={color} />
            </div>
            <p className="text-2xl font-bold text-gray-800">
              {typeof value === 'number' && label !== 'Categories'
                ? `₹${value.toLocaleString()}`
                : value}
            </p>
          </div>
        ))}
      </div>
      <p className="mt-8 text-sm text-gray-400 text-center">
        Charts and category breakdown coming in Phase 3
      </p>
    </div>
  )
}
