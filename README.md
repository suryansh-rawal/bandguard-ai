# 🛡️ BrandGuard AI

### AI-Powered Brand Governance & Content Review

**BrandGuard AI** is a brand-governance platform designed to help teams review content before publication. It aims to identify brand-rule violations, explain issues, suggest corrections, and keep humans in control of the final decision.

> **Project:** Inkloom AI Problem Statement — Round 2
> **Team:** Tech Titans
> **Team Leader:** Kanishka Shishodia
> **Team Member:** Suryansh Singh Rawal

---

## 📌 Problem Statement

Content created by employees, agencies, freelancers, and AI tools can contain unsupported claims, banned terminology, inconsistent brand messaging, and other guideline violations.

Manual reviews are time-consuming, and simple rejection messages do not help creators understand how to improve their content.

BrandGuard AI aims to provide an explainable review workflow that helps teams identify issues and improve content before publication.

## 💡 Proposed Solution

BrandGuard AI is designed to let users submit content, review detected issues, understand the reasons behind them, and work with suggested corrections.

Its core principle is:

**Detect → Explain → Fix → Review → Approve**

The final decision remains with the human reviewer.

## ✨ Current Features

The following frontend features have been implemented and manually tested locally:

* **Landing Page:** Introduction to BrandGuard AI.
* **Content Input:** Enter or paste text for review.
* **Content Type Selection:** Choose the type of content being reviewed.
* **Review Interface:** Display issue cards using sample API response data.
* **Issue Details:** Show issue types, severity, explanations, and guideline references from the mock response.
* **Review Actions:** Accept, edit, and dispute interactions are available in the interface; full backend persistence remains to be verified.
* **Copy Final Text:** Copy the final text from the report interface.
* **Input Validation:** Display a validation message when the submitted text is empty.
* **Text Design Controls:** Preview text with configurable fonts, size, spacing, weight, and colour.
* **Responsive Layout:** Mobile-sized and desktop layouts have been manually checked.

### Current Implementation Status

The frontend currently uses a fixed mock API response when mock mode is enabled. Consequently, the displayed issues are sample data and do not represent live AI analysis of arbitrary user input.

Live backend integration, production deployment, and complete end-to-end testing are pending.

## 🛠️ Technology Stack

| Technology           | Purpose                                 |
| -------------------- | --------------------------------------- |
| React                | Frontend components and UI              |
| Vite                 | Development server and production build |
| Tailwind CSS         | Responsive styling                      |
| React Router         | Client-side navigation                  |
| JavaScript Fetch API | API communication layer                 |
| JSON                 | Mock analysis response                  |

The original proposal also outlines a backend architecture involving FastAPI, PostgreSQL with pgvector, retrieval-based evidence checking, deterministic rules, and a hosted language model. These components should be considered planned until their implementation is verified.

## 🔄 Core Workflow

1. Open the application.
2. Navigate to the content analysis page.
3. Enter or paste content and select a content type.
4. Submit the content for analysis.
5. Review the report generated from the current mock response.
6. Inspect issue explanations and suggested corrections.
7. Use the available review actions.
8. Copy the final text.

**Note:** The current mock mode returns a predefined sample report. Live analysis of the submitted content will depend on backend integration.

## 🚀 Run Locally

### Prerequisites

* Node.js
* npm
* Git

### Installation

Clone the repository:

```bash
git clone https://github.com/suryansh-rawal/bandguard-ai.git
```

Navigate to the frontend directory:

```bash
cd bandguard-ai/frontend
```

Install dependencies:

```bash
npm install
```

Create or configure the frontend environment file as described below.

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in your terminal.

### Production Build

To create a production build:

```bash
npm run build
```

To preview the generated build locally:

```bash
npm run preview
```

The production build has been tested locally.

## ⚙️ Environment Configuration

The frontend uses environment variables to select mock mode and configure the backend API.

Example `.env` configuration for local mock mode:

```env
VITE_USE_MOCK=true
```

When the backend is ready, configure the API URL using the variable expected by the current API helper:

```env
VITE_USE_MOCK=false
VITE_API_URL=http://localhost:8000
```

Replace the example API URL with the actual backend URL when deploying.

**Important:** Never place private API keys, database passwords, or other secrets in frontend environment variables. Variables exposed to a browser are not secret.

## 🧪 Testing

The project includes a `TEST_SET.md` file with test scenarios covering:

* Clean content
* Banned terminology
* Unsupported claims
* Brand-fact mismatches
* Brand-tone violations
* Sensitive information

These scenarios must be executed against the live backend before reporting final pass/fail results.

### Verified Locally

* Landing-to-Analyze navigation
* Text input
* Report rendering with mock data
* Empty-input validation
* Copy final text
* Responsive layout checks
* Successful production build

### Pending Verification

* Live API integration
* Analysis of arbitrary submitted content
* Backend persistence for review actions
* Live citation and evidence validation
* Complete end-to-end workflow
* Production deployment

## 🔮 Planned Improvements for Round 3

### 1. Evidence-Backed Analysis Engine

Connect the application to a live analysis backend that checks submitted content against brand rules and approved evidence, provides explainable findings, and routes uncertain or high-risk issues for human review.

### 2. Review Workflow and Audit Trail

Introduce role-based review, approval and request-changes workflows, comments, version comparison, and traceable review history.

### 3. Guideline Health Dashboard

Identify repeated content violations and frequently disputed or unclear guidelines, helping teams improve their brand rules over time.

## 👥 Team

**Tech Titans**

* **Kanishka Shishodia** — Team Leader
* **Suryansh Singh Rawal** — Team Member

## 📌 Project Status

BrandGuard AI is under development for Round 2 of the Inkloom AI problem statement. The frontend prototype is available for local testing; backend integration and production deployment remain pending.

---

*BrandGuard AI — Helping teams protect brand trust before content goes live.*
