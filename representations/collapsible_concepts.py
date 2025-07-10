# representations/collapsible_concepts.py
from typing import Dict, Any, List
import re
from .base import BaseRepresentation, RepresentationResult

class CollapsibleConceptsRepresentation(BaseRepresentation):
    """Collapsible concepts representation with hierarchical structure"""
    
    def get_mode_name(self) -> str:
        return "collapsible_concepts"
    
    def get_description(self) -> str:
        return "Nested, expandable concept trees for hierarchical learning"
    
    def get_icon(self) -> str:
        return "🧩"
    
    def get_category(self) -> str:
        return "interactive"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into collapsible concepts representation"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for concept extraction")
        
        try:
            # Extract hierarchical concepts
            concepts = self.extract_hierarchical_concepts(content)
            
            # Calculate metrics
            total_concepts = self.count_total_concepts(concepts)
            max_depth = self.calculate_max_depth(concepts)
            complexity = self.assess_complexity(total_concepts, max_depth)
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'concepts': concepts,
                    'hierarchy_stats': {
                        'total_concepts': total_concepts,
                        'max_depth': max_depth,
                        'root_concepts': len(concepts)
                    }
                },
                metadata={
                    'total_concepts': total_concepts,
                    'max_depth': max_depth,
                    'complexity': complexity,
                    'interaction_type': 'expandable'
                },
                css_classes=['collapsible-concepts', 'hierarchical', 'interactive'],
                javascript_code='initializeCollapsibleConcepts',
                frontend_config={
                    'container_id': 'collapsible-concepts',
                    'auto_expand_first': True,
                    'enable_search': True,
                    'animation_duration': 300
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Failed to generate collapsible concepts: {str(e)}")
    
    def extract_hierarchical_concepts(self, content: str) -> List[Dict[str, Any]]:
        """Extract concepts and organize them hierarchically"""
        paragraphs = self.extract_paragraphs(content)
        concepts = []
        
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
            
            # Extract main concept from paragraph
            main_concept = self.extract_main_concept_from_paragraph(paragraph)
            
            # Extract sub-concepts
            sub_concepts = self.extract_sub_concepts(paragraph, main_concept)
            
            # Create concept object
            concept = {
                'id': f'concept_{i}',
                'title': main_concept['title'],
                'content': main_concept['content'],
                'level': 1,
                'icon': self.get_concept_icon(main_concept['type']),
                'type': main_concept['type'],
                'expanded': i == 0,  # First concept expanded by default
                'children': sub_concepts
            }
            
            concepts.append(concept)
        
        # Enhance with relationships
        self.add_concept_relationships(concepts, content)
        
        return concepts
    
    def extract_main_concept_from_paragraph(self, paragraph: str) -> Dict[str, Any]:
        """Extract the main concept from a paragraph"""
        sentences = self.extract_sentences(paragraph)
        
        if not sentences:
            return {
                'title': 'Unknown Concept',
                'content': paragraph,
                'type': 'general'
            }
        
        # Use first sentence as title, but clean it up
        first_sentence = sentences[0].strip()
        
        # Extract a good title from the first sentence
        title = self.extract_concept_title(first_sentence)
        
        # Classify the concept type
        concept_type = self.classify_concept_type(paragraph)
        
        return {
            'title': title,
            'content': paragraph.strip(),
            'type': concept_type
        }
    
    def extract_concept_title(self, sentence: str) -> str:
        """Extract a good title from a sentence"""
        # Remove common sentence starters
        sentence = re.sub(r'^(The|A|An|This|That|These|Those|In|On|At|For|With|By)\s+', '', sentence, flags=re.IGNORECASE)
        
        # Try to find the main subject
        # Look for patterns like "X is..." or "X are..."
        match = re.match(r'^([^,\.]{1,50}?)\s+(?:is|are|was|were|can|will|should|could|would|has|have|represents?|means?)', sentence, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if len(title) > 10 and len(title) < 60:
                return self.clean_title(title)
        
        # Fallback: take first meaningful phrase
        words = sentence.split()
        if len(words) > 1:
            # Take first 3-8 words depending on length
            word_count = min(8, max(3, len(words) // 3))
            title = ' '.join(words[:word_count])
            return self.clean_title(title)
        
        return self.clean_title(sentence[:50])
    
    def clean_title(self, title: str) -> str:
        """Clean up a title"""
        # Remove trailing punctuation
        title = re.sub(r'[,\.;:!?]+$', '', title)
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title.strip()
    
    def classify_concept_type(self, content: str) -> str:
        """Classify the type of concept"""
        content_lower = content.lower()
        
        # Technology concepts
        tech_keywords = ['technology', 'software', 'hardware', 'algorithm', 'system', 'computer', 'digital', 'internet', 'network', 'database', 'programming', 'code']
        if any(keyword in content_lower for keyword in tech_keywords):
            return 'technology'
        
        # Process concepts
        process_keywords = ['process', 'method', 'procedure', 'approach', 'technique', 'strategy', 'workflow', 'steps', 'stages']
        if any(keyword in content_lower for keyword in process_keywords):
            return 'process'
        
        # Definition concepts
        definition_keywords = ['definition', 'meaning', 'refers to', 'defined as', 'means', 'is the', 'concept of']
        if any(keyword in content_lower for keyword in definition_keywords):
            return 'definition'
        
        # Example concepts
        example_keywords = ['example', 'instance', 'case', 'illustration', 'demonstration', 'for example']
        if any(keyword in content_lower for keyword in example_keywords):
            return 'example'
        
        # Benefit/advantage concepts
        benefit_keywords = ['benefit', 'advantage', 'positive', 'improvement', 'enhancement', 'value', 'gain']
        if any(keyword in content_lower for keyword in benefit_keywords):
            return 'benefit'
        
        # Challenge/problem concepts
        challenge_keywords = ['challenge', 'problem', 'issue', 'difficulty', 'limitation', 'drawback', 'disadvantage']
        if any(keyword in content_lower for keyword in challenge_keywords):
            return 'challenge'
        
        return 'general'
    
    def extract_sub_concepts(self, paragraph: str, main_concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sub-concepts from a paragraph"""
        sentences = self.extract_sentences(paragraph)
        sub_concepts = []
        
        # Skip first sentence (used for main concept)
        for i, sentence in enumerate(sentences[1:], 1):
            if len(sentence.strip()) < 20:  # Skip very short sentences
                continue
            
            # Look for sub-concept indicators
            if self.is_sub_concept(sentence):
                sub_title = self.extract_sub_concept_title(sentence)
                sub_type = self.classify_sub_concept_type(sentence)
                
                sub_concept = {
                    'id': f'{main_concept.get("title", "concept")}_sub_{i}',
                    'title': sub_title,
                    'content': sentence.strip(),
                    'level': 2,
                    'type': sub_type,
                    'icon': self.get_concept_icon(sub_type),
                    'children': []
                }
                
                sub_concepts.append(sub_concept)
        
        return sub_concepts[:5]  # Limit sub-concepts to avoid overcrowding
    
    def is_sub_concept(self, sentence: str) -> bool:
        """Check if a sentence represents a sub-concept"""
        sentence_lower = sentence.lower()
        
        # Sub-concept indicators
        indicators = [
            'first', 'second', 'third', 'finally', 'additionally', 'furthermore',
            'also', 'moreover', 'in addition', 'another', 'specifically',
            'for example', 'such as', 'including', 'like', 'particularly'
        ]
        
        # Check for numbered lists
        if re.match(r'^\s*\d+[\.\)]\s*', sentence):
            return True
        
        # Check for bullet point indicators
        if re.match(r'^\s*[-\*\•]\s*', sentence):
            return True
        
        # Check for sub-concept indicators
        return any(indicator in sentence_lower for indicator in indicators)
    
    def extract_sub_concept_title(self, sentence: str) -> str:
        """Extract title for a sub-concept"""
        # Remove list indicators
        sentence = re.sub(r'^\s*\d+[\.\)]\s*', '', sentence)
        sentence = re.sub(r'^\s*[-\*\•]\s*', '', sentence)
        
        # Extract title similar to main concept
        title = self.extract_concept_title(sentence)
        
        # If title is too long, truncate
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title
    
    def classify_sub_concept_type(self, sentence: str) -> str:
        """Classify sub-concept type"""
        sentence_lower = sentence.lower()
        
        if any(keyword in sentence_lower for keyword in ['step', 'stage', 'phase']):
            return 'step'
        elif any(keyword in sentence_lower for keyword in ['feature', 'characteristic', 'property']):
            return 'feature'
        elif any(keyword in sentence_lower for keyword in ['example', 'instance', 'case']):
            return 'example'
        elif any(keyword in sentence_lower for keyword in ['benefit', 'advantage']):
            return 'benefit'
        elif any(keyword in sentence_lower for keyword in ['requirement', 'need', 'prerequisite']):
            return 'requirement'
        
        return 'detail'
    
    def get_concept_icon(self, concept_type: str) -> str:
        """Get icon for concept type"""
        icon_map = {
            'technology': '💻',
            'process': '⚙️',
            'definition': '📖',
            'example': '💡',
            'benefit': '✅',
            'challenge': '⚠️',
            'step': '📋',
            'feature': '🔧',
            'requirement': '📋',
            'detail': '🔍',
            'general': '📝'
        }
        
        return icon_map.get(concept_type, '📝')
    
    def add_concept_relationships(self, concepts: List[Dict[str, Any]], content: str):
        """Add relationships between concepts"""
        # Simple relationship detection based on cross-references
        for concept in concepts:
            concept['related_concepts'] = []
            
            for other_concept in concepts:
                if concept['id'] != other_concept['id']:
                    # Check if concepts are related by looking for mentions
                    if self.concepts_are_related(concept, other_concept, content):
                        concept['related_concepts'].append(other_concept['id'])
    
    def concepts_are_related(self, concept1: Dict[str, Any], concept2: Dict[str, Any], content: str) -> bool:
        """Check if two concepts are related"""
        # Simple heuristic: if key terms from one concept appear in the other
        concept1_keywords = self.extract_keywords_from_concept(concept1)
        concept2_keywords = self.extract_keywords_from_concept(concept2)
        
        # Check for keyword overlap
        overlap = set(concept1_keywords).intersection(set(concept2_keywords))
        return len(overlap) > 0
    
    def extract_keywords_from_concept(self, concept: Dict[str, Any]) -> List[str]:
        """Extract keywords from a concept"""
        text = f"{concept['title']} {concept['content']}"
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'this', 'that', 'these', 'those'}
        
        keywords = [word for word in words if word not in common_words]
        
        # Return top keywords
        return list(set(keywords))[:5]
    
    def count_total_concepts(self, concepts: List[Dict[str, Any]]) -> int:
        """Count total number of concepts including sub-concepts"""
        total = len(concepts)
        for concept in concepts:
            total += len(concept.get('children', []))
        return total
    
    def calculate_max_depth(self, concepts: List[Dict[str, Any]]) -> int:
        """Calculate maximum depth of concept hierarchy"""
        max_depth = 1  # At least 1 level
        
        for concept in concepts:
            if concept.get('children'):
                max_depth = max(max_depth, 2)  # Currently only 2 levels supported
        
        return max_depth
    
    def assess_complexity(self, total_concepts: int, max_depth: int) -> str:
        """Assess complexity of concept structure"""
        if total_concepts > 15 or max_depth > 2:
            return 'high'
        elif total_concepts > 8 or max_depth > 1:
            return 'medium'
        else:
            return 'low'