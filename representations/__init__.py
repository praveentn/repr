# representations/__init__.py
from .base import BaseRepresentation, RepresentationResult
from .knowledge_graph import KnowledgeGraphRepresentation
from .plain_text import PlainTextRepresentation
from .color_coded import ColorCodedRepresentation
from .collapsible_concepts import CollapsibleConceptsRepresentation
from .summary import SummaryRepresentation
from .timeline import TimelineRepresentation
from .puzzle_based import PuzzleBasedRepresentation

__all__ = [
    'BaseRepresentation',
    'RepresentationResult',
    'KnowledgeGraphRepresentation',
    'PlainTextRepresentation',
    'ColorCodedRepresentation',
    'CollapsibleConceptsRepresentation',
    'SummaryRepresentation',
    'TimelineRepresentation',
    'PuzzleBasedRepresentation'
]