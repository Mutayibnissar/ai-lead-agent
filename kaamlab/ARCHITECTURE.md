# KaamLab MVP Architecture

## Core actors
1. Learner — learns micro-skills, accepts real briefs, submits deliverables, builds a Talent Passport.
2. Business — posts a problem, reviews matched evidence, gives feedback and can convert project work into paid opportunities.
3. Admin — verifies evidence, manages pilot quality and monitors validation metrics.

## Core loop
Course → Real Work → Talent Passport → Opportunity

Business Problem Marketplace → Brief → Matching → Delivery → Business Feedback → Verification → Passport → Paid Project / Internship / Job

## AI layer
AI should assist, not replace verification:
- brief structuring
- skill extraction and micro-skill mapping
- learner/project matching
- project-plan generation
- feedback summarization
- portfolio/Talent Passport drafting
- learner work assistant

Human verification remains the trust layer.

## Data model
User(id, role, name, email)
Skill(id, name, track)
Course(id, skill_ids)
Business(id, profile, verification_status)
Brief(id, business_id, title, description, skill_ids, deadline, status)
Application(id, brief_id, learner_id, status)
Project(id, brief_id, learner_id, deliverables, status)
Feedback(id, project_id, business_id, rating, comments)
Evidence(id, project_id, file_url, verification_status)
Passport(id, learner_id, verified_project_ids, skills, feedback)
Opportunity(id, project_id, type, status)

## Production stack
Next.js + TypeScript + Tailwind
PostgreSQL/Supabase
Object storage for evidence
Server-side OpenAI integration
GitHub Actions CI/CD

## Pilot
10–12 weeks, 15 learners, 5 businesses, 3 tracks, with 1–2 projects/student as the source presentation proposes. These are pilot assumptions, not validated results.
