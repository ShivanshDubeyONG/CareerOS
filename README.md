# CareerOS

> *Your career data is scattered everywhere. CareerOS puts the pieces together.*

[![Live Demo](https://img.shields.io/badge/Live-Demo-2dd4a8?style=for-the-badge)](https://careeros-yp7y.onrender.com)

CareerOS is an AI-powered career intelligence platform that analyzes a candidate's professional footprint across multiple sources and turns it into an evidence-backed career profile.

Instead of evaluating a resume in isolation, CareerOS cross-checks information across:

- 📄 Resume
- 💼 LinkedIn
- 🐙 GitHub
- 💻 LeetCode

The goal is simple:

> **Separate what a candidate claims, what they demonstrate, and what can be independently supported across sources.**

## 🚀 Live Demo

### [→ Try CareerOS](https://careeros-yp7y.onrender.com)

Upload a resume and let CareerOS connect the signals across your professional footprint.

> **Note:** The backend runs on Render's free tier, so the first analysis after inactivity may take some time to wake up.

---

## 🧠 What Makes CareerOS Different?

Most resume analyzers answer:

> *"How good is this resume?"*

CareerOS asks a different question:

> *"What does the evidence across this candidate's professional footprint actually say?"*

A candidate might claim Python experience on their resume.

CareerOS can cross-reference that claim against:

- LinkedIn experience
- GitHub repositories and technologies
- LeetCode problem-solving activity
- Project descriptions and evidence

This creates a **cross-source view of the candidate**, rather than treating each profile independently.

---

## ⚙️ How It Works

CareerOS runs a multi-stage career intelligence pipeline:

```text
                    ┌─────────────────┐
                    │ Resume PDF/DOCX │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │Resume Extraction│
                    │& Link Detection │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
     ┌─────────┐       ┌──────────┐       ┌──────────┐
     │ LinkedIn│       │  GitHub  │       │ LeetCode │
     └────┬────┘       └────┬─────┘       └────┬─────┘
          │                  │                  │
          ▼                  ▼                  ▼
      Profile +           Repository +       Problem +
     experience         project analysis   skill analysis
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Unified Evidence    │
                  │ Engine              │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Career Intelligence │
                  │ & Scoring           │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │ React Dashboard     │
                  └─────────────────────┘
