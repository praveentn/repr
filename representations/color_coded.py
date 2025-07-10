# representations/color_coded.py
from typing import Dict, Any, List
import re
from .base import BaseRepresentation, RepresentationResult

class ColorCodedRepresentation(BaseRepresentation):
    """Color-coded representation with categorized sections"""
    
    def get_mode_name(self) -> str:
        return "color_coded"
    
    def get_description(self) -> str:
        return "Color-tagged sections with legend (facts, assumptions, examples, warnings)"
    
    def get_icon(self) -> str:
        return "🎨"
    
    def get_category(self) -> str:
        return "visual"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into color-coded representation"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for color coding")
        
        try:
            # Extract and categorize content sections
            sections = self.categorize_content(content)
            
            # Create legend
            legend = self.create_legend()
            
            # Calculate statistics
            total_sections = sum(len(section_list) for section_list in sections.values())
            dominant_type = max(sections.keys(), key=lambda k: len(sections[k])) if sections else "facts"
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'sections': sections,
                    'legend': legend,
                    'statistics': {
                        'total_sections': total_sections,
                        'facts_count': len(sections.get('facts', [])),
                        'assumptions_count': len(sections.get('assumptions', [])),
                        'examples_count': len(sections.get('examples', [])),
                        'warnings_count': len(sections.get('warnings', []))
                    }
                },
                metadata={
                    'sections_count': total_sections,
                    'dominant_type': dominant_type,
                    'complexity': 'medium' if total_sections > 10 else 'low'
                },
                css_classes=['color-coded', 'with-legend', 'categorized'],
                frontend_config={
                    'enable_section_toggle': True,
                    'enable_category_filter': True,
                    'animation_enabled': True
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Failed to generate color-coded representation: {str(e)}")
    
    def categorize_content(self, content: str) -> Dict[str, List[str]]:
        """Categorize content into different sections"""
        sections = {
            'facts': [],
            'assumptions': [],
            'examples': [],
            'warnings': []
        }
        
        sentences = self.extract_sentences(content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Categorize each sentence
            category = self.classify_sentence(sentence)
            sections[category].append(sentence)
        
        return sections
    
    def classify_sentence(self, sentence: str) -> str:
        """Classify a sentence into one of the four categories"""
        sentence_lower = sentence.lower()
        
        # Warning indicators (highest priority)
        warning_indicators = [
            'warning', 'danger', 'risk', 'caution', 'avoid', 'harmful', 'unsafe',
            'threat', 'vulnerability', 'security', 'breach', 'attack', 'malicious',
            'beware', 'careful', 'critical', 'urgent', 'important to note',
            'however', 'but', 'limitation', 'drawback', 'disadvantage', 'problem',
            'issue', 'concern', 'challenge', 'difficulty'
        ]
        
        if any(indicator in sentence_lower for indicator in warning_indicators):
            return 'warnings'
        
        # Example indicators
        example_indicators = [
            'example', 'instance', 'such as', 'like', 'for example', 'for instance',
            'e.g.', 'namely', 'including', 'consider', 'suppose', 'imagine',
            'case study', 'demonstration', 'illustration', 'sample'
        ]
        
        if any(indicator in sentence_lower for indicator in example_indicators):
            return 'examples'
        
        # Assumption indicators
        assumption_indicators = [
            'assume', 'assuming', 'likely', 'probably', 'might', 'could', 'may',
            'perhaps', 'possibly', 'potentially', 'presumably', 'supposedly',
            'theoretically', 'hypothetically', 'arguably', 'seemingly', 'appears',
            'suggests', 'implies', 'indicates', 'seems', 'tends to', 'often',
            'usually', 'typically', 'generally', 'commonly', 'frequently'
        ]
        
        if any(indicator in sentence_lower for indicator in assumption_indicators):
            return 'assumptions'
        
        # Fact indicators
        fact_indicators = [
            'fact', 'data', 'research', 'study', 'evidence', 'proof', 'demonstrated',
            'shown', 'proven', 'established', 'confirmed', 'verified', 'validated',
            'measured', 'observed', 'recorded', 'documented', 'published',
            'according to', 'based on', 'statistics', 'findings', 'results',
            'conclusion', 'analysis', 'survey', 'experiment', 'test'
        ]
        
        if any(indicator in sentence_lower for indicator in fact_indicators):
            return 'facts'
        
        # Advanced classification based on sentence structure
        return self.classify_by_structure(sentence)
    
    def classify_by_structure(self, sentence: str) -> str:
        """Classify sentence based on linguistic structure"""
        sentence_lower = sentence.lower()
        
        # Questions often indicate uncertainty or assumptions
        if sentence.strip().endswith('?'):
            return 'assumptions'
        
        # Sentences with numbers/percentages often indicate facts
        if re.search(r'\d+(\.\d+)?%|\d+(\,\d{3})*(\.\d+)?', sentence):
            return 'facts'
        
        # Sentences starting with specific patterns
        if re.match(r'^(it is|this is|that is|there are|there is)', sentence_lower):
            return 'facts'
        
        if re.match(r'^(if|when|while|although|unless)', sentence_lower):
            return 'assumptions'
        
        # Conditional statements
        if 'if' in sentence_lower and ('then' in sentence_lower or 'would' in sentence_lower):
            return 'assumptions'
        
        # Imperative sentences (commands/warnings)
        imperative_starters = ['do not', 'avoid', 'make sure', 'ensure', 'remember', 'be careful']
        if any(sentence_lower.startswith(starter) for starter in imperative_starters):
            return 'warnings'
        
        # Default to facts for definitional or descriptive sentences
        return 'facts'
    
    def create_legend(self) -> Dict[str, Dict[str, str]]:
        """Create legend for color-coded sections"""
        return {
            'facts': {
                'color': 'blue',
                'bg_color': 'bg-blue-50',
                'border_color': 'border-blue-400',
                'text_color': 'text-blue-800',
                'label': 'Key Facts & Data',
                'icon': '📊',
                'description': 'Verified information, research findings, and established facts'
            },
            'assumptions': {
                'color': 'yellow',
                'bg_color': 'bg-yellow-50',
                'border_color': 'border-yellow-400',
                'text_color': 'text-yellow-800',
                'label': 'Assumptions & Hypotheses',
                'icon': '❓',
                'description': 'Uncertain elements, assumptions, and hypothetical scenarios'
            },
            'examples': {
                'color': 'green',
                'bg_color': 'bg-green-50',
                'border_color': 'border-green-400',
                'text_color': 'text-green-800',
                'label': 'Examples & Illustrations',
                'icon': '💡',
                'description': 'Concrete examples, case studies, and practical instances'
            },
            'warnings': {
                'color': 'red',
                'bg_color': 'bg-red-50',
                'border_color': 'border-red-400',
                'text_color': 'text-red-800',
                'label': 'Warnings & Risks',
                'icon': '⚠️',
                'description': 'Important warnings, risks, limitations, and concerns'
            }
        }