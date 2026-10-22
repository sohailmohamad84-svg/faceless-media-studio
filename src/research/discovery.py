"""Topic discovery and catalog management for Faceless Media Studio."""
from typing import List, Dict, Any
from src.database.models import Topic, Source
from src.database.repository import TopicRepository, SourceRepository
from src.research.scoring import calculate_topic_score


SEED_RESEARCH_TOPICS = [
    {
        "title": "How Costco's $1.50 Hot Dog Protects a $250 Billion Empire",
        "angle": "Why losing money on lunch is Costco's single most profitable strategic decision.",
        "category_pillar": "Hidden Unit Economics",
        "primary_viewer_question": "Why has Costco refused to raise the hot dog price since 1985 despite massive inflation?",
        "target_audience": "Curious consumers, business operators, retail investors",
        "evidence_summary": "Costco sells over 130 million hot dog combos annually. The food court is a loss leader engineered to anchor high-margin annual membership renewals (93% US renewal rate).",
        "demand": 94.0,
        "originality": 88.0,
        "evergreen": 98.0,
        "commercial": 92.0,
        "competition": 82.0,
        "source_quality": 95.0,
        "feasibility": 95.0,
        "why_this_topic": "Universal curiosity hook with bulletproof financial data from SEC Form 10-K filings. High organic CTR potential.",
        "suggested_length_min": 12,
        "sources": [
            {
                "title": "Costco Wholesale Corp Form 10-K (Annual Report)",
                "url": "https://investor.costco.com/sec-filings",
                "publisher": "U.S. Securities and Exchange Commission",
                "source_type": "SEC 10-K Filing",
                "excerpt": "Membership fee revenue accounted for over 72% of Costco's operating income in FY2023, enabling rock-bottom merchandise markups.",
                "credibility_rating": 5,
            },
            {
                "title": "The Story Behind Costco's $1.50 Hot Dog",
                "url": "https://www.mentalfloss.com/article/547020/costco-hot-dog-combo-price",
                "publisher": "Mental Floss & Seattle Times Archives",
                "source_type": "Historical Investigation",
                "excerpt": "Co-founder Jim Sinegal famously told former CEO Craig Jelinek: 'If you raise that effing hot dog, I will kill you. Figure it out.'",
                "credibility_rating": 4,
            },
        ],
    },
    {
        "title": "Why Toys 'R' Us Really Died (It Wasn't Amazon)",
        "angle": "How a $6.6 Billion Leveraged Buyout suffocated a beloved toy icon in Wall Street debt.",
        "category_pillar": "Corporate Autopsies",
        "primary_viewer_question": "Did Amazon kill Toys 'R' Us, or did private equity strip it from the inside?",
        "target_audience": "Nostalgic millennials, finance students, retail watchers",
        "evidence_summary": "In 2005, Bain Capital, KKR, and Vornado bought Toys 'R' Us using $5.3B in debt. Annual interest payments of $400M prevented store modernization and e-commerce investment.",
        "demand": 90.0,
        "originality": 85.0,
        "evergreen": 95.0,
        "commercial": 88.0,
        "competition": 80.0,
        "source_quality": 96.0,
        "feasibility": 92.0,
        "why_this_topic": "Busts the common myth that e-commerce killed retail; reveals the mechanical debt trap of leveraged buyouts.",
        "suggested_length_min": 14,
        "sources": [
            {
                "title": "Toys 'R' Us Chapter 11 Bankruptcy Court Docket",
                "url": "https://www.bloomberg.com/news/articles/toys-r-us-bankruptcy-debt",
                "publisher": "Bloomberg / US Bankruptcy Court Eastern District of Virginia",
                "source_type": "Court Records",
                "excerpt": "At the time of filing, Toys 'R' Us carried $5.2 billion in debt, consuming 97% of its operating profit just to service interest.",
                "credibility_rating": 5,
            }
        ],
    },
    {
        "title": "The Secret Math of Airline Miles: Why Airlines Are Actually Credit Card Banks",
        "angle": "Major airlines generate more operating profit selling loyalty points to Chase and Amex than flying passenger planes.",
        "category_pillar": "Hidden Unit Economics",
        "primary_viewer_question": "How do airlines survive when jet fuel and airplane leasing costs are so astronomical?",
        "target_audience": "Frequent flyers, travel hackers, fintech enthusiasts",
        "evidence_summary": "During the 2020 pandemic, United, American, and Delta mortgaged their frequent flyer programs for over $6B to $10B each, valuing the loyalty programs higher than the airlines themselves.",
        "demand": 89.0,
        "originality": 92.0,
        "evergreen": 92.0,
        "commercial": 95.0,
        "competition": 84.0,
        "source_quality": 94.0,
        "feasibility": 90.0,
        "why_this_topic": "Massive mindshift for viewers. Drives intense comment debate and high Tier-1 credit card advertiser RPM.",
        "suggested_length_min": 11,
        "sources": [
            {
                "title": "United Airlines MileagePlus Financing Disclosures",
                "url": "https://ir.united.com/sec-filings",
                "publisher": "SEC Form 8-K",
                "source_type": "SEC Filing",
                "excerpt": "MileagePlus was appraised at $21.9 billion in 2020, with EBITDA margins exceeding 53%.",
                "credibility_rating": 5,
            }
        ],
    },
    {
        "title": "How Lego Nearly Went Bankrupt in 2003 (And The Turnaround That Saved It)",
        "angle": "Lego was losing $1 million a day until a radical supply chain autopsy cut 50% of its brick variations.",
        "category_pillar": "Modern Strategic Pivots",
        "primary_viewer_question": "How did the world's most beloved toy company survive a near-fatal collapse?",
        "target_audience": "Entrepreneurs, design lovers, general audience",
        "evidence_summary": "Lego expanded into clothing, video games, and theme parks, ballooning to 12,000 unique parts. Jørgen Vig Knudstorp cut parts in half and focused on the core brick system.",
        "demand": 91.0,
        "originality": 84.0,
        "evergreen": 96.0,
        "commercial": 86.0,
        "competition": 81.0,
        "source_quality": 92.0,
        "feasibility": 92.0,
        "why_this_topic": "Inspiring turnaround story with timeless operational lessons about product discipline and supply chain focus.",
        "suggested_length_min": 13,
        "sources": [],
    },
    {
        "title": "The $47 Billion Illusion: The Autopsy of WeWork",
        "angle": "How Adam Neumann convinced SoftBank to value subleased desks at tech unicorn multiples.",
        "category_pillar": "Startup Implosions",
        "primary_viewer_question": "How did a commercial real estate subletting company convince investors it was worth $47 billion?",
        "target_audience": "Tech founders, venture capitalists, curious professionals",
        "evidence_summary": "WeWork committed to $47B in long-term lease obligations while relying on month-to-month tenant revenues, leading to disastrous unit economics when growth stalled.",
        "demand": 93.0,
        "originality": 82.0,
        "evergreen": 90.0,
        "commercial": 91.0,
        "competition": 78.0,
        "source_quality": 96.0,
        "feasibility": 93.0,
        "why_this_topic": "Modern financial drama with official SEC S-1 filings detailing bizarre governance and valuation excess.",
        "suggested_length_min": 15,
        "sources": [],
    },
    {
        "title": "Why Movie Theaters Don't Care About Ticket Sales",
        "angle": "The 85% margin popcorn engine that subsidizes Hollywood studios.",
        "category_pillar": "Hidden Unit Economics",
        "primary_viewer_question": "Why does movie theater popcorn cost $9 when a bag of kernels costs 15 cents?",
        "target_audience": "Film enthusiasts, consumers, business students",
        "evidence_summary": "Studios take up to 60-70% of box office ticket revenue. Theaters survive almost exclusively on concession margins and screen advertising.",
        "demand": 87.0,
        "originality": 86.0,
        "evergreen": 96.0,
        "commercial": 84.0,
        "competition": 85.0,
        "source_quality": 93.0,
        "feasibility": 96.0,
        "why_this_topic": "Highly relatable everyday consumer question with simple, striking unit economics charts.",
        "suggested_length_min": 10,
        "sources": [],
    },
    {
        "title": "How McDonald's Really Makes Billions: A Real Estate Company with Burgers",
        "angle": "Ray Kroc and Harry Sonneborn's formula of buying prime store real estate and leasing it to franchisees.",
        "category_pillar": "Hidden Unit Economics",
        "primary_viewer_question": "Is McDonald's a fast food restaurant or the world's largest commercial real estate owner?",
        "target_audience": "Real estate investors, franchise seekers, business students",
        "evidence_summary": "McDonald's owns over $40 billion in real estate and collects rent indexed to franchisee sales, generating high, recession-resistant operating margins.",
        "demand": 92.0,
        "originality": 80.0,
        "evergreen": 98.0,
        "commercial": 92.0,
        "competition": 75.0,
        "source_quality": 96.0,
        "feasibility": 95.0,
        "why_this_topic": "Timeless business model revelation that performs consistently well in search.",
        "suggested_length_min": 11,
        "sources": [],
    },
]


class TopicDiscoveryEngine:
    @staticmethod
    def seed_initial_topics() -> int:
        """Seed the database with the pre-researched topics if database is empty."""
        existing = TopicRepository.list_topics()
        if existing:
            return 0

        count = 0
        for item in SEED_RESEARCH_TOPICS:
            score_data = calculate_topic_score(
                demand=item["demand"],
                originality=item["originality"],
                evergreen=item["evergreen"],
                commercial=item["commercial"],
                competition=item["competition"],
                source_quality=item["source_quality"],
                feasibility=item["feasibility"],
            )

            topic = Topic(
                title=item["title"],
                angle=item["angle"],
                category_pillar=item["category_pillar"],
                primary_viewer_question=item["primary_viewer_question"],
                target_audience=item["target_audience"],
                evidence_summary=item["evidence_summary"],
                demand_score=item["demand"],
                originality_score=item["originality"],
                evergreen_score=item["evergreen"],
                commercial_score=item["commercial"],
                competition_score=item["competition"],
                source_quality_score=item["source_quality"],
                feasibility_score=item["feasibility"],
                total_score=score_data["total_score"],
                status="backlog",
                why_this_topic=item["why_this_topic"],
                suggested_length_min=item["suggested_length_min"],
            )
            topic_id = TopicRepository.add_topic(topic)
            count += 1

            for s in item.get("sources", []):
                source = Source(
                    topic_id=topic_id,
                    title=s["title"],
                    url=s["url"],
                    publisher=s.get("publisher", ""),
                    source_type=s.get("source_type", "Article"),
                    excerpt=s.get("excerpt", ""),
                    credibility_rating=s.get("credibility_rating", 5),
                )
                SourceRepository.add_source(source)

        return count
