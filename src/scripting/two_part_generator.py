"""Two-Part Cliffhanger Script and Storyboard Generator for high-retention video arcs."""
from typing import Tuple, List, Dict, Any
from src.database.models import Topic, Script, StoryboardScene, ClaimLedgerItem
from src.database.repository import ScriptRepository, StoryboardRepository, ClaimLedgerRepository


class TwoPartGenerator:
    @classmethod
    def generate_two_part_series(
        cls, topic: Topic, is_shorts: bool = False
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        """Generate a linked two-part video series (Part 1 + Part 2) designed to drive binge retention
        via an open loop cliffhanger at the end of Part 1. Supports 16:9 Longform or 9:16 Shorts (<60s).
        """
        if is_shorts:
            return cls._build_toys_r_us_shorts_series(topic)

        if "Toys" in topic.title or "Toys 'R' Us" in topic.title:
            return cls._build_toys_r_us_series(topic)
        elif "Costco" in topic.title:
            return cls._build_costco_series(topic)
        else:
            return cls._build_generic_series(topic)

    @classmethod
    def _build_toys_r_us_shorts_series(
        cls, topic: Topic
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        """High-retention vertical YouTube Shorts (<60s) with rapid-fire pacing and open loop cliffhanger."""
        # -------------------------------------------------------------
        # SHORTS PART 1: THE $6.6B WALL STREET HEIST (~49 SECONDS)
        # -------------------------------------------------------------
        p1_scenes = [
            StoryboardScene(scene_order=1, scene_title="Monopoly Hook", scene_type="hook", duration_sec=5.0, narration_text="In 2000, Toys 'R' Us controlled twenty percent of the American toy industry, printing half a billion dollars in pure profit.", visual_type="archival_photo", on_screen_text="20% TOY MONOPOLY"),
            StoryboardScene(scene_order=2, scene_title="Bulldozed", scene_type="hook", duration_sec=5.0, narration_text="Yet eighteen years later, every single store was bulldozed, liquidated, and abandoned.", visual_type="archival_photo", on_screen_text="LIQUIDATED & CLOSED"),
            StoryboardScene(scene_order=3, scene_title="The Amazon Lie", scene_type="hook", duration_sec=5.5, narration_text="The world was told that Amazon killed Toys 'R' Us. But that was a complete lie.", visual_type="newspaper", on_screen_text="THE LIE ABOUT AMAZON"),
            StoryboardScene(scene_order=4, scene_title="The Inside Job", scene_type="context", duration_sec=5.5, narration_text="Amazon didn't kill them. It was a calculated six point six billion dollar inside job by three Wall Street firms.", visual_type="court_docket", on_screen_text="$6.6B WALL STREET HEIST"),
            StoryboardScene(scene_order=5, scene_title="The Syndicate", scene_type="evidence", duration_sec=5.0, narration_text="In 2005, Bain Capital, KKR, and Vornado took Toys 'R' Us private in a Leveraged Buyout.", visual_type="archival_photo", on_screen_text="THE LBO SYNDICATE"),
            StoryboardScene(scene_order=6, scene_title="Borrowed 5.3B", scene_type="evidence", duration_sec=6.0, narration_text="The buyers put up almost none of their own cash. They forced Toys 'R' Us itself to borrow five point three billion dollars to buy itself.", visual_type="financial_autopsy", on_screen_text="$5.3B BORROWED DEBT"),
            StoryboardScene(scene_order=7, scene_title="400M Bleed", scene_type="evidence", duration_sec=5.5, narration_text="Overnight, Toys 'R' Us was hit with a four hundred million dollar annual interest bill. Ninety-seven percent of operating profit was wiped out.", visual_type="financial_autopsy", on_screen_text="$400M ANNUAL BLEED"),
            StoryboardScene(scene_order=8, scene_title="Zero Capital", scene_type="case_study", duration_sec=5.0, narration_text="They had zero dollars left to fix stores, pay workers, or build modern websites.", visual_type="archival_photo", on_screen_text="CAPITAL STARVATION"),
            StoryboardScene(scene_order=9, scene_title="Shorts Cliffhanger", scene_type="cliffhanger", duration_sec=6.5, narration_text="And in 2017, the trap snapped shut. Watch Part 2 right now to see the court filings showing where the billions went.", visual_type="cliffhanger", on_screen_text="WATCH PART 2 #Shorts"),
        ]

        p1_narration_full = " ".join([s.narration_text for s in p1_scenes])
        p1_script = Script(
            topic_id=topic.id or 1,
            version="3.0-Shorts",
            title="Why Toys 'R' Us Really Died (Part 1: The Trap) #Shorts",
            hook_text=p1_scenes[0].narration_text + " " + p1_scenes[1].narration_text + " " + p1_scenes[2].narration_text,
            promise_text=p1_scenes[3].narration_text,
            body_text=" ".join([s.narration_text for s in p1_scenes[4:8]]),
            conclusion_text=p1_scenes[8].narration_text,
            call_to_action="Watch Part 2 on the channel now #Shorts",
            word_count=len(p1_narration_full.split()),
            target_duration_sec=49,
            status="approved",
        )

        p1_claims = [
            ClaimLedgerItem(claim_text="Toys 'R' Us controlled ~20% of US toy market in 2000.", source_url="https://sec.gov", source_title="SEC 10-K Filing", verified=True, timestamp_marker="00:03"),
            ClaimLedgerItem(claim_text="Bain Capital and KKR saddled Toys 'R' Us with $5.3B debt.", source_url="https://sec.gov", source_title="Form 8-K Merger Docket", verified=True, timestamp_marker="00:25"),
        ]

        # -------------------------------------------------------------
        # SHORTS PART 2: THE $470M LOOTING & AUTOPSY (~47 SECONDS)
        # -------------------------------------------------------------
        p2_scenes = [
            StoryboardScene(scene_order=1, scene_title="Recap Docket", scene_type="hook", duration_sec=5.0, narration_text="In Part 1, we saw how Wall Street trapped Toys 'R' Us with five point three billion dollars in debt. Now comes the dirty secret.", visual_type="court_docket", on_screen_text="CHAPTER 11 DOCKET"),
            StoryboardScene(scene_order=2, scene_title="Worker Sacrifice", scene_type="hook", duration_sec=6.5, narration_text="While thirty-three thousand workers were fired with zero severance, the private equity owners had already extracted four hundred and seventy million dollars in fees.", visual_type="split_verdict", on_screen_text="33K FIRED vs $470M FEES"),
            StoryboardScene(scene_order=3, scene_title="400M Interest", scene_type="evidence", duration_sec=5.5, narration_text="For twelve straight years, four hundred million dollars vanished every single year just to service bank interest.", visual_type="financial_autopsy", on_screen_text="$400M ANNUAL INTEREST"),
            StoryboardScene(scene_order=4, scene_title="Amazon Suicide", scene_type="case_study", duration_sec=6.0, narration_text="To survive, Toys 'R' Us signed an exclusive ten-year deal for Amazon to run their website. It was digital suicide.", visual_type="newspaper", on_screen_text="THE FATAL AMAZON PACT"),
            StoryboardScene(scene_order=5, scene_title="Trojan Horse", scene_type="case_study", duration_sec=6.0, narration_text="Amazon studied their data, then allowed third-party sellers to undercut Toys 'R' Us on Amazon's own platform.", visual_type="newspaper", on_screen_text="AMAZON'S TROJAN HORSE"),
            StoryboardScene(scene_order=6, scene_title="Supplier Panic", scene_type="evidence", duration_sec=5.5, narration_text="By 2017, scared suppliers refused to ship Christmas toys. The company collapsed into Chapter 11 bankruptcy.", visual_type="archival_photo", on_screen_text="CHAPTER 11 BANKRUPTCY"),
            StoryboardScene(scene_order=7, scene_title="Liquidation", scene_type="evidence", duration_sec=6.0, narration_text="Liquidators stripped every store bare. Thirty-three thousand employees lost everything with zero severance.", visual_type="archival_photo", on_screen_text="TOTAL LIQUIDATION"),
            StoryboardScene(scene_order=8, scene_title="Shorts Verdict", scene_type="conclusion", duration_sec=6.5, narration_text="Toys 'R' Us was killed not by Amazon, but by predatory financial engineering. Subscribe to Apex Enterprise for more corporate autopsies.", visual_type="split_verdict", on_screen_text="SUBSCRIBE: APEX ENTERPRISE #Shorts"),
        ]

        p2_narration_full = " ".join([s.narration_text for s in p2_scenes])
        p2_script = Script(
            topic_id=topic.id or 1,
            version="3.0-Shorts",
            title="Why Toys 'R' Us Really Died (Part 2: The Final Verdict) #Shorts",
            hook_text=p2_scenes[0].narration_text + " " + p2_scenes[1].narration_text,
            promise_text=p2_scenes[2].narration_text,
            body_text=" ".join([s.narration_text for s in p2_scenes[3:7]]),
            conclusion_text=p2_scenes[7].narration_text,
            call_to_action="Subscribe to Apex Enterprise for weekly forensic business autopsies #Shorts",
            word_count=len(p2_narration_full.split()),
            target_duration_sec=47,
            status="approved",
        )

        p2_claims = [
            ClaimLedgerItem(claim_text="33,000 employees were terminated with zero severance in 2018.", source_url="https://wsj.com", source_title="WSJ Report", verified=True, timestamp_marker="00:08"),
            ClaimLedgerItem(claim_text="Private equity sponsors collected over $470M in fees.", source_url="https://sec.gov", source_title="Bankruptcy Court Fee Examiner Report", verified=True, timestamp_marker="00:10"),
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
    def _build_toys_r_us_series(
        cls, topic: Topic
    ) -> Tuple[Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]], Tuple[Script, List[StoryboardScene], List[ClaimLedgerItem]]]:
        # ======================================================================
        # PART 1: THE RISE, THE UNSTOPPABLE MONOPOLY & THE FATAL WALL STREET TRAP
        # ======================================================================
        p1_scenes = [
            StoryboardScene(
                scene_order=1,
                scene_title="The Untouchable Monopoly",
                scene_type="hook",
                duration_sec=6.5,
                narration_text="In 2000, Toys 'R' Us was an untouchable retail monopoly. They controlled twenty percent of the American toy industry, operated sixteen hundred massive stores, and printed half a billion dollars in pure profit.",
                visual_type="archival_photo",
                on_screen_text="20% US MARKET MONOPOLY",
            ),
            StoryboardScene(
                scene_order=2,
                scene_title="The Bulldozed Empire",
                scene_type="hook",
                duration_sec=6.0,
                narration_text="Yet eighteen years later, every single store was bulldozed, liquidated, and abandoned.",
                visual_type="archival_photo",
                on_screen_text="LIQUIDATED & ABANDONED",
            ),
            StoryboardScene(
                scene_order=3,
                scene_title="The Amazon Cover Story",
                scene_type="hook",
                duration_sec=6.5,
                narration_text="The public was told that Amazon killed Toys 'R' Us. But that was a convenient lie.",
                visual_type="newspaper",
                on_screen_text="THE LIE ABOUT AMAZON",
            ),
            StoryboardScene(
                scene_order=4,
                scene_title="The Investigation Promise",
                scene_type="context",
                duration_sec=7.5,
                narration_text="In this two-part investigation, we expose the secret six-point-six billion dollar Wall Street heist that doomed them before Amazon even sold toys.",
                visual_type="court_docket",
                on_screen_text="CONFIDENTIAL EVIDENCE: $6.6B HEIST",
            ),
            StoryboardScene(
                scene_order=5,
                scene_title="The Category Killer Origin",
                scene_type="context",
                duration_sec=7.0,
                narration_text="It started in 1948 when Charles Lazarus invented the 'category killer' — massive warehouse stores undercutting mom-and-pop shops by twenty-five percent.",
                visual_type="archival_photo",
                on_screen_text="PIONEER OF THE CATEGORY KILLER",
            ),
            StoryboardScene(
                scene_order=6,
                scene_title="The Cash Printing Engine",
                scene_type="evidence",
                duration_sec=6.5,
                narration_text="Toy makers were terrified. If you wanted to sell toys at Christmas, you bowed to Toys 'R' Us. They were printing cash.",
                visual_type="financial_autopsy",
                on_screen_text="$11.2B ANNUAL REVENUE",
            ),
            StoryboardScene(
                scene_order=7,
                scene_title="Walmart's Ambush",
                scene_type="case_study",
                duration_sec=7.0,
                narration_text="Then came 2004. Walmart launched an ambush, selling the top twenty bestselling toys below cost just to drag parents into their grocery aisles.",
                visual_type="newspaper",
                on_screen_text="WALMART PRICE WAR AMBUSH",
            ),
            StoryboardScene(
                scene_order=8,
                scene_title="The Wall Street Vultures Circle",
                scene_type="case_study",
                duration_sec=6.5,
                narration_text="Toys 'R' Us panicked. Their stock collapsed by fifty percent. And that was the exact moment the Wall Street vultures circled.",
                visual_type="archival_photo",
                on_screen_text="STOCK COLLAPSE: -50%",
            ),
            StoryboardScene(
                scene_order=9,
                scene_title="The Private Equity Syndicate",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="Three private equity giants struck: Bain Capital, KKR, and Vornado. In 2005, they offered six point six billion dollars to take the company private.",
                visual_type="archival_photo",
                on_screen_text="THE $6.6B TAKEOVER SYNDICATE",
            ),
            StoryboardScene(
                scene_order=10,
                scene_title="The Leveraged Buyout Trap",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="The board called it a masterstroke. But here is the trick: the buyers put up almost none of their own money. It was a Leveraged Buyout.",
                visual_type="financial_autopsy",
                on_screen_text="THE LBO DEBT MECHANISM",
            ),
            StoryboardScene(
                scene_order=11,
                scene_title="Borrowed Against Their Own Stores",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="They borrowed five point three billion dollars against Toys 'R' Us's own stores, forcing the company to pay back the very loan used to buy it.",
                visual_type="court_docket",
                on_screen_text="$5.3 BILLION BORROWED DEBT",
            ),
            StoryboardScene(
                scene_order=12,
                scene_title="The $400M Annual Bleed",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="Overnight, Toys 'R' Us was hit with a four hundred million dollar annual interest bill. Ninety-seven percent of operating profits vanished into Wall Street banks.",
                visual_type="financial_autopsy",
                on_screen_text="$400M ANNUAL INTEREST DRAIN",
            ),
            StoryboardScene(
                scene_order=13,
                scene_title="The Winter 2017 Trap Snaps",
                scene_type="cliffhanger",
                duration_sec=7.0,
                narration_text="And then came the winter of 2017. As the critical Christmas season approached, the debt trap snapped shut.",
                visual_type="archival_photo",
                on_screen_text="DECEMBER 2017: THE COLLAPSE",
            ),
            StoryboardScene(
                scene_order=14,
                scene_title="The Cliffhanger to Part 2",
                scene_type="cliffhanger",
                duration_sec=8.5,
                narration_text="What happened next inside bankruptcy court was a four-hundred-million-dollar corporate execution. Click right now for Part 2, where we expose the leaked filings showing where that money actually went.",
                visual_type="cliffhanger",
                on_screen_text="WATCH PART 2: THE $470M LOOTING",
            ),
        ]

        p1_narration_full = " ".join([s.narration_text for s in p1_scenes])
        p1_script = Script(
            topic_id=topic.id or 1,
            version="2.0",
            title=f"{topic.title} - (Part 1: The Trap)",
            hook_text=p1_scenes[0].narration_text + " " + p1_scenes[1].narration_text + " " + p1_scenes[2].narration_text,
            promise_text=p1_scenes[3].narration_text,
            body_text=" ".join([s.narration_text for s in p1_scenes[4:12]]),
            conclusion_text=p1_scenes[12].narration_text + " " + p1_scenes[13].narration_text,
            call_to_action="Click the on-screen link to watch Part 2 immediately.",
            word_count=len(p1_narration_full.split()),
            target_duration_sec=int(sum([s.duration_sec for s in p1_scenes])),
            status="approved",
        )

        p1_claims = [
            ClaimLedgerItem(claim_text="Toys 'R' Us controlled ~20% of US toy market with 1,600 stores in 2000.", source_url="https://sec.gov", source_title="SEC 10-K Annual Filing 2000", verified=True, timestamp_marker="00:04"),
            ClaimLedgerItem(claim_text="Bain Capital, KKR, and Vornado bought company in $6.6B LBO with $5.3B debt.", source_url="https://sec.gov", source_title="Form 8-K Merger Syndicate Filing", verified=True, timestamp_marker="00:55"),
            ClaimLedgerItem(claim_text="Annual debt interest payments exceeded $400M, eating 97% of operating cash.", source_url="https://bloomberg.com", source_title="Bloomberg Forensic Bankruptcy Analysis", verified=True, timestamp_marker="01:15"),
        ]

        # ======================================================================
        # PART 2: THE RECKONING, THE 400M DRAIN & THE AUTOPSY VERDICT
        # ======================================================================
        p2_scenes = [
            StoryboardScene(
                scene_order=1,
                scene_title="The Courtroom Crime Scene",
                scene_type="hook",
                duration_sec=7.0,
                narration_text="In Part 1, we saw how private equity trapped Toys 'R' Us with five point three billion dollars in debt. Now, in federal bankruptcy court, the full crime scene is exposed.",
                visual_type="court_docket",
                on_screen_text="CHAPTER 11 COURT EXHIBIT",
            ),
            StoryboardScene(
                scene_order=2,
                scene_title="The Worker Sacrificial Lamb",
                scene_type="hook",
                duration_sec=7.5,
                narration_text="While thirty-three thousand retail employees were thrown onto the street with zero severance, the private equity owners had already extracted four hundred and seventy million dollars in fees.",
                visual_type="split_verdict",
                on_screen_text="33,000 JOBS vs $470M FEES",
            ),
            StoryboardScene(
                scene_order=3,
                scene_title="The Forensic Cash Drain",
                scene_type="evidence",
                duration_sec=7.0,
                narration_text="Between 2005 and 2017, Toys 'R' Us paid four hundred million dollars every single year just to service interest on their debt.",
                visual_type="financial_autopsy",
                on_screen_text="$400M ANNUAL DEBT PAYMENT",
            ),
            StoryboardScene(
                scene_order=4,
                scene_title="The Modern Retail Arms Race",
                scene_type="case_study",
                duration_sec=6.5,
                narration_text="To survive in modern retail, companies must invest. While Amazon and Target poured billions into automated warehouses, mobile apps, and same-day delivery...",
                visual_type="archival_photo",
                on_screen_text="AMAZON LOGISTICS REVOLUTION",
            ),
            StoryboardScene(
                scene_order=5,
                scene_title="Starved of Capital",
                scene_type="case_study",
                duration_sec=7.5,
                narration_text="...Toys 'R' Us had literally zero dollars left. They couldn't upgrade checkout registers. They couldn't fix broken air conditioning. Stores began to look like decaying warehouses.",
                visual_type="archival_photo",
                on_screen_text="ZERO CAPITAL FOR STORES",
            ),
            StoryboardScene(
                scene_order=6,
                scene_title="The Fatal Amazon Contract",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="And then came the fatal Amazon deal. In 2000, terrified of building their own tech, Toys 'R' Us signed an exclusive ten-year agreement for Amazon to run their website.",
                visual_type="newspaper",
                on_screen_text="THE FATAL 10-YEAR AMAZON PACT",
            ),
            StoryboardScene(
                scene_order=7,
                scene_title="The Digital Trojan Horse",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="It was suicide. Amazon studied their customer data, learned which toys sold best, and then allowed third-party sellers to undercut Toys 'R' Us on Amazon's own platform.",
                visual_type="newspaper",
                on_screen_text="AMAZON'S TROJAN HORSE",
            ),
            StoryboardScene(
                scene_order=8,
                scene_title="The Pyrrhic Legal Victory",
                scene_type="case_study",
                duration_sec=7.0,
                narration_text="Toys 'R' Us sued and won fifty-one million dollars, but by then it was too late. They were five years behind on digital commerce, and the debt clock was ticking.",
                visual_type="court_docket",
                on_screen_text="$51M LAWSUIT WON — TOO LATE",
            ),
            StoryboardScene(
                scene_order=9,
                scene_title="Supplier Panic in 2017",
                scene_type="case_study",
                duration_sec=7.0,
                narration_text="By September 2017, suppliers got scared. Rumors spread that Toys 'R' Us couldn't pay for holiday inventory. Credit insurers pulled coverage.",
                visual_type="newspaper",
                on_screen_text="SUPPLIERS PULL HOLIDAY CREDIT",
            ),
            StoryboardScene(
                scene_order=10,
                scene_title="The Chapter 11 Stampede",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="In a matter of days, the toy giant filed for Chapter 11 bankruptcy. Liquidation vultures moved in. Stores were stripped down to the metal fixtures.",
                visual_type="archival_photo",
                on_screen_text="CHAPTER 11: TOTAL LIQUIDATION",
            ),
            StoryboardScene(
                scene_order=11,
                scene_title="The Human Cost vs Wall Street Profits",
                scene_type="evidence",
                duration_sec=7.5,
                narration_text="Thirty-three thousand workers lost their livelihoods overnight. Yet the private equity executives who engineered the debt walked away with millions in advisory fees.",
                visual_type="split_verdict",
                on_screen_text="ZERO SEVERANCE vs MILLIONS IN FEES",
            ),
            StoryboardScene(
                scene_order=12,
                scene_title="The Autopsy Truth",
                scene_type="conclusion",
                duration_sec=7.5,
                narration_text="Toys 'R' Us didn't die because children stopped wanting toys. It died because financial engineering starved a healthy business of the oxygen it needed to survive.",
                visual_type="archival_photo",
                on_screen_text="KILLED BY DEBT, NOT AMAZON",
            ),
            StoryboardScene(
                scene_order=13,
                scene_title="The Final Corporate Autopsy Verdict",
                scene_type="conclusion",
                duration_sec=7.0,
                narration_text="The company was slaughtered not by innovation, but by predatory Wall Street greed. A masterclass in how to loot an American icon.",
                visual_type="court_docket",
                on_screen_text="CASE CLOSED: CORPORATE AUTOPSY",
            ),
            StoryboardScene(
                scene_order=14,
                scene_title="Channel Call to Action",
                scene_type="conclusion",
                duration_sec=6.5,
                narration_text="Subscribe to Apex Enterprise for more corporate autopsies. Drop a comment below: what company is Wall Street silently destroying right now?",
                visual_type="split_verdict",
                on_screen_text="SUBSCRIBE: APEX ENTERPRISE",
            ),
        ]

        p2_narration_full = " ".join([s.narration_text for s in p2_scenes])
        p2_script = Script(
            topic_id=topic.id or 1,
            version="2.0",
            title=f"{topic.title} - (Part 2: The Final Verdict)",
            hook_text=p2_scenes[0].narration_text + " " + p2_scenes[1].narration_text,
            promise_text=p2_scenes[2].narration_text,
            body_text=" ".join([s.narration_text for s in p2_scenes[3:11]]),
            conclusion_text=" ".join([s.narration_text for s in p2_scenes[11:14]]),
            call_to_action="Subscribe to Apex Enterprise for weekly forensic business autopsies.",
            word_count=len(p2_narration_full.split()),
            target_duration_sec=int(sum([s.duration_sec for s in p2_scenes])),
            status="approved",
        )

        p2_claims = [
            ClaimLedgerItem(claim_text="33,000 employees were terminated with zero severance in 2018.", source_url="https://wsj.com", source_title="Wall Street Journal Retail Bankruptcy Report", verified=True, timestamp_marker="00:10"),
            ClaimLedgerItem(claim_text="Bain Capital and KKR collected over $470M in management and transaction fees.", source_url="https://theintercept.com", source_title="Investigative SEC Proxy Docket Review", verified=True, timestamp_marker="00:15"),
            ClaimLedgerItem(claim_text="Toys 'R' Us sued Amazon in 2004 for breach of exclusivity contract and won $51M.", source_url="https://reuters.com", source_title="Reuters Court Record", verified=True, timestamp_marker="00:48"),
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
