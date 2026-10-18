import { useState, useEffect } from 'react'
import { getInvoices, createInvoice, updateInvoice, deleteInvoice } from '../api'
import { Plus, CheckCircle, Trash2, AlertCircle, Loader2 } from 'lucide-react'

const STATUS_STYLES = {
  paid:    'bg-green-50 text-green-700',
  unpaid:  'bg-yellow-50 text-yellow-700',
  overdue: 'bg-red-50 text-red-700',
}

const emptyForm = {
  invoice_number: '', client: '', amount: '',
  currency: 'INR', issue_date: '', due_date: '', status: 'unpaid',
}

export default function Invoices() {
  const [invoices, setInvoices] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { load() }, [])

  async function load() {
    const { data } = await getInvoices()
    setInvoices(data.invoices)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await createInvoice({ ...form, amount: parseFloat(form.amount) })
      setForm(emptyForm)
      setShowForm(false)
      await load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create invoice.')
    } finally {
      setSaving(false)
    }
  }

  async function markPaid(id) {
    await updateInvoice(id, { status: 'paid' })
    await load()
  }

  async function handleDelete(id) {
    if (!confirm('Delete this invoice?')) return
    await deleteInvoice(id)
    await load()
  }

  const overdue = invoices.filter((i) => i.status === 'overdue')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Invoice Tracker</h2>
          <p className="text-sm text-gray-500 mt-1">Track paid, unpaid, and overdue invoices.</p>
        </div>
        <button
          onClick={() => { setShowForm((v) => !v); setError('') }}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
        >
          <Plus size={15} /> New Invoice
        </button>
      </div>

      {/* Overdue alert */}
      {overdue.length > 0 && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
          <AlertCircle size={16} />
          {overdue.length} invoice{overdue.length > 1 ? 's are' : ' is'} overdue.
        </div>
      )}

      {/* Add invoice form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h3 className="font-medium text-gray-800">New Invoice</h3>
          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
          )}
          <div className="grid grid-cols-2 gap-4">
            <Field label="Invoice #" required>
              <input className={inp} value={form.invoice_number} onChange={(e) => setForm({ ...form, invoice_number: e.target.value })} required />
            </Field>
            <Field label="Client" required>
              <input className={inp} value={form.client} onChange={(e) => setForm({ ...form, client: e.target.value })} required />
            </Field>
            <Field label="Amount" required>
              <input type="number" step="0.01" min="0.01" className={inp} value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            </Field>
            <Field label="Currency">
              <input className={inp} value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} />
            </Field>
            <Field label="Issue Date" required>
              <input type="date" className={inp} value={form.issue_date} onChange={(e) => setForm({ ...form, issue_date: e.target.value })} required />
            </Field>
            <Field label="Due Date" required>
              <input type="date" className={inp} value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} required />
            </Field>
          </div>
          <div className="flex gap-3 pt-1">
            <button type="submit" disabled={saving} className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
              {saving && <Loader2 size={14} className="animate-spin" />} Save Invoice
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="px-5 py-2 rounded-lg text-sm border border-gray-200 text-gray-600 hover:bg-gray-50">
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Invoice table */}
      {invoices.length === 0
        ? (
          <div className="bg-white rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
            <p className="text-gray-400 text-sm">No invoices yet. Click "New Invoice" to add one.</p>
          </div>
        )
        : (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  {['Invoice #', 'Client', 'Amount', 'Issue Date', 'Due Date', 'Status', ''].map((h) => (
                    <th key={h} className="px-4 py-3 text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {invoices.map((inv) => (
                  <tr key={inv.id} className={`hover:bg-gray-50 ${inv.status === 'overdue' ? 'bg-red-50/30' : ''}`}>
                    <td className="px-4 py-3 font-medium text-gray-800">{inv.invoice_number}</td>
                    <td className="px-4 py-3 text-gray-700">{inv.client}</td>
                    <td className="px-4 py-3 text-gray-800 font-medium">₹{Number(inv.amount).toLocaleString()}</td>
                    <td className="px-4 py-3 text-gray-500">{inv.issue_date}</td>
                    <td className="px-4 py-3 text-gray-500">{inv.due_date}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_STYLES[inv.status]}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {inv.status !== 'paid' && (
                          <button onClick={() => markPaid(inv.id)} title="Mark as paid" className="text-green-600 hover:text-green-700">
                            <CheckCircle size={16} />
                          </button>
                        )}
                        <button onClick={() => handleDelete(inv.id)} title="Delete" className="text-gray-400 hover:text-red-500">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </div>
  )
}

function Field({ label, required, children }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-600">{label}{required && ' *'}</label>
      {children}
    </div>
  )
}

const inp = 'border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 w-full'
