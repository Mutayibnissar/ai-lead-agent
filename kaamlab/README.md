# KaamLab Website

Premium static website prototype for KaamLab — Kashmir Skill Employment Ecosystem.

## Source alignment
The website follows the concept and terminology of the KaamLab presentation:
- Learn. Do. Prove. Earn.
- Course → Real Work → Talent Passport → Opportunity
- Micro-skills
- Real Work Lab
- Business Problem Marketplace
- Talent Passport
- Project → Paid Project → Paid Internship → Job
- Srinagar-first 10–12 week pilot
- 15 learners, 5 businesses, 3 tracks

Pilot figures, pricing, budget and economics are illustrative assumptions and should be validated before launch.

## Production direction
Recommended next layer: Next.js + TypeScript, Tailwind CSS, PostgreSQL/Supabase, role-based authentication, portfolio evidence storage, server-side OpenAI integration for skill extraction/brief generation/matching/feedback, and GitHub Actions for CI/CD.

Never put an OpenAI API key in browser-side JavaScript. Store OPENAI_API_KEY as a server-side secret/environment variable.

This prototype lives under kaamlab/ so the existing repository content remains untouched.
