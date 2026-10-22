# Copyright Policy, Content Originality & Compliance Guide

## 1. Official YouTube Partner Program (YPP) Compliance

YouTube's monetization policies prioritize **originality, viewer value, and authentic storytelling**. Channels that aggregate generic content or rely on automated text-to-speech reading Wikipedia pages face rejection under the **"Reused Content"** and **"Repetitive Content"** policies.

### Reused Content Policy
- **Definition:** Reused content is content that does not provide significant original commentary, narrative perspective, or educational value.
- **How Faceless Media Studio Guarantees Compliance:**
  1. **Original Research & Synthesis:** Every video combines primary source financial filings (SEC 10-Ks, investor earnings calls, court documents) with investigative storytelling.
  2. **No Competitor Video Snippets:** The studio prohibits downloading and chopping up competitor YouTube videos or television broadcasts.
  3. **Procedural & Original Visuals:** The visual track relies on original high-resolution charts created from data, animated kinetic typography, verified public domain photographs, and licensed Creative Commons / Pexels B-roll.
  4. **Claim Ledger Verification:** Every material fact is cross-referenced in an internal ledger, ensuring verifiable accuracy.

### Repetitive Content Policy
- **Definition:** Mass-produced, programmatic videos produced from identical templates without discernible qualitative variation.
- **How Faceless Media Studio Prevents Repetitive Content:**
  1. **Unique Narrative Architecture:** Video storyboards are customized to the specific business story (e.g., a corporate duel vs. a bankruptcy autopsy vs. a pricing strategy breakdown).
  2. **Adaptive Visual Layouts:** Dynamic switching between timeline charts, financial waterfalls, split-screen comparisons, and archival news cards.
  3. **Similarity Checks:** Automated script comparisons flag vocabulary overlap with previous channel uploads.

---

## 2. Fair Use & Nominative Fair Use Standards

In corporate business documentaries, referencing company names, trademarks, and historical events is legally protected under **Nominative Fair Use**:
- **Permissible Use:** Using a brand name (e.g., "Costco", "Boeing", "Netflix") or displaying their official trademarked logo solely for the purpose of identifying the subject of critical news, commentary, or financial analysis.
- **Prohibited Conduct:** 
  - Using a brand's logo in a way that implies endorsement, sponsorship, or affiliation.
  - Using copyrighted music, movie scenes, or protected broadcast footage without explicit licensing.
- **Fair Use Checklist Before Production:**
  - [x] Is the logo or brand asset used purely for identification and factual analysis?
  - [x] Does the commentary provide educational or analytical value beyond the asset itself?
  - [x] Is the amount of referenced third-party material limited to what is strictly necessary?
  - [x] Does the video avoid acting as a market substitute for the original asset?

---

## 3. Synthetic Media & YouTube AI Disclosure Rules

YouTube requires creators to disclose when content includes **realistic altered or synthetic media** (such as AI-generated voices or realistic synthetic footage depicting real-world events).

### Application Implementation
1. **Mandatory Metadata Flag:** When uploading via the YouTube Data API, `hasAlteredOrSyntheticContent` is flagged whenever AI narration or synthetic visuals are utilized.
2. **On-Screen Transparency:** Video descriptions automatically include a standard editorial disclosure:
   > *"Narration generated with neural voice technology. Research, data visualization, scriptwriting, and editorial curation produced by the Apex Enterprise editorial team."*
3. **Strict Prohibition on Deepfakes & Impersonation:**
   - The studio will **never** generate synthetic voice clones of real executives, political figures, or celebrities.
   - The studio will **never** generate realistic fabricated video footage of historical events presented as fact.

---

## 4. Pre-Publication Compliance Gate

Every video must pass an automated and manual 8-point compliance gate before entering the human approval queue:

1. **Source Citation:** Are all statistics, revenue figures, and historical dates backed by primary sources in the claim ledger?
2. **Audio Rights:** Is the voice model licensed for commercial content production? Is background music copyright-free / licensed?
3. **Asset Licensing:** Does every stock photo, video clip, and illustration carry an active CC0, Pexels, Pixabay, or public-domain license record in `assets.db`?
4. **Advertiser Friendliness:** Does the script avoid gratuitous violence, hate speech, vulgarity, and unverified medical/financial fraud?
5. **No Clickbait Misrepresentation:** Does the video deliver on the exact promise made in the title and thumbnail?
6. **Competitor Script Similarity:** Has the script been verified to be 100% original prose, avoiding close paraphrasing?
7. **SEC/Financial Disclaimer:** Does the description carry the required educational disclosure (*"This video is for educational purposes only and does not constitute financial, investment, or legal advice"*).
8. **Human Review Sign-off:** Has an authenticated editor watched the complete 1080p rendered export from beginning to end?
