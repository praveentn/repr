# representations/puzzle_based.py - Enhanced version
from typing import Dict, Any, List
import re
import json
import random
from .base import BaseRepresentation, RepresentationResult

class PuzzleBasedRepresentation(BaseRepresentation):
    """Enhanced puzzle-based representation with mini challenges to unlock content"""
    
    def get_mode_name(self) -> str:
        return "puzzle_based"
    
    def get_description(self) -> str:
        return "Unlock information by solving mini challenges - game-based learning"
    
    def get_icon(self) -> str:
        return "🧩"
    
    def get_category(self) -> str:
        return "interactive"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into puzzle-based representation"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for puzzle generation")
        
        try:
            # Segment content into logical chunks
            segments = self.segment_content(content)
            
            # Generate challenges for each segment
            puzzle_segments = []
            for i, segment in enumerate(segments):
                challenge = self.generate_challenge(segment, i)
                puzzle_segment = {
                    'id': f'segment_{i}',
                    'content': self.format_segment_content(segment),
                    'challenge': challenge,
                    'unlocked': i == 0,  # First segment unlocked by default
                    'revealed': False
                }
                puzzle_segments.append(puzzle_segment)
            
            # Calculate metrics
            total_segments = len(puzzle_segments)
            difficulty_levels = [seg['challenge']['difficulty'] for seg in puzzle_segments]
            avg_difficulty = sum(difficulty_levels) / len(difficulty_levels) if difficulty_levels else 1
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'segments': puzzle_segments,
                    'total_segments': total_segments,
                    'completion_stats': {
                        'unlocked_count': 1,  # First segment is unlocked
                        'revealed_count': 0,
                        'solved_count': 0
                    },
                    'instructions': {
                        'solve': "Answer the challenge correctly to unlock the content",
                        'reveal': "Click the reveal button to skip the challenge",
                        'retry': "Try again if your answer is incorrect"
                    }
                },
                metadata={
                    'total_segments': total_segments,
                    'avg_difficulty': round(avg_difficulty, 2),
                    'complexity': 'high' if total_segments > 8 else 'medium' if total_segments > 4 else 'low',
                    'interaction_type': 'puzzle_based',
                    'estimated_time_minutes': total_segments * 2  # Estimate 2 minutes per segment
                },
                css_classes=['puzzle-based', 'interactive', 'game-learning'],
                javascript_code='initializePuzzleMode',
                frontend_config={
                    'container_id': 'puzzle-based-container',
                    'enable_reveal': True,
                    'enable_retry': True,
                    'auto_progress': False
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Error generating puzzle representation: {str(e)}")
    
    def validate_content(self, content: str) -> bool:
        """Validate if content is suitable for puzzle generation"""
        if not content or len(content.strip()) < 100:
            return False
        return True
    
    def segment_content(self, content: str) -> List[str]:
        """Segment content into logical chunks for puzzle creation"""
        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # If we have too few paragraphs, split by sentences
        if len(paragraphs) < 3:
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            # Group sentences into chunks of 2-3
            chunks = []
            current_chunk = []
            for sentence in sentences:
                current_chunk.append(sentence)
                if len(current_chunk) >= 3:
                    chunks.append('. '.join(current_chunk) + '.')
                    current_chunk = []
            
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            
            return chunks[:8]  # Limit to 8 segments
        
        # Limit paragraphs and ensure reasonable length
        segments = []
        for para in paragraphs[:6]:
            if len(para) > 500:
                # Split long paragraphs
                mid = len(para) // 2
                split_point = para.find('. ', mid)
                if split_point != -1:
                    segments.append(para[:split_point + 1])
                    segments.append(para[split_point + 2:])
                else:
                    segments.append(para)
            else:
                segments.append(para)
        
        return segments[:8]  # Limit to 8 segments
    
    def generate_challenge(self, segment: str, index: int) -> Dict[str, Any]:
        """Generate an appropriate challenge for the content segment"""
        # Extract key information from the segment
        key_phrases = self.extract_key_phrases(segment)
        numbers = re.findall(r'\d+', segment)
        
        challenge_types = ['multiple_choice', 'text_input']
        challenge_type = random.choice(challenge_types)
        
        if challenge_type == 'multiple_choice':
            return self.create_multiple_choice_challenge(segment, key_phrases)
        else:
            return self.create_text_input_challenge(segment, key_phrases)
    
    def create_multiple_choice_challenge(self, segment: str, key_phrases: List[str]) -> Dict[str, Any]:
        """Create a multiple choice challenge"""
        # Extract a key concept from the segment
        words = segment.split()
        
        # Find important terms (capitalized words, longer words)
        important_terms = [word.strip('.,!?;:') for word in words 
                          if len(word) > 6 or word[0].isupper()]
        
        if important_terms:
            correct_answer = random.choice(important_terms[:3])
            question = f"Which of the following is mentioned in this section?"
            
            # Generate distractors
            distractors = [
                "Machine learning algorithm",
                "Quantum computing",
                "Artificial intelligence",
                "Data visualization",
                "Neural network",
                "Blockchain technology"
            ]
            
            # Filter out distractors that might be in the text
            clean_distractors = [d for d in distractors if d.lower() not in segment.lower()]
            selected_distractors = random.sample(clean_distractors, min(3, len(clean_distractors)))
            
            options = selected_distractors + [correct_answer]
            random.shuffle(options)
            
            correct_index = options.index(correct_answer)
            
            return {
                'type': 'multiple_choice',
                'question': question,
                'options': options,
                'correct_answer': correct_index,
                'hint': f"Look for key terms mentioned in the text",
                'difficulty': 2
            }
        
        # Fallback question
        return {
            'type': 'multiple_choice',
            'question': "What is the main topic of this section?",
            'options': [
                "Technology and innovation",
                "Historical events", 
                "Scientific research",
                "Business strategy"
            ],
            'correct_answer': 0,
            'hint': "Consider the overall theme of the content",
            'difficulty': 1
        }
    
    def create_text_input_challenge(self, segment: str, key_phrases: List[str]) -> Dict[str, Any]:
        """Create a text input challenge"""
        # Look for numbers in the text
        numbers = re.findall(r'\b\d+\b', segment)
        
        if numbers:
            number = random.choice(numbers)
            # Create a simple question about the number
            context = self.find_number_context(segment, number)
            
            return {
                'type': 'text_input',
                'question': f"What number is mentioned in the context of: {context}?",
                'correct_answer': [number, str(number)],
                'hint': "Look for numerical values in the text",
                'difficulty': 2
            }
        
        # Look for key terms
        if key_phrases:
            key_phrase = random.choice(key_phrases[:2])
            simplified_phrase = key_phrase.lower().strip('.,!?;:')
            
            return {
                'type': 'text_input',
                'question': f"Fill in the blank: One important concept mentioned is ______",
                'correct_answer': [simplified_phrase, key_phrase.lower()],
                'hint': f"It's a key term that starts with '{simplified_phrase[0]}'",
                'difficulty': 3
            }
        
        # Fallback question
        return {
            'type': 'text_input',
            'question': "What is one key word that summarizes this section?",
            'correct_answer': ["information", "knowledge", "data", "content"],
            'hint': "Think about what this section is trying to convey",
            'difficulty': 1
        }
    
    def find_number_context(self, text: str, number: str) -> str:
        """Find context around a number in the text"""
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if number in sentence:
                words = sentence.split()
                for i, word in enumerate(words):
                    if number in word:
                        # Get surrounding context
                        start = max(0, i - 3)
                        end = min(len(words), i + 4)
                        context_words = words[start:end]
                        context = ' '.join(context_words)
                        return context.strip()[:50] + "..."
        
        return "numerical information"
    
    def format_segment_content(self, segment: str) -> str:
        """Format segment content for display"""
        # Basic HTML formatting
        # Add paragraph breaks
        formatted = segment.replace('\n', '<br>')
        
        # Bold important terms (simple heuristic)
        words = formatted.split()
        for i, word in enumerate(words):
            clean_word = word.strip('.,!?;:')
            if len(clean_word) > 8 and clean_word[0].isupper():
                words[i] = f"<strong>{word}</strong>"
        
        return ' '.join(words)
    
    def extract_key_phrases(self, content: str, max_phrases: int = 5) -> List[str]:
        """Extract key phrases from content"""
        # Simple extraction based on capitalized words and important patterns
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b[a-z]+(?:ing|tion|sion|ment|ness)\b',  # Important suffixes
        ]
        
        phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            phrases.extend(matches)
        
        # Remove duplicates and filter
        unique_phrases = list(set(phrases))
        filtered_phrases = [p for p in unique_phrases if len(p) > 3 and len(p) < 30]
        
        return filtered_phrases[:max_phrases]
    
    def get_error_result(self, message: str) -> RepresentationResult:
        """Create error result for puzzle mode"""
        return RepresentationResult(
            mode=self.mode_name,
            content={
                'error': True,
                'message': message,
                'segments': [{
                    'id': 'error_segment',
                    'content': f"<p class='text-red-600'>{message}</p>",
                    'challenge': {
                        'type': 'text_input',
                        'question': "What would you like to learn about?",
                        'correct_answer': ["anything", "something", "knowledge"],
                        'hint': "Try asking a different question",
                        'difficulty': 1
                    },
                    'unlocked': True,
                    'revealed': False
                }],
                'total_segments': 1,
                'completion_stats': {
                    'unlocked_count': 1,
                    'revealed_count': 0,
                    'solved_count': 0
                }
            },
            metadata={
                'error': True,
                'total_segments': 1,
                'avg_difficulty': 1,
                'complexity': 'low',
                'interaction_type': 'puzzle_based'
            },
            css_classes=['puzzle-based', 'error']
        )