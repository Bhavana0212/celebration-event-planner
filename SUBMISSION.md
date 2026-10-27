# Hack2Skill submission pack — Challenge 5

Fill the form fields below. Do NOT submit until you have pasted your real
public GitHub link, deployed Streamlit link, demo video link and LinkedIn post link.
You have 3 attempts total, and the module closes 1 Nov 2026 at 1:29 PM IST.

## 1. Public GitHub Repository Link
Paste your public repo URL here, e.g. https://github.com/<your-username>/celebration-event-planner
Rules checked: public, single branch (main), under 10 MB.

## 2. Project Deployed Link
Paste your Streamlit Cloud URL here, e.g. https://<your-app>.streamlit.app
Deploy steps are in README.md.

## 3. Project Demo Video Submission
Upload the demo walkthrough to YouTube as Unlisted, or to Drive with access given,
then paste that link here. The Instagram reel (final_reel_v3.mp4, with voiceover)
is a 85-second walkthrough of the same plan — it can be reused as the demo video
only after you upload it to YouTube/Drive; do not paste an Instagram link here
unless the form accepts it.

## 4. Describe the changes / updates made in the deployed version (copy-paste)

Merged two builds into one market-ready Streamlit Celebration & Event Planner for 8 event types including Community Event. One form now generates: invitation, real guest list with RSVP, context-aware budget split with tier and actual-vs-planned tracker, vendor checklist and vendor manager, countdown checklist, day schedule, games, music by moment, guest-scaled shopping list, logistics, dietary-safe menu, risk alerts, and Markdown/.ics/CSV/JSON export. Added a landing page, multi-event dashboard, currency choice, 101 passing tests and CI. Core planning is rule-based and testable; AI is an optional ideas layer with offline fallback.

## 5. Mention the Gen AI services utilized, and where (copy-paste)

GenAI was used in two places. (1) Development: Muse (Meta AI) assisted in merging, designing and testing this app. (2) In-app: Google Gemini (gemini-2.5-flash, via google-genai) in planner/ai.py writes creative ideas in the Ideas tab when GEMINI_API_KEY is set in Streamlit Secrets; it sends only validated plan context, with user notes fenced as untrusted data, capped at 5 calls per session. Without a key, offline ideas are used and the app works fully. No GCP credits were used and no key is hard-coded.

## 6. LinkedIn Post — post this text first, then paste the post link

Post text (copy-paste to LinkedIn):

I built a GenAI-powered Celebration & Event Planner for Hack2Skill Virtual: PromptWars — Challenge 5. 🎉

One prompt — occasion, guests, budget, theme — creates an invitation, guest list, budget split, vendor checklist, day schedule, games, music plan, shopping list and personalised ideas. It works for weddings, birthdays and community events.

Plan smarter. Celebrate bigger.
#PromptWars #Hack2Skill #GenAI #EventPlanning

After posting on LinkedIn, paste that post's URL (starting https://linkedin.com/...) into the LinkedIn Post field on Hack2Skill. Do not paste a profile URL.
