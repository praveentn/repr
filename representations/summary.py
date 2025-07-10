# representations/summary.py
from typing import Dict, Any, List
import re
from .base import BaseRepresentation, RepresentationResult

class SummaryRepresentation(BaseRepresentation):
    """Summary representation with key points and TL;DR"""
    
    def get_mode_name(self) -> str:
        return "summary"
    
    def get_description(self) -> str:
        return "Concise key points and executive summary"
    
    def get_icon(self) -> str:
        return "📦"
    
    def get_category(self) -> str:
        return "basic"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into summary representation"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for summarization")
        
        try:
            # Extract key components
            key_points = self.extract_key_points(content)
            tldr = self.generate_tldr(content, key_points)
            main_topics = self.extract_main_topics(content)
            important_quotes = self.extract_important_quotes(content)
            
            # Calculate compression metrics
            original_word_count = self.calculate_word_count(content)
            summary_word_count = self.calculate_word_count(' '.join(key_points) + ' ' + tldr)
            compression_ratio = round(summary_word_count / original_word_count, 2) if original_word_count > 0 else 0
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'tldr': tldr,
                    'key_points': key_points,
                    'main_topics': main_topics,
                    'important_quotes': important_quotes,
                    'full_content': content,
                    'metrics': {
                        'original_words': original_word_count,
                        'summary_words': summary_word_count,
                        'compression_ratio': compression_ratio,
                        'key_points_count': len(key_points)
                    }
                },
                metadata={
                    'compression_ratio': compression_ratio,
                    'key_point_count': len(key_points),
                    'main_topics_count': len(main_topics),
                    'summary_quality': self.assess_summary_quality(key_points, main_topics)
                },
                css_classes=['summary', 'condensed', 'key-points'],
                frontend_config={
                    'enable_expand': True,
                    'show_metrics': True,
                    'highlight_key_points': True
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Failed to generate summary: {str(e)}")
    
    def extract_key_points(self, content: str, max_points: int = 6) -> List[str]:
        """Extract key points from content using multiple strategies"""
        paragraphs = self.extract_paragraphs(content)
        sentences = self.extract_sentences(content)
        
        key_points = []
        
        # Strategy 1: First sentence of each paragraph (topic sentences)
        for paragraph in paragraphs[:max_points]:
            paragraph_sentences = self.extract_sentences(paragraph)
            if paragraph_sentences:
                first_sentence = paragraph_sentences[0].strip()
                if len(first_sentence) > 20 and first_sentence not in key_points:
                    key_points.append(first_sentence)
        
        # Strategy 2: Sentences with importance indicators
        importance_indicators = [
            'important', 'key', 'main', 'primary', 'essential', 'critical',
            'significant', 'major', 'crucial', 'fundamental', 'core',
            'in summary', 'to conclude', 'overall', 'therefore', 'thus',
            'as a result', 'consequently', 'in conclusion'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if (any(indicator in sentence_lower for indicator in importance_indicators) and
                len(sentence) > 30 and sentence not in key_points):
                key_points.append(sentence.strip())
        
        # Strategy 3: Sentences with numbers/statistics (often important)
        for sentence in sentences:
            if (re.search(r'\d+(\.\d+)?%|\d+(\,\d{3})*(\.\d+)?', sentence) and
                len(sentence) > 25 and sentence not in key_points):
                key_points.append(sentence.strip())
        
        # Strategy 4: Sentences with definitions or explanations
        definition_patterns = [
            r'.+\s+is\s+.+',
            r'.+\s+are\s+.+',
            r'.+\s+means\s+.+',
            r'.+\s+refers to\s+.+',
            r'.+\s+defined as\s+.+'
        ]
        
        for sentence in sentences:
            if (any(re.search(pattern, sentence, re.IGNORECASE) for pattern in definition_patterns) and
                len(sentence) > 30 and sentence not in key_points):
                key_points.append(sentence.strip())
        
        # Remove duplicates while preserving order and limit
        seen = set()
        unique_key_points = []
        for point in key_points:
            if point not in seen and len(unique_key_points) < max_points:
                seen.add(point)
                unique_key_points.append(point)
        
        return unique_key_points
    
    def generate_tldr(self, content: str, key_points: List[str]) -> str:
        """Generate TL;DR from content and key points"""
        # If we have key points, use the most important one
        if key_points:
            # Find the most comprehensive key point
            best_point = max(key_points, key=lambda x: len(x.split()))
            
            # Enhance it with context
            main_topic = self.extract_main_topic(content)
            if main_topic and main_topic.lower() not in best_point.lower():
                return f"About {main_topic}: {best_point}"
            return best_point
        
        # Fallback: use first substantial sentence
        sentences = self.extract_sentences(content)
        for sentence in sentences:
            if len(sentence) > 50:
                return sentence.strip()
        
        # Final fallback
        words = content.split()
        if len(words) > 20:
            return ' '.join(words[:20]) + "..."
        
        return "Summary not available for this content."
    
    def extract_main_topics(self, content: str, max_topics: int = 5) -> List[str]:
        """Extract main topics from content"""
        # Extract frequent important terms
        key_phrases = self.extract_key_phrases(content)
        
        # Extract capitalized terms (proper nouns, concepts)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Combine and rank by frequency
        all_terms = key_phrases + capitalized_terms
        term_frequency = {}
        
        for term in all_terms:
            term_clean = term.strip()
            if len(term_clean) > 3:
                term_frequency[term_clean] = term_frequency.get(term_clean, 0) + 1
        
        # Sort by frequency and filter
        sorted_terms = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Return top terms, avoiding duplicates
        topics = []
        for term, freq in sorted_terms:
            if len(topics) >= max_topics:
                break
            
            # Avoid adding terms that are substrings of existing topics
            if not any(term.lower() in existing.lower() or existing.lower() in term.lower() 
                      for existing in topics):
                topics.append(term)
        
        return topics
    
    def extract_main_topic(self, content: str) -> str:
        """Extract the single main topic of the content"""
        topics = self.extract_main_topics(content, max_topics=1)
        return topics[0] if topics else "General Information"
    
    def extract_important_quotes(self, content: str, max_quotes: int = 3) -> List[str]:
        """Extract important quotes or notable statements"""
        sentences = self.extract_sentences(content)
        quotes = []
        
        # Look for sentences with quotation marks
        quoted_sentences = [s for s in sentences if '"' in s or "'" in s]
        quotes.extend(quoted_sentences[:max_quotes])
        
        # Look for sentences with strong statements
        strong_indicators = [
            'according to', 'research shows', 'studies indicate', 'experts say',
            'it is proven', 'evidence suggests', 'data reveals', 'findings show'
        ]
        
        for sentence in sentences:
            if (any(indicator in sentence.lower() for indicator in strong_indicators) and
                len(quotes) < max_quotes and sentence not in quotes):
                quotes.append(sentence)
        
        # Look for sentences with statistical claims
        for sentence in sentences:
            if (re.search(r'\d+(\.\d+)?%|\d+(\,\d{3})*(\.\d+)?', sentence) and
                len(quotes) < max_quotes and sentence not in quotes):
                quotes.append(sentence)
        
        return quotes[:max_quotes]
    
    def assess_summary_quality(self, key_points: List[str], main_topics: List[str]) -> str:
        """Assess the quality of the generated summary"""
        key_points_count = len(key_points)
        topics_count = len(main_topics)
        
        if key_points_count >= 4 and topics_count >= 3:
            return 'high'
        elif key_points_count >= 2 and topics_count >= 2:
            return 'medium'
        else:
            return 'low'
        