
# CareerOS

> *Your career data is scattered everywhere. CareerOS puts the pieces together.*

CareerOS is an AI-powered career intelligence platform that analyzes a candidate's professional footprint across multiple sources and turns it into an evidence-backed career profile.

Instead of evaluating a resume in isolation, CareerOS cross-checks information across:

- Resume
- LinkedIn
- GitHub
- LeetCode

The goal is to distinguish between what a candidate **claims**, what they **demonstrate**, and what can be **independently supported across sources**.

---

## What CareerOS Does

CareerOS runs a multi-stage career intelligence pipeline:

```text
                    ┌─────────────────┐
                    │  Resume PDF/DOCX│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Resume Extraction│
                    │ & Link Detection │
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
     Profile +          Repository +       Problem +
     experience         project analysis   skill analysis
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Unified Evidence    │
                  │ Engine               │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Career Intelligence │
                  │ & Scoring            │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │ React Dashboard      │
                  └─────────────────────┘