# CareerOS

**[LIVE DEMO](https://careeros-yp7y.onrender.com)**

CareerOS is an AI-powered career intelligence platform that analyzes a candidate's professional footprint across multiple sources and turns it into an evidence-backed career profile.

Instead of evaluating a resume in isolation, CareerOS cross-checks information across:

- Resume
- LinkedIn
- GitHub
- LeetCode


<img width="1385" height="906" alt="p1gng" src="https://github.com/user-attachments/assets/6a858f54-fd26-41aa-8e6b-433ff4e74d45" />
<img width="1388" height="965" alt="p2gng" src="https://github.com/user-attachments/assets/3b3f2677-e55f-41d7-9632-2cb82352cd86" />

<img width="1377" height="970" alt="p3gng" src="https://github.com/user-attachments/assets/c629a447-27f7-47eb-8479-81d4960c3f15" />
<img width="1382" height="963" alt="p4gng" src="https://github.com/user-attachments/assets/9203569d-1a1f-4702-9de0-046d1e8c6891" />

<img width="1243" height="840" alt="p5gng" src="https://github.com/user-attachments/assets/eade6255-4884-4d75-b415-6ebd9fc70b34" />

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
