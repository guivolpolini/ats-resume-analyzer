# ATS Resume Analyzer

MVP de uma plataforma de análise e otimização de currículos utilizando Inteligência Artificial (Google Gemini Pro).

> 🚧 Projeto em desenvolvimento — construído passo a passo, documentando cada etapa via commits no GitHub.

## O que o projeto faz

- Envio de currículo em PDF ou DOCX
- Cole a descrição de uma vaga
- Análise via Google Gemini Pro:
  - ATS Score (0 a 100)
  - Palavras-chave presentes e ausentes
  - Pontos fortes e pontos a melhorar
  - Geração de currículo otimizado para a vaga
- Preview e download do currículo otimizado em PDF
- Limite de 3 análises gratuitas por dia (usuários comuns)
- Administrador com análises ilimitadas (verificado no backend)

## Stack

**Frontend:** React + Vite + Tailwind CSS
**Backend:** Python + FastAPI
**IA:** Google Gemini Pro API
**Versionamento:** Git + GitHub

## Estrutura do projeto

```text
ats-resume-analyzer/
│
├── frontend/
│
├── backend/
│   └── app/
│       ├── routes/
│       ├── services/
│       ├── utils/
│       └── prompts/
│
├── .env.example
├── .gitignore
└── README.md
```

## Como rodar (em construção)

As instruções de instalação e execução do frontend e do backend serão adicionadas conforme cada parte for implementada nas próximas etapas.

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```env
GEMINI_API_KEY=
ADMIN_EMAIL=
```

A chave da API do Gemini fica exclusivamente no backend — nunca é exposta no frontend.

## Regra importante sobre a IA

O Gemini nunca inventa informações. Ele só reorganiza, melhora e adapta o que já existe no currículo enviado. Se uma habilidade pedida na vaga não estiver no currículo, o sistema informa que ela está ausente, em vez de inventá-la.

## Roadmap futuro

- Login / Cadastro / Login com Google
- Banco de dados e histórico de análises
- Assinaturas (Mercado Pago) com planos Free e Pro
- Geração de carta de apresentação
- Otimização de LinkedIn
- Preparação para entrevistas
- Dashboard de candidaturas

## Status

Etapa atual: **1 — inicialização do projeto**
