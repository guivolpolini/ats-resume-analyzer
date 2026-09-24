import { useEffect, useState, useRef } from 'react'

const API_URL =
  import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== ''
    ? import.meta.env.VITE_API_URL
    : (import.meta.env.DEV ? 'http://localhost:8000' : '')

function App() {
  const [apiStatus, setApiStatus] = useState('checking') // 'online' | 'offline' | 'checking'
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [isDragging, setIsDragging] = useState(false)

  const fileInputRef = useRef(null)

  // Checagem de saúde da API
  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === 'healthy' ? 'online' : 'offline'))
      .catch(() => setApiStatus('offline'))
  }, [])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    validateAndSetFile(selectedFile)
  }

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return
    const validExtensions = ['pdf', 'docx']
    const ext = selectedFile.name.split('.').pop()?.toLowerCase()

    if (!validExtensions.includes(ext)) {
      setErrorMessage('Por favor, selecione um arquivo válido em formato PDF (.pdf) ou Word (.docx).')
      return
    }

    setErrorMessage('')
    setFile(selectedFile)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files?.[0]
    validateAndSetFile(droppedFile)
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!file) {
      setErrorMessage('Envie seu currículo em PDF ou DOCX antes de analisar.')
      return
    }
    if (!jobDescription.trim() || jobDescription.trim().length < 20) {
      setErrorMessage('Cole uma descrição de vaga com pelo menos 20 caracteres.')
      return
    }

    setErrorMessage('')
    setIsLoading(true)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('job_description', jobDescription)

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ocorreu um erro ao processar a análise.')
      }

      setAnalysisResult(data)
      // Rolagem suave para os resultados
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (err) {
      setErrorMessage(err.message || 'Erro ao conectar com o servidor.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadPdf = async () => {
    if (!analysisResult?.optimized_resume) return

    setIsDownloading(true)
    try {
      const response = await fetch(`${API_URL}/api/generate-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          optimized_resume: analysisResult.optimized_resume,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Falha ao gerar arquivo PDF.')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url

      const candidateName = analysisResult.optimized_resume.full_name || 'candidato'
      const cleanName = candidateName.toLowerCase().replace(/[^a-z0-9]/g, '_')
      a.download = `curriculo_otimizado_${cleanName}.pdf`

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setErrorMessage(err.message || 'Erro ao baixar o currículo em PDF.')
    } finally {
      setIsDownloading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setJobDescription('')
    setAnalysisResult(null)
    setErrorMessage('')
    if (fileInputRef.current) fileInputRef.current.value = ''
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-emerald-600 bg-emerald-50 border-emerald-200'
    if (score >= 50) return 'text-amber-600 bg-amber-50 border-amber-200'
    return 'text-rose-600 bg-rose-50 border-rose-200'
  }

  const getScoreBadgeText = (score) => {
    if (score >= 75) return 'Excelente aderência ATS'
    if (score >= 50) return 'Aderência moderada'
    return 'Baixa aderência inicial'
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased flex flex-col font-sans">
      {/* Barra superior de navegação */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-sm">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <span className="font-semibold text-slate-900 tracking-tight text-base sm:text-lg">
                ATS Resume Analyzer
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs px-2 py-0.5 font-medium rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
                Google Gemini
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border border-slate-200 bg-slate-50">
              <span
                className={`h-2 w-2 rounded-full ${
                  apiStatus === 'online'
                    ? 'bg-emerald-500'
                    : apiStatus === 'checking'
                    ? 'bg-amber-400 animate-pulse'
                    : 'bg-rose-500'
                }`}
              />
              <span className="text-slate-600">
                API {apiStatus === 'online' ? 'Online' : apiStatus === 'checking' ? 'Conectando...' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Hero */}
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Otimize seu currículo para sistemas <span className="text-indigo-600">ATS</span>
          </h1>
          <p className="mt-3 text-slate-600 text-sm sm:text-base leading-relaxed">
            Faça upload do seu currículo em PDF ou DOCX, cole os requisitos da vaga e receba um diagnóstico detalhado com pontuação ATS, análise de lacunas e uma versão otimizada para download.
          </p>

          <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200/70 text-amber-800 text-xs text-left">
            <svg className="w-4 h-4 text-amber-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>
              <strong>Fidelidade garantida:</strong> A IA nunca inventa competências que você não possui. Ela reorganiza suas experiências reais e aponta o que falta.
            </span>
          </div>
        </div>

        {/* Mensagem de Erro Geral */}
        {errorMessage && (
          <div className="mb-8 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-start gap-3">
            <svg className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <strong className="font-semibold">Atenção:</strong> {errorMessage}
            </div>
            <button
              onClick={() => setErrorMessage('')}
              className="text-rose-400 hover:text-rose-700 transition"
            >
              ✕
            </button>
          </div>
        )}

        {/* Formulário de Análise */}
        <form onSubmit={handleAnalyze} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
            {/* Coluna 1: Upload de Currículo */}
            <div className="flex flex-col">
              <label className="block text-sm font-semibold text-slate-800 mb-2">
                1. Currículo atual (PDF ou DOCX)
              </label>

              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex-1 border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition ${
                  isDragging
                    ? 'border-indigo-500 bg-indigo-50/50'
                    : file
                    ? 'border-emerald-300 bg-emerald-50/20'
                    : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                />

                {file ? (
                  <div className="flex flex-col items-center">
                    <div className="h-12 w-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mb-3">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span className="font-medium text-slate-800 text-sm max-w-[220px] truncate">
                      {file.name}
                    </span>
                    <span className="text-xs text-slate-500 mt-1">
                      {(file.size / 1024).toFixed(1)} KB • Clique para trocar
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <div className="h-12 w-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <span className="text-sm font-medium text-slate-700">
                      Arraste seu arquivo ou <span className="text-indigo-600 underline">clique para selecionar</span>
                    </span>
                    <span className="text-xs text-slate-400 mt-1">
                      Suporte a arquivos PDF (.pdf) e Word (.docx)
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Coluna 2: Descrição da Vaga */}
            <div className="flex flex-col">
              <label htmlFor="job-description" className="block text-sm font-semibold text-slate-800 mb-2">
                2. Descrição da vaga desejada
              </label>
              <textarea
                id="job-description"
                rows={7}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Cole aqui o texto completo da vaga (responsabilidades, requisitos obrigatórios, diferenciais e tecnologias)..."
                className="w-full flex-1 p-3.5 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-slate-400 text-slate-800 resize-none transition"
              />
              <div className="mt-2 flex justify-between text-xs text-slate-400">
                <span>Mínimo recomendado: 20 caracteres</span>
                <span>{jobDescription.length} caracteres</span>
              </div>
            </div>
          </div>

          {/* Botão de Envio */}
          <div className="mt-8 pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
            <span className="text-xs text-slate-500">
              {apiStatus !== 'online' && '⚠️ Certifique-se de que o backend FastAPI está em execução.'}
            </span>

            <button
              type="submit"
              disabled={isLoading || !file || !jobDescription.trim()}
              className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-medium text-sm flex items-center justify-center gap-2 shadow-sm transition ${
                isLoading || !file || !jobDescription.trim()
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer active:scale-95'
              }`}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                  </svg>
                  Analisando com Gemini Pro...
                </>
              ) : (
                <>
                  <span>Analisar Compatibilidade</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Seção de Resultados */}
        {analysisResult && (
          <div id="results-section" className="mt-12 space-y-8 animate-fade-in">
            {/* Cabeçalho do Resultado com Score ATS */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
                <div className="flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
                  {/* Gauge de Score */}
                  <div
                    className={`w-24 h-24 rounded-2xl border-2 flex flex-col items-center justify-center shrink-0 ${getScoreColor(
                      analysisResult.ats_score
                    )}`}
                  >
                    <span className="text-3xl font-extrabold">{analysisResult.ats_score}</span>
                    <span className="text-[11px] font-semibold uppercase tracking-wider">de 100</span>
                  </div>

                  <div>
                    <div className="flex items-center justify-center sm:justify-start gap-2">
                      <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                        {getScoreBadgeText(analysisResult.ats_score)}
                      </span>
                    </div>
                    <h2 className="text-xl font-bold text-slate-900 mt-1">Diagnóstico Geral da IA</h2>
                    <p className="text-slate-600 text-sm mt-1 max-w-xl">
                      {analysisResult.summary}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
                  <button
                    onClick={handleDownloadPdf}
                    disabled={isDownloading}
                    className="w-full sm:w-auto px-5 py-2.5 rounded-xl font-medium text-sm bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center gap-2 shadow-sm transition active:scale-95"
                  >
                    {isDownloading ? (
                      <>
                        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                        </svg>
                        Gerando PDF...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Baixar Currículo Otimizado (PDF)
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleReset}
                    className="w-full sm:w-auto px-4 py-2.5 rounded-xl font-medium text-sm border border-slate-300 text-slate-700 hover:bg-slate-50 transition"
                  >
                    Nova Análise
                  </button>
                </div>
              </div>
            </div>

            {/* Grid: Palavras-chave Encontradas e Ausentes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Presentes */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <div className="flex items-center gap-2 text-emerald-700 font-semibold text-sm mb-4">
                  <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Palavras-chave encontradas ({analysisResult.matched_keywords?.length || 0})</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.matched_keywords?.map((kw, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200"
                    >
                      ✓ {kw}
                    </span>
                  ))}
                  {(!analysisResult.matched_keywords || analysisResult.matched_keywords.length === 0) && (
                    <span className="text-xs text-slate-400">Nenhuma correspondência exata detectada.</span>
                  )}
                </div>
              </div>

              {/* Ausentes */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <div className="flex items-center gap-2 text-rose-700 font-semibold text-sm mb-4">
                  <svg className="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Requisitos da vaga ausentes no currículo ({analysisResult.missing_keywords?.length || 0})</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.missing_keywords?.map((kw, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-rose-50 text-rose-800 border border-rose-200"
                    >
                      ✕ {kw}
                    </span>
                  ))}
                  {(!analysisResult.missing_keywords || analysisResult.missing_keywords.length === 0) && (
                    <span className="text-xs text-slate-400">Nenhum requisito crítico ausente!</span>
                  )}
                </div>
              </div>
            </div>

            {/* Grid: Pontos Fortes e Pontos a Melhorar */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Pontos Fortes */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900 text-sm mb-3 flex items-center gap-2">
                  <span className="text-emerald-600">★</span> Pontos Fortes Identificados
                </h3>
                <ul className="space-y-2.5 text-sm text-slate-600">
                  {analysisResult.strengths?.map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Pontos a Melhorar */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900 text-sm mb-3 flex items-center gap-2">
                  <span className="text-amber-500">⚡</span> Oportunidades de Melhoria
                </h3>
                <ul className="space-y-2.5 text-sm text-slate-600">
                  {analysisResult.improvements?.map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-amber-500 font-bold">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Visualização Prévia do Currículo Otimizado */}
            {analysisResult.optimized_resume && (
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="border-b border-slate-200 bg-slate-50 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">
                      Prévia do Currículo Otimizado
                    </h3>
                    <p className="text-xs text-slate-500">
                      Redação reformulada com verbos de ação e ênfase no alinhamento com a vaga.
                    </p>
                  </div>
                  <button
                    onClick={handleDownloadPdf}
                    disabled={isDownloading}
                    className="px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-1.5 transition"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Baixar PDF
                  </button>
                </div>

                <div className="p-6 sm:p-10 space-y-6 max-w-4xl mx-auto text-slate-800">
                  {/* Cabeçalho */}
                  <div className="text-center pb-6 border-b border-slate-200">
                    <h4 className="text-2xl font-bold text-slate-900 tracking-tight">
                      {analysisResult.optimized_resume.full_name || 'Nome do Candidato'}
                    </h4>
                    {analysisResult.optimized_resume.contact_info && (
                      <p className="text-xs text-slate-500 mt-1">
                        {analysisResult.optimized_resume.contact_info}
                      </p>
                    )}
                  </div>

                  {/* Resumo Profissional */}
                  {analysisResult.optimized_resume.professional_summary && (
                    <div>
                      <h5 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-1 mb-2">
                        Resumo Profissional
                      </h5>
                      <p className="text-sm text-slate-700 leading-relaxed">
                        {analysisResult.optimized_resume.professional_summary}
                      </p>
                    </div>
                  )}

                  {/* Habilidades */}
                  {analysisResult.optimized_resume.skills && (
                    <div>
                      <h5 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-1 mb-2">
                        Habilidades & Competências
                      </h5>
                      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-sm text-slate-700">
                        {analysisResult.optimized_resume.skills.map((s, idx) => (
                          <li key={idx} className="flex items-center gap-2">
                            <span className="text-indigo-500 font-bold">•</span>
                            <span>{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Experiências */}
                  {analysisResult.optimized_resume.experiences && (
                    <div>
                      <h5 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-1 mb-3">
                        Experiência Profissional
                      </h5>
                      <div className="space-y-4">
                        {analysisResult.optimized_resume.experiences.map((exp, idx) => (
                          <div key={idx} className="space-y-1">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between text-sm">
                              <span className="font-semibold text-slate-900">{exp.role}</span>
                              <span className="text-xs text-slate-500">{exp.period}</span>
                            </div>
                            <div className="text-xs font-medium text-slate-600 italic">
                              {exp.company}
                            </div>
                            <ul className="mt-2 space-y-1">
                              {exp.highlights?.map((h, hIdx) => (
                                <li key={hIdx} className="text-xs text-slate-700 flex items-start gap-2">
                                  <span className="text-slate-400 font-bold shrink-0">•</span>
                                  <span>{h}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Formação Acadêmica */}
                  {analysisResult.optimized_resume.education && (
                    <div>
                      <h5 className="text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-1 mb-2">
                        Formação Acadêmica
                      </h5>
                      <div className="space-y-2">
                        {analysisResult.optimized_resume.education.map((edu, idx) => (
                          <div key={idx} className="text-sm">
                            <span className="font-semibold text-slate-900">{edu.degree}</span>
                            <span className="text-slate-500 text-xs"> — {edu.institution} {edu.period ? `(${edu.period})` : ''}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12">
        <div className="max-w-6xl mx-auto px-4 text-center text-xs text-slate-500">
          ATS Resume Analyzer • Projeto de Portfólio • Integração com Google Gemini Pro via FastAPI & React
        </div>
      </footer>
    </div>
  )
}

export default App
