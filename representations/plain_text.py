# representations/plain_text.py
from typing import Dict, Any
from .base import BaseRepresentation, RepresentationResult

class PlainTextRepresentation(BaseRepresentation):
    """Plain text representation with basic formatting"""
    
    def get_mode_name(self) -> str:
        return "plain_text"
    
    def get_description(self) -> str:
        return "Simple, clean text format"
    
    def get_icon(self) -> str:
        return "📝"
    
    def get_category(self) -> str:
        return "basic"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into plain text representation"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for processing")
        
        try:
            # Clean and format the content
            formatted_content = self.format_plain_text(content)
            
            # Calculate metrics
            word_count = self.calculate_word_count(content)
            read_time = self.estimate_read_time(content)
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'text': content,
                    'formatted': formatted_content,
                    'paragraphs': self.extract_paragraphs(content),
                    'word_count': word_count,
                    'read_time': read_time
                },
                metadata={
                    'word_count': word_count,
                    'estimated_read_time': read_time,
                    'paragraph_count': len(self.extract_paragraphs(content)),
                    'complexity': 'low'
                },
                css_classes=['plain-text', 'readable'],
                frontend_config={
                    'enable_copy': True,
                    'enable_print': True,
                    'font_family': 'Inter, sans-serif'
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Failed to process plain text: {str(e)}")
    
    def format_plain_text(self, content: str) -> str:
        """Format content for HTML display"""
        # Convert newlines to HTML breaks
        formatted = content.replace('\n\n', '</p><p>')
        formatted = formatted.replace('\n', '<br>')
        
        # Wrap in paragraph tags
        if not formatted.startswith('<p>'):
            formatted = f'<p>{formatted}</p>'
        
        # Basic text enhancements
        formatted = self.enhance_text_formatting(formatted)
        
        return formatted
    
    def enhance_text_formatting(self, text: str) -> str:
        """Add basic text enhancements"""
        import re
        
        # Bold for emphasized words (words in asterisks)
        text = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', text)
        
        # Italic for emphasized words (words in underscores)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
        
        # Highlight technical terms
        tech_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'algorithm', 'blockchain', 'quantum computing',
            'cloud computing', 'big data', 'internet of things', 'cybersecurity'
        ]
        
        for term in tech_terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            text = pattern.sub(f'<span class="tech-term">{term}</span>', text)
        
        return text
