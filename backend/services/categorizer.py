CATEGORIES = ["Software", "Hardware", "Travel", "Food", "Office Supplies", "Marketing", "Other"]

_KEYWORDS: dict[str, list[str]] = {
    "Software": ["software", "saas", "subscription", "license", "adobe", "github", "aws", "cloud", "hosting", "domain", "figma", "notion", "slack", "zoom"],
    "Hardware": ["hardware", "laptop", "monitor", "keyboard", "mouse", "cable", "printer", "hard drive", "ssd", "ram", "gpu", "cpu"],
    "Travel": ["uber", "ola", "flight", "airline", "hotel", "airbnb", "train", "bus", "taxi", "fuel", "petrol", "toll", "parking"],
    "Food": ["swiggy", "zomato", "restaurant", "cafe", "coffee", "food", "lunch", "dinner", "breakfast", "grocery", "supermarket"],
    "Office Supplies": ["stationery", "paper", "pen", "notebook", "office", "supplies", "desk", "chair", "whiteboard"],
    "Marketing": ["ads", "advertising", "google ads", "meta ads", "facebook", "instagram", "marketing", "seo", "campaign", "promotion"],
}


def suggest_category(merchant: str, raw_text: str) -> str:
    combined = (merchant + " " + raw_text).lower()
    for category, keywords in _KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    return "Other"
