import { useState, useEffect } from 'react'
import { uploadReceipt, confirmReceipt, getExpenses } from '../api'
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

const CATEGORIES = ['Software', 'Hardware', 'Travel', 'Food', 'Office Supplies', 'Marketing', 'Other']

const emptyForm = {
  merchant: '', date: '', amount: '', currency: 'INR',
  category: 'Other', tax: '', receipt_path: '', review_status: 'needs_review',
}

export default function Receipts() {
  const [expenses, setExpenses] = useState([])
  const [form, setForm] = useState(null)       // null = no file uploaded yet
  const [status, setStatus] = useState('idle') // idle | uploading | reviewing | saving | saved | error
  const [error, setError] = useState('')

  useEffect(() => {
    getExpenses().then((r) => setExpenses(r.data.expenses))
  }, [])

  async function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setStatus('uploading')
    setError('')
    try {
      const fd = new FormData()
      fd.append('file', file)
      const { data } = await uploadReceipt(fd)
      setForm({ ...emptyForm, ...data, amount: data.amount ?? '', tax: data.tax ?? '' })
      setStatus('reviewing')
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.')
      setStatus('error')
    }
  }

  async function handleConfirm(e) {
    e.preventDefault()
    setStatus('saving')
    setError('')
    try {
      await confirmReceipt({
        ...form,
        amount: parseFloat(form.amount),
        tax: form.tax !== '' ? parseFloat(form.tax) : null,
      })
      setStatus('saved')
      setForm(null)
      const { data } = await getExpenses()
      setExpenses(data.expenses)
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed.')
      setStatus('error')
    }
  }

  function handleDiscard() {
    setForm(null)
    setStatus('idle')
    setError('')
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Receipts & Expenses</h2>
        <p className="text-sm text-gray-500 mt-1">Upload a receipt — AI extracts the details for you to review.</p>
      </div>

      {/* Upload zone */}
      {!form && (
        <label className={`flex flex-col items-center justify-center gap-3 border-2 border-dashed rounded-xl p-12 cursor-pointer transition-colors ${status === 'uploading' ? 'border-indigo-300 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'}`}>
          {status === 'uploading'
            ? <Loader2 size={32} className="text-indigo-400 animate-spin" />
            : <Upload size={32} className="text-gray-400" />}
          <span className="text-sm text-gray-500">
            {status === 'uploading' ? 'Extracting text and running AI…' : 'Click or drag a receipt (JPG, PNG, PDF)'}
          </span>
          <input type="file" accept=".jpg,.jpeg,.png,.pdf" className="hidden" onChange={handleFileChange} disabled={status === 'uploading'} />
        </label>
      )}

      {/* Status messages */}
      {status === 'saved' && (
        <div className="flex items-center gap-2 text-green-600 text-sm bg-green-50 border border-green-200 rounded-lg px-4 py-3">
          <CheckCircle size={16} /> Expense saved successfully.
        </div>
      )}
      {status === 'error' && (
        <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Review form */}
      {form && (
        <form onSubmit={handleConfirm} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-gray-800">Review Extracted Details</h3>
            <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">Needs Review</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Merchant" required>
              <input className={input} value={form.merchant} onChange={(e) => setForm({ ...form, merchant: e.target.value })} required />
            </Field>
            <Field label="Date" required>
              <input type="date" className={input} value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
            </Field>
            <Field label="Amount" required>
              <input type="number" step="0.01" min="0.01" className={input} value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            </Field>
            <Field label="Currency">
              <input className={input} value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} />
            </Field>
            <Field label="Category">
              <select className={input} value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </Field>
            <Field label="Tax (optional)">
              <input type="number" step="0.01" min="0" className={input} value={form.tax} onChange={(e) => setForm({ ...form, tax: e.target.value })} />
            </Field>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={status === 'saving'} className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
              {status === 'saving' && <Loader2 size={14} className="animate-spin" />}
              Confirm & Save
            </button>
            <button type="button" onClick={handleDiscard} className="px-5 py-2 rounded-lg text-sm border border-gray-200 text-gray-600 hover:bg-gray-50">
              Discard
            </button>
          </div>
        </form>
      )}

      {/* Expense table */}
      {expenses.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                {['Merchant', 'Date', 'Amount', 'Category', 'Status'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {expenses.map((e) => (
                <tr key={e.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">{e.merchant}</td>
                  <td className="px-4 py-3 text-gray-500">{e.date}</td>
                  <td className="px-4 py-3 text-gray-800">₹{e.amount.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span className="bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full">{e.category}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${e.review_status === 'confirmed' ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}`}>
                      {e.review_status}
                    </span>
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

const input = 'border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 w-full'
