# CareerOS

> *Your career data is scattered everywhere. CareerOS puts the pieces together.*

**[→ Try CareerOS](https://careeros-yp7y.onrender.com)**

CareerOS is an AI-powered career intelligence platform that analyzes a candidate's professional footprint across multiple sources and turns it into an evidence-backed career profile.

Instead of evaluating a resume in isolation, CareerOS cross-checks information across:

- 📄 Resume
- 💼 LinkedIn
- 🐙 GitHub
- 💻 LeetCode

The goal is simple:

> **Separate what a candidate claims, what they demonstrate, and what can be independently supported across sources.**

---

## What Makes CareerOS Different?

Most resume analyzers ask:

> *"How good is this resume?"*

CareerOS asks:

> *"What does the evidence across this candidate's professional footprint actually say?"*

It connects resume claims with professional experience, projects, skills, and problem-solving activity to build a more complete picture of the candidate.

---

## How It Works

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
