from dataclasses import dataclass

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()

EXAMPLES = {
    "Payment issue": "I was charged twice for my subscription and need a refund.",
    "Bug report": "The application crashes every time I try to upload a PDF.",
    "Feedback": "The new dashboard looks great. I really like the simpler design.",
}

CATEGORIES = {
    "Billing": "Payments, charges, invoices, refunds or subscriptions",
    "Support": "Questions or help using the product",
    "Bug": "Something in the product is broken or not working as expected",
    "Feedback": "Opinions, praise or suggestions about the product",
    "General": "Anything that does not fit the other categories",
}

URGENCY_LEVELS = [
    "Can wait, no action needed soon",
    "Should be handled this week",
    "Should be handled within a day",
    "Should be handled within hours",
    "Needs immediate action",
]


@dataclass
class Analysis:
    category: str
    category_confidence: float
    urgency: float
    urgency_label: str
    urgency_confidence: float
    human_attention: bool
    human_attention_confidence: float


def analyze(message: str) -> Analysis:
    client = TypeSafeClient()  # reads TYPESAFE_API_KEY from the environment
    response = client.system_one(
        state=message,
        questions={
            "category": Choice(
                instructions="What is this message about?",
                criteria=CATEGORIES,
            ),
            "urgency": Score(
                instructions="How urgently does this message need a response?",
                criteria=URGENCY_LEVELS,
            ),
            "human_attention": Noul(
                instructions="A human needs to personally handle this message.",
                criteria={
                    "true": "Needs a person to act, decide or reply",
                    "false": "Can be handled automatically or just acknowledged",
                },
            ),
        },
    )

    category = response.answers["category"]
    urgency = response.answers["urgency"]
    human = response.answers["human_attention"]

    # Score returns an expected level between 0 and len(levels) - 1; scale it to 0-10.
    max_level = len(URGENCY_LEVELS) - 1
    needs_human = human.noul >= 0.5

    return Analysis(
        category=category.choice,
        category_confidence=category.confidence,
        urgency=round(urgency.score / max_level * 10, 1),
        urgency_label=URGENCY_LEVELS[round(urgency.score)],
        urgency_confidence=urgency.confidence,
        human_attention=needs_human,
        human_attention_confidence=human.noul if needs_human else 1 - human.noul,
    )


if __name__ == "__main__":
    for message in EXAMPLES.values():
        result = analyze(message)
        print(message)
        print(f"  Category:        {result.category} ({result.category_confidence:.0%})")
        print(f"  Urgency:         {result.urgency} / 10, {result.urgency_label} ({result.urgency_confidence:.0%})")
        print(f"  Human attention: {'Yes' if result.human_attention else 'No'} ({result.human_attention_confidence:.0%})")
        print()
