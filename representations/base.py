# representations/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import re
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class RepresentationResult:
    """Result container for representation processing"""
    mode: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    css_classes: List[str]
    javascript_code: Optional[str] = None
    frontend_config: Optional[Dict[str, Any]] = None

    def dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'mode': self.mode,
            'content': self.content,
            'metadata': self.metadata,
            'css_classes': self.css_classes,
            'javascript_code': self.javascript_code,
            'frontend_config': self.frontend_config
        }

class BaseRepresentation(ABC):
    """Base class for all representation types"""
    
    def __init__(self):
        self.mode_name = self.get_mode_name()
        self.description = self.get_description()
        self.icon = self.get_icon()
        self.category = self.get_category()
    
    @abstractmethod
    def get_mode_name(self) -> str:
        """Return the mode name identifier"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return description of this representation"""
        pass
    
    @abstractmethod
    def get_icon(self) -> str:
        """Return icon for this representation"""
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """Return category of this representation"""
        pass
    
    @abstractmethod
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content and return representation result"""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Get representation information"""
        return {
            'name': self.mode_name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category
        }
    
    # Common utility methods that subclasses can use
    
    def extract_sentences(self, content: str) -> List[str]:
        """Extract sentences from content"""
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_paragraphs(self, content: str) -> List[str]:
        """Extract paragraphs from content"""
        paragraphs = content.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def extract_key_phrases(self, content: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from content"""
        # Simple extraction based on capitalized words and common patterns
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b(?:artificial intelligence|machine learning|deep learning|neural network)\b',  # Common tech terms
            r'\b\w+(?:\s+\w+){0,2}(?=\s+(?:is|are|was|were|can|will|should|could))\b'  # Subject phrases
        ]
        
        phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            phrases.extend([match for match in matches if len(match) > 3])
        
        # Remove duplicates and limit
        unique_phrases = list(dict.fromkeys(phrases))
        return unique_phrases[:max_phrases]
    
    def extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from content (simple NER)"""
        entities = []
        
        # Extract capitalized words/phrases (potential entities)
        capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(capitalized_pattern, content)
        
        for i, match in enumerate(set(matches)):  # Remove duplicates
            entities.append({
                'id': f'entity_{i}',
                'name': match,
                'type': self._classify_entity(match),
                'importance': content.lower().count(match.lower()),
                'description': f'Entity: {match}'
            })
        
        return entities
    
    def _classify_entity(self, entity: str) -> str:
        """Simple entity classification"""
        entity_lower = entity.lower()
        
        # Technology terms
        tech_terms = ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'deep', 'neural', 'network', 'algorithm', 'data', 'quantum', 'computing', 'blockchain', 'internet', 'software', 'hardware', 'computer', 'digital']
        if any(term in entity_lower for term in tech_terms):
            return 'technology'
        
        # Science terms
        science_terms = ['atom', 'molecule', 'dna', 'cell', 'protein', 'electron', 'photon', 'physics', 'chemistry', 'biology']
        if any(term in entity_lower for term in science_terms):
            return 'science'
        
        # Business/Organization terms
        business_terms = ['company', 'corporation', 'business', 'organization', 'enterprise', 'industry', 'market']
        if any(term in entity_lower for term in business_terms):
            return 'organization'
        
        # Default to concept
        return 'concept'
    
    def extract_relationships(self, entities: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction based on proximity and common patterns
        relationship_patterns = [
            (r'(\w+)\s+(?:is|are)\s+(?:a|an|the)?\s*(\w+)', 'is_a'),
            (r'(\w+)\s+(?:has|have|contains?)\s+(\w+)', 'has'),
            (r'(\w+)\s+(?:uses?|utilizes?)\s+(\w+)', 'uses'),
            (r'(\w+)\s+(?:creates?|produces?|generates?)\s+(\w+)', 'creates'),
            (r'(\w+)\s+(?:and|with|plus)\s+(\w+)', 'relates_to'),
            (r'(\w+)\s+(?:enables?|allows?)\s+(\w+)', 'enables'),
            (r'(\w+)\s+(?:requires?|needs?)\s+(\w+)', 'requires')
        ]
        
        for i, (pattern, rel_type) in enumerate(relationship_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                source_entity = self._find_entity_by_name(entities, match[0])
                target_entity = self._find_entity_by_name(entities, match[1])
                
                if source_entity and target_entity:
                    relationships.append({
                        'id': f'rel_{i}_{len(relationships)}',
                        'source': source_entity['id'],
                        'target': target_entity['id'],
                        'relationship': rel_type,
                        'type': 'semantic'
                    })
        
        return relationships
    
    def _find_entity_by_name(self, entities: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
        """Find entity by name (case insensitive)"""
        name_lower = name.lower()
        for entity in entities:
            if name_lower in entity['name'].lower() or entity['name'].lower() in name_lower:
                return entity
        return None
    
    def extract_timeline_events(self, content: str) -> List[Dict[str, Any]]:
        """Extract timeline events from content"""
        events = []
        
        # Date patterns
        date_patterns = [
            (r'\b(\d{4})\b', 'year'),
            (r'\b(\d{1,2}/\d{1,2}/\d{4})\b', 'date'),
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b', 'month_year'),
            (r'\b(early|mid|late)\s+(\d{4}s?)\b', 'period'),
            (r'\b(first|second|third|last)\s+(quarter|half|decade|century)\b', 'relative_period')
        ]
        
        sentences = self.extract_sentences(content)
        
        for sentence in sentences:
            for pattern, date_type in date_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                if matches:
                    for match in matches:
                        event_date = match if isinstance(match, str) else ' '.join(match)
                        events.append({
                            'date': event_date,
                            'event': sentence.strip(),
                            'type': date_type,
                            'importance': len(sentence.split())  # Longer sentences = more important
                        })
                        break  # Only one date pattern per sentence
        
        # Sort by importance and limit
        events.sort(key=lambda x: x['importance'], reverse=True)
        return events[:10]  # Limit to 10 events
    
    def calculate_word_count(self, content: str) -> int:
        """Calculate word count"""
        return len(content.split())
    
    def estimate_read_time(self, content: str, wpm: int = 200) -> str:
        """Estimate reading time"""
        word_count = self.calculate_word_count(content)
        minutes = max(1, word_count // wpm)
        return f"{minutes} min"
    
    def create_summary_points(self, content: str, max_points: int = 5) -> List[str]:
        """Create summary points from content"""
        paragraphs = self.extract_paragraphs(content)
        
        # Take first sentence of each paragraph
        summary_points = []
        for paragraph in paragraphs[:max_points]:
            sentences = self.extract_sentences(paragraph)
            if sentences:
                summary_points.append(sentences[0])
        
        return summary_points
    
    def validate_content(self, content: str) -> bool:
        """Validate that content is suitable for processing"""
        if not content or len(content.strip()) < 10:
            return False
        return True
    
    def get_error_result(self, error_message: str) -> RepresentationResult:
        """Return error result"""
        return RepresentationResult(
            mode=self.mode_name,
            content={
                'error': True,
                'message': error_message,
                'fallback_content': 'Unable to process content for this representation mode.'
            },
            metadata={
                'error': True,
                'processing_time': 0
            },
            css_classes=['error-state'],
            frontend_config={'show_error': True}
        )
