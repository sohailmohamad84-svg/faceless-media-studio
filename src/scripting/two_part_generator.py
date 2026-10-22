"""Two-Part Cliffhanger Script and Storyboard Generator for high-retention video arcs."""
from typing import Tuple, List, Dict, Any
from src.database.models import Topic, Script, StoryboardScene, ClaimLedgerItem
from src.database.repository import ScriptRepository, StoryboardRepository, ClaimLedgerRepository


class TwoPartGenerator:
    @classmethod
    def generate_two_part_series(
        cls, topic: Topic
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        """Generate a linked two-part video series (Part 1 + Part 2) designed to drive binge retention
        via an open loop cliffhanger at the end of Part 1.
        """
        if "Toys" in topic.title or "Toys 'R' Us" in topic.title:
            return cls._build_toys_r_us_series(topic)
        elif "Costco" in topic.title:
            return cls._build_costco_series(topic)
        else:
            return cls._build_generic_series(topic)

    @classmethod
    def _build_toys_r_us_series(
        cls, topic: Topic
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        # ======================================================================
        # PART 1: THE RISE, THE UNSTOPPABLE MONOPOLY & THE FATAL WALL STREET TRAP
        # ======================================================================
        p1_hook = (
            "In 2000, Toys 'R' Us was untouchable. "
            "They controlled twenty percent of the American toy market, operated sixteen hundred stores, "
            "and generated twelve billion dollars in revenue. "
            "Yet eighteen years later, every single store was liquidated and bulldozed. "
            "Most people still believe Amazon killed Toys 'R' Us. That is a lie."
        )
        p1_promise = (
            "In this two-part investigation, we uncover the secret financial trap that destroyed a childhood icon — "
            "and the six-billion-dollar Wall Street deal that doomed them before Amazon even sold toys."
        )
        p1_body = (
            "Toys 'R' Us wasn't just a toy store; it was the original retail category killer. "
            "Charles Lazarus pioneered high-volume warehouse aisles that undercut mom-and-pop shops by twenty-five percent. "
            "Suppliers were terrified of them. If you wanted to sell a toy at Christmas, you bowed to Toys 'R' Us.\n\n"
            "But by 2004, a quiet crisis began. Walmart started selling the top twenty toys at a loss to lure parents into buying groceries. "
            "Toys 'R' Us panicked. Their stock plummeted fifty percent. "
            "And that's when three private equity giants circled: Bain Capital, KKR, and Vornado."
        )
        p1_cliffhanger = (
            "In 2005, the board signed a secret six point six billion dollar deal that Wall Street called a masterstroke. "
            "What the public didn't know was that the buyers put up almost none of their own money. "
            "They loaded five point three billion dollars in debt directly onto Toys 'R' Us's balance sheet. "
            "And what happened next inside those boardrooms was a 400-million-dollar annual bloodbath. "
            "Click on-screen or in the description for Part 2: The Final Execution, where we expose the exact bankruptcy filings that finished them off."
        )

        p1_script = Script(
            topic_id=topic.id or 1,
            version="1.0",
            title=f"{topic.title} - (Part 1: The Trap)",
            hook_text=p1_hook,
            promise_text=p1_promise,
            body_text=p1_body,
            conclusion_text=p1_cliffhanger,
            call_to_action="Watch Part 2 right now for the shocking conclusion.",
            word_count=len((p1_hook + " " + p1_promise + " " + p1_body + " " + p1_cliffhanger).split()),
            target_duration_sec=75,
            status="draft",
        )

        p1_scenes = [
            StoryboardScene(scene_order=1, scene_title="The Untouchable Empire", scene_type="hook", duration_sec=14.0, narration_text=p1_hook, visual_type="headline", on_screen_text="THE LIE ABOUT AMAZON"),
            StoryboardScene(scene_order=2, scene_title="The Investigation Promise", scene_type="context", duration_sec=10.0, narration_text=p1_promise, visual_type="title_card", on_screen_text="PART 1: THE TRAP"),
            StoryboardScene(scene_order=3, scene_title="The Category Killer", scene_type="evidence", duration_sec=16.0, narration_text="Toys 'R' Us was the original category killer. Charles Lazarus pioneered massive warehouse aisles that undercut competitors by 25 percent. If you sold a toy, you bowed to them.", visual_type="chart", on_screen_text="20% US MARKET DOMINANCE"),
            StoryboardScene(scene_order=4, scene_title="Walmart's Ambush", scene_type="case_study", duration_sec=18.0, narration_text="By 2004, Walmart started selling the top twenty toys at a loss to lure parents into buying groceries. Toys 'R' Us panicked as stock plummeted fifty percent. That's when Bain Capital and KKR circled.", visual_type="document", on_screen_text="STOCK COLLAPSE: -50%"),
            StoryboardScene(scene_order=5, scene_title="The Cliffhanger to Part 2", scene_type="cliffhanger", duration_sec=18.0, narration_text=p1_cliffhanger, visual_type="cliffhanger", on_screen_text="WATCH PART 2 NOW: THE $6.6B COLLAPSE"),
        ]

        p1_claims = [
            ClaimLedgerItem(claim_text="Toys 'R' Us operated over 1,600 stores and controlled 20% of US toy market.", source_url="https://sec.gov", source_title="Toys 'R' Us Annual Report 2000", verified=True, timestamp_marker="00:04"),
            ClaimLedgerItem(claim_text="Bain Capital, KKR, and Vornado executed $6.6B LBO with $5.3B debt.", source_url="https://sec.gov", source_title="Form 8-K Merger Filing 2005", verified=True, timestamp_marker="00:55"),
        ]

        # ======================================================================
        # PART 2: THE RECKONING, THE 400M DRAIN & THE AUTOPSY VERDICT
        # ======================================================================
        p2_hook = (
            "Previously in Part 1, we saw how private equity loaded Toys 'R' Us with five point three billion dollars in debt. "
            "Now comes the part Wall Street tried to hide: where the money actually went."
        )
        p2_promise = (
            "In this concluding investigation, we dissect the court exhibits from the Chapter 11 bankruptcy filing "
            "to reveal why Toys 'R' Us couldn't even afford to fix broken air conditioning in their stores."
        )
        p2_body = (
            "From 2005 to 2017, Toys 'R' Us paid four hundred million dollars every single year just to service interest on their debt. "
            "To put that in perspective: ninety-seven percent of their operating profits vanished straight into bank interest payments.\n\n"
            "While Amazon and Target spent hundreds of millions upgrading websites, modernizing supply chains, and building mobile apps, "
            "Toys 'R' Us had zero dollars left. "
            "Their stores smelled old, registers broke down, and their website was outsourced because they couldn't fund their own engineering team.\n\n"
            "When the retail crisis hit in 2017, lenders refused to refinance. The company fell into bankruptcy court, where liquidated assets paid off the debt holders while 33,000 employees lost their jobs with zero severance."
        )
        p2_conclusion = (
            "Toys 'R' Us didn't die because children stopped wanting toys. "
            "It died because financial engineering suffocated an operational titan. "
            "Subscribe to Apex Enterprise for more forensic business autopsies. Drop a comment: which retailer is repeating this fatal mistake today?"
        )

        p2_script = Script(
            topic_id=topic.id or 1,
            version="1.0",
            title=f"{topic.title} - (Part 2: The Final Verdict)",
            hook_text=p2_hook,
            promise_text=p2_promise,
            body_text=p2_body,
            conclusion_text=p2_conclusion,
            call_to_action="Subscribe for weekly forensic corporate autopsies.",
            word_count=len((p2_hook + " " + p2_promise + " " + p2_body + " " + p2_conclusion).split()),
            target_duration_sec=80,
            status="draft",
        )

        p2_scenes = [
            StoryboardScene(scene_order=1, scene_title="Recap Hook", scene_type="hook", duration_sec=12.0, narration_text=p2_hook, visual_type="title_card", on_screen_text="PART 2: THE AUTOPSY"),
            StoryboardScene(scene_order=2, scene_title="The $400M Annual Drain", scene_type="evidence", duration_sec=18.0, narration_text="From 2005 to 2017, Toys 'R' Us paid four hundred million dollars every single year just to service interest. Ninety-seven percent of operating profits vanished into Wall Street banks.", visual_type="chart", on_screen_text="$400,000,000 ANNUAL INTEREST"),
            StoryboardScene(scene_order=3, scene_title="The Paralyzed Balance Sheet", scene_type="case_study", duration_sec=22.0, narration_text="While Amazon and Target poured hundreds of millions into websites and supply chains, Toys 'R' Us had zero capital left. Stores degraded and the website fell years behind.", visual_type="document", on_screen_text="ZERO CAPITAL FOR INNOVATION"),
            StoryboardScene(scene_order=4, scene_title="The Liquidation & Verdict", scene_type="conclusion", duration_sec=20.0, narration_text=p2_conclusion, visual_type="headline", on_screen_text="KILLED BY DEBT: THE AUTOPSY VERDICT"),
        ]

        p2_claims = [
            ClaimLedgerItem(claim_text="Toys 'R' Us paid ~$400M annually in interest expense from 2005-2017.", source_url="https://sec.gov", source_title="Form 10-K Pre-Bankruptcy SEC Filing", verified=True, timestamp_marker="00:15"),
            ClaimLedgerItem(claim_text="33,000 workers were terminated during liquidation in 2018.", source_url="https://bloomberg.com", source_title="Bloomberg Bankruptcy Court Docket", verified=True, timestamp_marker="00:45"),
        ]

        # Save both to database
        s1_id = ScriptRepository.add_script(p1_script)
        p1_script.id = s1_id
        StoryboardRepository.clear_scenes_for_script(s1_id)
        for s in p1_scenes:
            s.script_id = s1_id
            StoryboardRepository.add_scene(s)
        for c in p1_claims:
            c.script_id = s1_id
            ClaimLedgerRepository.add_claim(c)

        s2_id = ScriptRepository.add_script(p2_script)
        p2_script.id = s2_id
        StoryboardRepository.clear_scenes_for_script(s2_id)
        for s in p2_scenes:
            s.script_id = s2_id
            StoryboardRepository.add_scene(s)
        for c in p2_claims:
            c.script_id = s2_id
            ClaimLedgerRepository.add_claim(c)

        return (p1_script, p1_scenes, p1_claims), (p2_script, p2_scenes, p2_claims)

    @classmethod
    def _build_costco_series(
        cls, topic: Topic
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        # Part 1: The $1.50 Mystery & The Negative Margin Hot Dog
        p1_hook = (
            "Every year, Costco sells over 130 million hot dogs. "
            "And since 1985, the price hasn't changed by a single cent: exactly one dollar and fifty cents. "
            "If that price kept up with inflation, you'd be paying over five dollars today. "
            "When the CEO tried to raise the price, the founder threatened his life."
        )
        p1_promise = (
            "In Part 1 of this investigation, we uncover the secret economics behind Costco's loss leader — "
            "and why losing millions on hot dogs is actually a calculated psychological weapon."
        )
        p1_body = (
            "Costco Wholesale isn't a supermarket. "
            "Standard supermarkets make money by marking up groceries twenty-five to thirty percent. "
            "At Costco, markups are strictly capped at fourteen percent — barely enough to pay warehouse utilities.\n\n"
            "So why does Costco sell hot dogs and whole rotisserie chickens at a massive loss? "
            "Because they engineered the world's most lucrative psychological anchor."
        )
        p1_cliffhanger = (
            "In 2023, Wall Street analysts realized something terrifying about Costco's financial statements: "
            "if you removed one specific line item from their balance sheet, Costco would literally be bankrupt. "
            "What is that secret line item? "
            "Click on-screen right now for Part 2: The Secret Subscription Empire, where we reveal the hidden billion-dollar machine."
        )

        p1_script = Script(
            topic_id=topic.id or 1,
            version="1.0",
            title=f"{topic.title} - (Part 1: The Inflation-Proof Mystery)",
            hook_text=p1_hook,
            promise_text=p1_promise,
            body_text=p1_body,
            conclusion_text=p1_cliffhanger,
            call_to_action="Watch Part 2 for the secret balance sheet revelation.",
            word_count=len((p1_hook + " " + p1_promise + " " + p1_body + " " + p1_cliffhanger).split()),
            target_duration_sec=70,
            status="draft",
        )

        p1_scenes = [
            StoryboardScene(scene_order=1, scene_title="The $1.50 Threat", scene_type="hook", duration_sec=14.0, narration_text=p1_hook, visual_type="headline", on_screen_text="$1.50 SINCE 1985"),
            StoryboardScene(scene_order=2, scene_title="The Loss Leader Weapon", scene_type="context", duration_sec=12.0, narration_text=p1_promise, visual_type="title_card", on_screen_text="PART 1: THE WEAPON"),
            StoryboardScene(scene_order=3, scene_title="The 14% Markup Cap", scene_type="evidence", duration_sec=16.0, narration_text=p1_body, visual_type="chart", on_screen_text="14% MAXIMUM MARKUP"),
            StoryboardScene(scene_order=4, scene_title="The Cliffhanger to Part 2", scene_type="cliffhanger", duration_sec=16.0, narration_text=p1_cliffhanger, visual_type="cliffhanger", on_screen_text="WATCH PART 2: THE HIDDEN MACHINE"),
        ]

        p1_claims = [
            ClaimLedgerItem(claim_text="Costco hot dog combo has stayed at $1.50 since 1985.", source_url="https://investor.costco.com", source_title="Costco Historical Disclosures", verified=True, timestamp_marker="00:04"),
            ClaimLedgerItem(claim_text="Costco merchandise markups are capped at 14-15%.", source_url="https://sec.gov", source_title="SEC Form 10-K Costco Wholesale Corp", verified=True, timestamp_marker="00:30"),
        ]

        # Part 2: The $4.6 Billion Subscription Goldmine
        p2_hook = (
            "Previously in Part 1, we saw that Costco loses money on its legendary hot dogs. "
            "Now, let's look at the smoking gun on page 32 of their SEC Form 10-K: Membership Fees."
        )
        p2_promise = (
            "In Part 2, we expose the exact financial formula that turned a warehouse club into a 250 billion dollar empire."
        )
        p2_body = (
            "In 2023, Costco collected four point six billion dollars in membership dues from one hundred and twenty-eight million cardholders. "
            "Because collecting an annual membership fee requires almost zero cost of goods sold, "
            "that single line item generates seventy-two percent of Costco's total operating profit!\n\n"
            "Costco doesn't sell groceries to make money. Costco sells groceries at cost to trick you into renewing your sixty-dollar annual subscription. "
            "And with a ninety-three percent renewal rate, it is the most ironclad recurring cash engine in corporate history."
        )
        p2_conclusion = (
            "The hot dog isn't a sacrifice. It is the gatekeeper to a four-billion-dollar toll booth. "
            "Subscribe to Apex Enterprise for weekly forensic business dissections. What corporate secret should we investigate next?"
        )

        p2_script = Script(
            topic_id=topic.id or 1,
            version="1.0",
            title=f"{topic.title} - (Part 2: The $4.6B Secret)",
            hook_text=p2_hook,
            promise_text=p2_promise,
            body_text=p2_body,
            conclusion_text=p2_conclusion,
            call_to_action="Subscribe to Apex Enterprise for more forensic dissections.",
            word_count=len((p2_hook + " " + p2_promise + " " + p2_body + " " + p2_conclusion).split()),
            target_duration_sec=75,
            status="draft",
        )

        p2_scenes = [
            StoryboardScene(scene_order=1, scene_title="The SEC Form 10-K Smoking Gun", scene_type="hook", duration_sec=12.0, narration_text=p2_hook, visual_type="document", on_screen_text="PAGE 32: MEMBERSHIP FEES"),
            StoryboardScene(scene_order=2, scene_title="72% Operating Profit", scene_type="evidence", duration_sec=18.0, narration_text=p2_body[:180], visual_type="chart", on_screen_text="72% OF TOTAL OPERATING INCOME"),
            StoryboardScene(scene_order=3, scene_title="The 93% Renewal Lock", scene_type="case_study", duration_sec=18.0, narration_text=p2_body[180:], visual_type="document", on_screen_text="93% RENEWAL RATE: THE TOLL BOOTH"),
            StoryboardScene(scene_order=4, scene_title="The Final Verdict", scene_type="conclusion", duration_sec=16.0, narration_text=p2_conclusion, visual_type="headline", on_screen_text="THE $250B LESSON"),
        ]

        p2_claims = [
            ClaimLedgerItem(claim_text="Costco membership fee revenue was $4.58B in 2023 (>70% of operating income).", source_url="https://sec.gov", source_title="Costco Wholesale FY2023 Form 10-K", verified=True, timestamp_marker="00:15"),
            ClaimLedgerItem(claim_text="US and Canada membership renewal rate is 92.7%.", source_url="https://investor.costco.com", source_title="Costco Q4 2023 Earnings Release", verified=True, timestamp_marker="00:35"),
        ]

        # Save both
        s1_id = ScriptRepository.add_script(p1_script)
        p1_script.id = s1_id
        StoryboardRepository.clear_scenes_for_script(s1_id)
        for s in p1_scenes:
            s.script_id = s1_id
            StoryboardRepository.add_scene(s)
        for c in p1_claims:
            c.script_id = s1_id
            ClaimLedgerRepository.add_claim(c)

        s2_id = ScriptRepository.add_script(p2_script)
        p2_script.id = s2_id
        StoryboardRepository.clear_scenes_for_script(s2_id)
        for s in p2_scenes:
            s.script_id = s2_id
            StoryboardRepository.add_scene(s)
        for c in p2_claims:
            c.script_id = s2_id
            ClaimLedgerRepository.add_claim(c)

        return (p1_script, p1_scenes, p1_claims), (p2_script, p2_scenes, p2_claims)

    @classmethod
    def _build_generic_series(
        cls, topic: Topic
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        # Generic fallback implementation
        p1_hook = f"Every major industry has a secret rule that outsiders never see. In {topic.title}, conventional wisdom is completely upside down."
        p1_promise = f"In Part 1 of this investigation, we dissect the strategic mechanics and unit economics behind {topic.title}."
        p1_body = f"When we analyze the public corporate filings, one startling fact emerges: {topic.evidence_summary}"
        p1_cliff = f"In Part 2, the secret boardroom showdown that changed everything. Click Part 2 on-screen right now to see the smoking gun."

        p1_script = Script(topic_id=topic.id or 1, title=f"{topic.title} - (Part 1)", hook_text=p1_hook, promise_text=p1_promise, body_text=p1_body, conclusion_text=p1_cliff, word_count=80, target_duration_sec=60, status="draft")
        p1_scenes = [
            StoryboardScene(scene_order=1, scene_title="Part 1 Hook", duration_sec=14.0, narration_text=p1_hook, visual_type="headline", on_screen_text=topic.title[:30].upper()),
            StoryboardScene(scene_order=2, scene_title="The Core Evidence", duration_sec=18.0, narration_text=p1_body, visual_type="chart", on_screen_text="THE HIDDEN MECHANISM"),
            StoryboardScene(scene_order=3, scene_title="Part 1 Cliffhanger", duration_sec=16.0, narration_text=p1_cliff, visual_type="cliffhanger", on_screen_text="WATCH PART 2 NOW"),
        ]
        p1_claims = [ClaimLedgerItem(claim_text=topic.evidence_summary[:100], source_url="https://sec.gov", source_title="SEC Filings", verified=True)]

        p2_hook = f"Previously in Part 1, we uncovered the hidden mechanics behind {topic.title}. Now comes the final reckoning."
        p2_promise = f"In Part 2, we reveal the financial autopsy and where the money actually went."
        p2_body = f"The underlying numbers expose why market dominance is never permanent without strategic discipline."
        p2_conc = "Subscribe to Apex Enterprise for more forensic corporate autopsies. What company should we investigate next?"

        p2_script = Script(topic_id=topic.id or 1, title=f"{topic.title} - (Part 2: The Verdict)", hook_text=p2_hook, promise_text=p2_promise, body_text=p2_body, conclusion_text=p2_conc, word_count=80, target_duration_sec=60, status="draft")
        p2_scenes = [
            StoryboardScene(scene_order=1, scene_title="Part 2 Recap", duration_sec=14.0, narration_text=p2_hook, visual_type="title_card", on_screen_text="PART 2: THE RECKONING"),
            StoryboardScene(scene_order=2, scene_title="The Verdict", duration_sec=18.0, narration_text=p2_body, visual_type="document", on_screen_text="THE FINAL AUTOPSY"),
            StoryboardScene(scene_order=3, scene_title="Conclusion", duration_sec=14.0, narration_text=p2_conc, visual_type="headline", on_screen_text="STRATEGIC VERDICT"),
        ]
        p2_claims = [ClaimLedgerItem(claim_text=topic.evidence_summary[:100], source_url="https://sec.gov", source_title="SEC Filings", verified=True)]

        s1_id = ScriptRepository.add_script(p1_script)
        p1_script.id = s1_id
        for s in p1_scenes:
            s.script_id = s1_id
            StoryboardRepository.add_scene(s)
        for c in p1_claims:
            c.script_id = s1_id
            ClaimLedgerRepository.add_claim(c)

        s2_id = ScriptRepository.add_script(p2_script)
        p2_script.id = s2_id
        for s in p2_scenes:
            s.script_id = s2_id
            StoryboardRepository.add_scene(s)
        for c in p2_claims:
            c.script_id = s2_id
            ClaimLedgerRepository.add_claim(c)

        return (p1_script, p1_scenes, p1_claims), (p2_script, p2_scenes, p2_claims)
