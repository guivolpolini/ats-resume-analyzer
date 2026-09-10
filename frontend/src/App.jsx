import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === 'healthy' ? 'online' : 'erro'))
      .catch(() => setApiStatus('offline'))
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="max-w-xl text-center">
        <h1 className="text-3xl font-bold text-slate-800">
          ATS Resume Analyzer
        </h1>
        <p className="mt-2 text-slate-500">
          Frontend em construção — React + Vite + Tailwind CSS configurados com sucesso.
        </p>

        <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              apiStatus === 'online'
                ? 'bg-green-500'
                : apiStatus === 'checking'
                ? 'bg-yellow-400'
                : 'bg-red-500'
            }`}
          />
          <span className="text-slate-600">
            API do backend:{' '}
            {apiStatus === 'online' && 'conectada'}
            {apiStatus === 'checking' && 'verificando...'}
            {apiStatus === 'offline' && 'offline (rode o backend)'}
            {apiStatus === 'erro' && 'respondeu com erro'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default App
