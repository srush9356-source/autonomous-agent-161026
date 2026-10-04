from app.models.source import Source
from app.services.competitive_intelligence import CompetitiveIntelligenceExtractor


source = Source(
    source_id="SRC-TEST-001",
    title="Example Food Company",
    url="https://example.com",
    source_type="company_website",
    publisher="Example Food Company",
    publication_date=None,
    authority_score=0.8,
    relevance_score=0.9,
    freshness_score=0.8,
)

content = """
Example Food Company produces processed fruit products for food and beverage
manufacturers. Its product portfolio includes mango pulp, guava pulp, and
strawberry pulp. The company supplies products in bulk quantities and focuses
on B2B customers. Pricing is available through direct quotation. The company
serves customers in domestic and international markets and emphasizes
consistent quality and reliable supply.
"""

extractor = CompetitiveIntelligenceExtractor()

result = extractor.extract(
    source=source,
    content=content,
)

print("\nCompetitive Intelligence:\n")

for key, value in result.items():
    print(f"{key}: {value}")