# ATS Resume Analyzer 🚀

Plataforma prática de análise e otimização de currículos para sistemas ATS (Applicant Tracking Systems) utilizando Inteligência Artificial (**Google Gemini Pro**).

> 💡 **Projeto de Portfólio**: Desenvolvido com foco em código limpo, arquitetura desacoplada e simplicidade técnica, sem complexidade de multi-tenancy ou sistemas de billing.

---

## 📋 Funcionalidades

- **Upload de currículo**: Suporte nativo a arquivos **PDF** (`.pdf`) e **Word** (`.docx`).
- **Análise contextual contra a vaga**: Avaliação de alinhamento com base na descrição real da oportunidade.
- **ATS Score (0 a 100)**: Métrica quantitativa de aderência do candidato aos requisitos da vaga.
- **Detecção de Palavras-Chave**:
  - Palavras-chave encontradas no currículo.
  - Palavras-chave ausentes exigidas ou valorizadas na descrição da vaga.
- **Diagnóstico Técnico**:
  - Destaques e pontos fortes identificados.
  - Oportunidades claras de melhoria.
- **Currículo Otimizado**:
  - Reestruturação profissional dos textos, experiências e competências.
  - Visualização formatada em tempo real na interface web.
- **Geração e Download de PDF**:
  - Download imediato de uma versão diagramada e 100% legível por softwares ATS (gerada via ReportLab).

---

## 🛡️ Regra de Integridade da IA (Anti-Alucinação)

O sistema segue uma **diretriz inegociável** definida no prompt do modelo:
- **A IA nunca inventa informações**, qualificações, empresas ou ferramentas não presentes no currículo original.
- O modelo apenas reestrutura, aprimora a clareza e destaca fatos reais. Competências não encontradas são reportadas como ausentes para que o candidato saiba onde se capacitar.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologias |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide Icons |
| **Backend** | Python 3.13, FastAPI, Uvicorn, Pydantic |
| **Processamento de Arquivos** | `pypdf`, `python-docx` |
| **Geração de PDF** | `reportlab` |
| **Inteligência Artificial** | Google GenAI SDK (`google-genai`), modelo Gemini Pro / 2.5 Flash |
| **Testes Automatizados** | `pytest`, `httpx` |

---

## 📂 Estrutura do Projeto

```text
ats-resume-analyzer/
├── frontend/                     # Interface do usuário (React + Vite + Tailwind)
│   ├── src/
│   │   ├── App.jsx               # Interface principal de upload, score e preview
│   │   ├── main.jsx              # Ponto de entrada React
│   │   └── index.css             # Estilos Tailwind
│   ├── package.json
│   └── vite.config.js
│
├── backend/                      # API REST em FastAPI
│   ├── app/
│   │   ├── main.py               # Inicialização do FastAPI e CORS
│   │   ├── routes/
│   │   │   └── analysis.py       # Endpoints /api/analyze e /api/generate-pdf
│   │   ├── services/
│   │   │   ├── gemini_service.py # Integração e parsing do Google Gemini
│   │   │   └── pdf_generator.py  # Diagramação de PDF com ReportLab
│   │   ├── utils/
│   │   │   └── extractor.py      # Extração de texto de PDF e DOCX
│   │   └── prompts/
│   │       └── ats_prompt.py     # Prompt estruturado com saída JSON
│   ├── tests/                    # Suíte de testes unitários e de integração
│   ├── requirements.txt          # Dependências de produção
│   └── requirements-dev.txt      # Dependências de desenvolvimento e testes
│
├── .env.example                  # Modelo de variáveis de ambiente
├── .gitignore
└── README.md
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- **Node.js** (versão 18 ou superior)
- **Python** (versão 3.11 ou superior)
- Chave de API do Google Gemini ([Google AI Studio](https://aistudio.google.com/))

### 1. Configurando o Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Adicione sua GEMINI_API_KEY no arquivo .env

# Iniciar o servidor FastAPI
uvicorn app.main:app --reload --port 8000
```
API disponível em: `http://localhost:8000`  
Documentação Swagger interativa: `http://localhost:8000/docs`

### 2. Configurando o Frontend

Em um novo terminal:

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento Vite
npm run dev
```
Aplicação disponível em: `http://localhost:5173`

---

## 🧪 Executando os Testes Automatizados

O backend conta com uma suíte abrangente cobrindo healthcheck, validação de entradas, extração de texto em PDF/DOCX, geração de PDF e fluxo mockado da IA:

```bash
cd backend
python -m pytest -v
```

---

## ☁️ Guia de Deploy Gratuito

### Backend (Render ou Railway)
1. Crie uma conta no [Render](https://render.com/).
2. Crie um novo **Web Service** conectado ao seu repositório GitHub.
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment Variables**, adicione:
   - `GEMINI_API_KEY`: sua chave do Google Gemini.
   - `FRONTEND_ORIGIN`: URL do frontend (ex: `https://meu-ats.vercel.app`).

### Frontend (Vercel)
1. Crie uma conta na [Vercel](https://vercel.com/).
2. Importe o repositório e configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
3. Em **Environment Variables**, adicione:
   - `VITE_API_URL`: URL do seu backend no Render (ex: `https://ats-api.onrender.com`).
4. Clique em **Deploy**.

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais detalhes.
