# representations/timeline.py
from typing import Dict, Any, List, Tuple
import re
from datetime import datetime
from .base import BaseRepresentation, RepresentationResult

class TimelineRepresentation(BaseRepresentation):
    """Timeline representation with chronological visualization"""
    
    def get_mode_name(self) -> str:
        return "timeline"
    
    def get_description(self) -> str:
        return "Chronological evolution view with interactive timeline"
    
    def get_icon(self) -> str:
        return "⏳"
    
    def get_category(self) -> str:
        return "temporal"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into timeline representation"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for timeline generation")
        
        try:
            # Extract timeline events
            events = self.extract_timeline_events_enhanced(content)
            
            if not events:
                return self.get_error_result("No temporal events found in content")
            
            # Sort and organize events
            sorted_events = self.sort_events_chronologically(events)
            
            # Calculate timeline metrics
            timeline_span = self.calculate_timeline_span(sorted_events)
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'events': sorted_events,
                    'timeline_config': self.create_timeline_config(sorted_events),
                    'stats': {
                        'event_count': len(sorted_events),
                        'timeline_span': timeline_span,
                        'start_period': sorted_events[0]['period'] if sorted_events else None,
                        'end_period': sorted_events[-1]['period'] if sorted_events else None
                    }
                },
                metadata={
                    'event_count': len(sorted_events),
                    'timeline_span': timeline_span,
                    'complexity': 'high' if len(sorted_events) > 10 else 'medium' if len(sorted_events) > 5 else 'low'
                },
                css_classes=['timeline', 'chronological', 'interactive'],
                javascript_code='initializeTimeline',
                frontend_config={
                    'container_id': 'timeline-container',
                    'enable_zoom': True,
                    'enable_navigation': True,
                    'show_periods': True
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Failed to generate timeline: {str(e)}")
    
    def extract_timeline_events_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced timeline event extraction"""
        events = []
        sentences = self.extract_sentences(content)
        
        # Enhanced date patterns with more variety
        date_patterns = [
            # Specific years
            (r'\b(\d{4})\b', 'year', self.parse_year),
            
            # Full dates
            (r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', 'date', self.parse_full_date),
            (r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b', 'date', self.parse_iso_date),
            
            # Month and year
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b', 'month_year', self.parse_month_year),
            (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})\b', 'month_year', self.parse_short_month_year),
            
            # Relative periods
            (r'\b(early|mid|late)\s+(\d{4}s?)\b', 'period', self.parse_relative_period),
            (r'\b(\d{4}s)\b', 'decade', self.parse_decade),
            
            # Ordinal periods
            (r'\b(first|second|third|fourth|last)\s+(quarter|half)\s+of\s+(\d{4})\b', 'quarter', self.parse_quarter),
            (r'\b(\d{1,2})(st|nd|rd|th)\s+century\b', 'century', self.parse_century),
            
            # Historical periods
            (r'\b(ancient|medieval|modern|contemporary|prehistoric)\s+(times?|era|period)\b', 'historical', self.parse_historical_period),
            
            # Age indicators
            (r'\b(\d+)\s+years?\s+ago\b', 'years_ago', self.parse_years_ago),
            (r'\b(recently|lately|currently|now|today|tomorrow|yesterday)\b', 'relative_time', self.parse_relative_time)
        ]
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) < 10:
                continue
            
            # Try each pattern
            for pattern, date_type, parser in date_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                
                if matches:
                    for match in matches:
                        try:
                            parsed_date = parser(match)
                            if parsed_date:
                                event = {
                                    'id': f'event_{len(events)}',
                                    'title': self.extract_event_title(sentence),
                                    'description': sentence_clean,
                                    'date_raw': match if isinstance(match, str) else ' '.join(match),
                                    'date_parsed': parsed_date,
                                    'period': parsed_date['period'],
                                    'precision': parsed_date['precision'],
                                    'type': self.classify_event_type(sentence),
                                    'importance': self.calculate_event_importance(sentence),
                                    'icon': self.get_event_icon(self.classify_event_type(sentence))
                                }
                                events.append(event)
                                break  # Only one date per sentence
                        except Exception as e:
                            continue  # Skip problematic dates
        
        # Remove duplicates and sort by importance
        unique_events = self.remove_duplicate_events(events)
        return unique_events
    
    def parse_year(self, match) -> Dict[str, Any]:
        """Parse a year"""
        year = int(match)
        if 1800 <= year <= 2100:  # Reasonable year range
            return {
                'year': year,
                'period': year,
                'precision': 'year',
                'sort_key': year
            }
        return None
    
    def parse_full_date(self, match) -> Dict[str, Any]:
        """Parse full date (MM/DD/YYYY or DD/MM/YYYY)"""
        try:
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y']:
                try:
                    date_obj = datetime.strptime(match, fmt)
                    return {
                        'year': date_obj.year,
                        'month': date_obj.month,
                        'day': date_obj.day,
                        'period': date_obj.year + (date_obj.month - 1) / 12,
                        'precision': 'day',
                        'sort_key': date_obj.year * 10000 + date_obj.month * 100 + date_obj.day
                    }
                except ValueError:
                    continue
        except:
            pass
        return None
    
    def parse_iso_date(self, match) -> Dict[str, Any]:
        """Parse ISO date (YYYY-MM-DD)"""
        try:
            date_obj = datetime.strptime(match, '%Y-%m-%d')
            return {
                'year': date_obj.year,
                'month': date_obj.month,
                'day': date_obj.day,
                'period': date_obj.year + (date_obj.month - 1) / 12,
                'precision': 'day',
                'sort_key': date_obj.year * 10000 + date_obj.month * 100 + date_obj.day
            }
        except:
            return None
    
    def parse_month_year(self, match) -> Dict[str, Any]:
        """Parse month and year"""
        month_name, year = match
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        month_num = month_map.get(month_name.lower())
        if month_num:
            year_int = int(year)
            return {
                'year': year_int,
                'month': month_num,
                'period': year_int + (month_num - 1) / 12,
                'precision': 'month',
                'sort_key': year_int * 100 + month_num
            }
        return None
    
    def parse_short_month_year(self, match) -> Dict[str, Any]:
        """Parse abbreviated month and year"""
        month_abbr, year = match
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month_num = month_map.get(month_abbr.lower().replace('.', ''))
        if month_num:
            year_int = int(year)
            return {
                'year': year_int,
                'month': month_num,
                'period': year_int + (month_num - 1) / 12,
                'precision': 'month',
                'sort_key': year_int * 100 + month_num
            }
        return None
    
    def parse_relative_period(self, match) -> Dict[str, Any]:
        """Parse relative periods like 'early 1990s'"""
        period_type, year_range = match
        
        if year_range.endswith('s'):
            decade = int(year_range[:-1])
        else:
            decade = int(year_range)
        
        period_offset = {
            'early': 0.2,
            'mid': 0.5,
            'late': 0.8
        }.get(period_type.lower(), 0.5)
        
        return {
            'year': decade,
            'period': decade + period_offset,
            'precision': 'period',
            'sort_key': decade * 10 + int(period_offset * 10)
        }
    
    def parse_decade(self, match) -> Dict[str, Any]:
        """Parse decade like '1990s'"""
        decade = int(match[:-1])
        return {
            'year': decade,
            'period': decade + 5,  # Middle of decade
            'precision': 'decade',
            'sort_key': decade
        }
    
    def parse_quarter(self, match) -> Dict[str, Any]:
        """Parse quarters like 'first quarter of 2020'"""
        quarter_word, period_type, year = match
        
        quarter_map = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'last': 4
        }
        
        quarter_num = quarter_map.get(quarter_word.lower(), 2)
        year_int = int(year)
        
        if period_type == 'quarter':
            month = (quarter_num - 1) * 3 + 2  # Middle month of quarter
            period = year_int + (month - 1) / 12
        else:  # half
            month = 3 if quarter_num <= 2 else 9
            period = year_int + (month - 1) / 12
        
        return {
            'year': year_int,
            'quarter': quarter_num,
            'period': period,
            'precision': 'quarter',
            'sort_key': year_int * 10 + quarter_num
        }
    
    def parse_century(self, match) -> Dict[str, Any]:
        """Parse century like '21st century'"""
        century_num, suffix = match
        century = int(century_num)
        
        # Convert to approximate year (middle of century)
        year = (century - 1) * 100 + 50
        
        return {
            'year': year,
            'century': century,
            'period': year,
            'precision': 'century',
            'sort_key': year
        }
    
    def parse_historical_period(self, match) -> Dict[str, Any]:
        """Parse historical periods"""
        period_name = match.lower()
        
        # Approximate mappings for historical periods
        period_map = {
            'ancient': 500,
            'medieval': 1000,
            'modern': 1800,
            'contemporary': 1950,
            'prehistoric': -2000
        }
        
        year = period_map.get(period_name, 1000)
        
        return {
            'year': year,
            'period': year,
            'precision': 'era',
            'sort_key': year
        }
    
    def parse_years_ago(self, match) -> Dict[str, Any]:
        """Parse 'X years ago'"""
        years_ago = int(match)
        current_year = datetime.now().year
        year = current_year - years_ago
        
        return {
            'year': year,
            'period': year,
            'precision': 'relative',
            'sort_key': year
        }
    
    def parse_relative_time(self, match) -> Dict[str, Any]:
        """Parse relative time words"""
        time_word = match.lower()
        current_year = datetime.now().year
        
        time_map = {
            'recently': current_year - 1,
            'lately': current_year - 1,
            'currently': current_year,
            'now': current_year,
            'today': current_year,
            'tomorrow': current_year + 1,
            'yesterday': current_year - 1
        }
        
        year = time_map.get(time_word, current_year)
        
        return {
            'year': year,
            'period': year,
            'precision': 'relative',
            'sort_key': year
        }
    
    def extract_event_title(self, sentence: str) -> str:
        """Extract a concise title for the event"""
        # Remove date patterns to focus on the event
        sentence_clean = re.sub(r'\b\d{4}\b', '', sentence)
        sentence_clean = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', '', sentence_clean, flags=re.IGNORECASE)
        
        # Extract key action or subject
        words = sentence_clean.split()
        
        # Find important verbs and nouns
        important_words = []
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word)
            if len(word_clean) > 3 and word_clean.lower() not in ['this', 'that', 'these', 'those', 'with', 'from', 'they', 'were', 'have', 'been']:
                important_words.append(word_clean)
        
        # Create title from important words
        if important_words:
            title = ' '.join(important_words[:6])  # Take first 6 important words
            if len(title) > 60:
                title = title[:57] + "..."
            return title
        
        # Fallback: use first part of sentence
        if len(sentence) > 60:
            return sentence[:57] + "..."
        return sentence
    
    def classify_event_type(self, sentence: str) -> str:
        """Classify the type of event"""
        sentence_lower = sentence.lower()
        
        # Technology events
        if any(keyword in sentence_lower for keyword in ['invented', 'developed', 'created', 'launched', 'released', 'introduced']):
            return 'innovation'
        
        # Discovery events
        if any(keyword in sentence_lower for keyword in ['discovered', 'found', 'identified', 'observed', 'detected']):
            return 'discovery'
        
        # Business events
        if any(keyword in sentence_lower for keyword in ['founded', 'established', 'company', 'business', 'corporation', 'startup']):
            return 'business'
        
        # Historical events
        if any(keyword in sentence_lower for keyword in ['war', 'battle', 'revolution', 'independence', 'treaty', 'peace']):
            return 'historical'
        
        # Scientific events
        if any(keyword in sentence_lower for keyword in ['research', 'study', 'experiment', 'theory', 'hypothesis', 'published']):
            return 'scientific'
        
        # Personal events
        if any(keyword in sentence_lower for keyword in ['born', 'died', 'married', 'graduated', 'appointed', 'elected']):
            return 'personal'
        
        return 'general'
    
    def calculate_event_importance(self, sentence: str) -> int:
        """Calculate importance score for an event"""
        sentence_lower = sentence.lower()
        importance = 1
        
        # Length bonus (longer descriptions often more important)
        importance += min(len(sentence) // 50, 3)
        
        # Important keywords boost
        important_keywords = [
            'first', 'invented', 'discovered', 'revolutionary', 'breakthrough',
            'significant', 'major', 'important', 'critical', 'landmark',
            'historic', 'unprecedented', 'groundbreaking', 'pioneering'
        ]
        
        for keyword in important_keywords:
            if keyword in sentence_lower:
                importance += 2
        
        # Numbers and statistics boost
        if re.search(r'\d+(\.\d+)?%|\$\d+|\d+(\,\d{3})*', sentence):
            importance += 1
        
        return min(importance, 10)  # Cap at 10
    
    def get_event_icon(self, event_type: str) -> str:
        """Get icon for event type"""
        icon_map = {
            'innovation': '💡',
            'discovery': '🔍',
            'business': '🏢',
            'historical': '🏛️',
            'scientific': '🔬',
            'personal': '👤',
            'general': '📅'
        }
        
        return icon_map.get(event_type, '📅')
    
    def remove_duplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on similarity"""
        unique_events = []
        
        for event in events:
            is_duplicate = False
            
            for existing in unique_events:
                # Check for similarity in title and date
                if (self.events_similar(event, existing) or 
                    abs(event['date_parsed']['period'] - existing['date_parsed']['period']) < 0.1):
                    is_duplicate = True
                    # Keep the more important event
                    if event['importance'] > existing['importance']:
                        unique_events.remove(existing)
                        unique_events.append(event)
                    break
            
            if not is_duplicate:
                unique_events.append(event)
        
        return unique_events
    
    def events_similar(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
        """Check if two events are similar"""
        # Simple similarity check based on title overlap
        title1_words = set(event1['title'].lower().split())
        title2_words = set(event2['title'].lower().split())
        
        if len(title1_words) == 0 or len(title2_words) == 0:
            return False
        
        overlap = len(title1_words.intersection(title2_words))
        min_length = min(len(title1_words), len(title2_words))
        
        return overlap / min_length > 0.6  # 60% word overlap
    
    def sort_events_chronologically(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort events chronologically"""
        return sorted(events, key=lambda x: x['date_parsed']['sort_key'])
    
    def calculate_timeline_span(self, events: List[Dict[str, Any]]) -> str:
        """Calculate the span of the timeline"""
        if not events:
            return "No timeline"
        
        start_year = events[0]['date_parsed']['year']
        end_year = events[-1]['date_parsed']['year']
        
        span_years = end_year - start_year
        
        if span_years == 0:
            return "Single year"
        elif span_years < 10:
            return f"{span_years} years"
        elif span_years < 100:
            return f"{span_years // 10} decades"
        else:
            return f"{span_years // 100} centuries"
    
    def create_timeline_config(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create configuration for timeline visualization"""
        if not events:
            return {}
        
        return {
            'orientation': 'horizontal',
            'show_current_time': False,
            'zoom_min': 1000 * 60 * 60 * 24 * 365,  # 1 year in milliseconds
            'zoom_max': 1000 * 60 * 60 * 24 * 365 * 100,  # 100 years
            'stack': True,
            'margin': {'item': 10, 'axis': 20},
            'editable': False,
            'selectable': True,
            'multiselect': False,
            'tooltip': {
                'followMouse': True,
                'overflowMethod': 'cap'
            }
        }
