from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class UserPreferences:
    keep_preference: str = 'newest'  # newest|oldest|largest|smallest
    deletion_method: str = 'recycle'  # recycle|permanent
    filters_enabled: bool = False
    extensions: Set[str] = field(default_factory=set)
    min_size: int = 0
    max_size: int = 0
    size_unit: str = 'KB'
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)
    scoring_enabled: bool = True
    score_weights: Dict[str, float] = field(default_factory=lambda: {
        'recency': 0.3,
        'size': 0.2,
        'location': 0.2,
        'extension': 0.1,
        'name': 0.2
    })

    def validate(self) -> bool:
        return (self.max_size == 0 or self.min_size <= self.max_size) and \
               self.keep_preference in ('newest', 'oldest', 'largest', 'smallest') 