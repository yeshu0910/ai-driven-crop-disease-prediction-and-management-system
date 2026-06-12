# Project Constitution

## Purpose
This project builds an AI-Driven Crop Disease Prediction and Management System. Every feature must support farmers and agronomists in identifying, diagnosing, and managing crop diseases using machine learning and reliable data.

## Core Principles
- **Farmer-First Design**: Every feature must prioritize usability in real agricultural settings with limited connectivity.
- **Data Integrity**: Crop and disease data must be accurate, reproducible, and version-controlled.
- **AI Transparency**: ML predictions must include confidence scores and evidence-based explanations.
- **Security & Privacy**: Farmer and farm data must be protected with end-to-end encryption and role-based access.
- **Interoperability**: System must integrate with IoT sensors, weather APIs, and farm management platforms via open standards.
- **Open Development**: All specs, plans, and tasks must be documented in this Spec-Kit structure.
- **Testing Rigor**: ML models require statistical validation; APIs require integration tests; minimum 80% code coverage.

## Governance
- All features require a `spec.md` approved before implementation.
- Architecture decisions are recorded in `plan.md`.
- Work is tracked in `tasks.md` with explicit status columns.
- Breaking changes to the ML pipeline require a migration plan.
- No secrets in code, `.env`, or documentation.

## Tech Stack Constraints
- Backend: Python 3.10+, FastAPI, PostgreSQL
- ML: PyTorch, ONNX for model serving
- Mobile: Flutter (iOS/Android)
- Infra: Docker, GitLab CI/CD, Kubernetes
