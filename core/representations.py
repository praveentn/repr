# core/representations.py
import json
import re
import html
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RepresentationResult:
    mode: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    css_classes: List[str]
    javascript_code: Optional[str] = None

class RepresentationEngine:
    def __init__(self):
        self.available_modes = {
            "plain_text": {
                "name": "Plain Text",
                "description": "Simple, clean text format",
                "icon": "📝",
                "category": "basic"
            },
            "color_coded": {
                "name": "Color-Coded",
                "description": "Color-tagged sections with legend",
                "icon": "🎨",
                "category": "visual"
            },
            "collapsible_concepts": {
                "name": "Collapsible Concepts",
                "description": "Nested, expandable concept trees",
                "icon": "🧩",
                "category": "interactive"
            },
            "knowledge_graph": {
                "name": "Knowledge Graph",
                "description": "Visual web of interconnected concepts",
                "icon": "🧠",
                "category": "visual"
            },
            "analogical": {
                "name": "Analogical",
                "description": "Metaphor-based explanations",
                "icon": "🧪",
                "category": "creative"
            },
            "persona_eli5": {
                "name": "ELI5",
                "description": "Explain like I'm 5",
                "icon": "👶",
                "category": "persona"
            },
            "persona_expert": {
                "name": "Expert",
                "description": "Technical, detailed analysis",
                "icon": "👩‍🔬",
                "category": "persona"
            },
            "persona_layman": {
                "name": "Layman",
                "description": "General audience explanation",
                "icon": "👨‍🏫",
                "category": "persona"
            },
            "cinematic": {
                "name": "Cinematic",
                "description": "Narrative storytelling approach",
                "icon": "🎞️",
                "category": "creative"
            },
            "interactive": {
                "name": "Interactive",
                "description": "Engaging scenarios and examples",
                "icon": "🕹️",
                "category": "interactive"
            },
            "timeline": {
                "name": "Timeline",
                "description": "Chronological evolution view",
                "icon": "⏳",
                "category": "temporal"
            },
            "comparison": {
                "name": "Multi-perspective",
                "description": "Different viewpoints side-by-side",
                "icon": "💬",
                "category": "analytical"
            },
            "summary": {
                "name": "Summary",
                "description": "Concise key points",
                "icon": "📦",
                "category": "basic"
            },
            "detailed": {
                "name": "Detailed",
                "description": "Comprehensive deep dive",
                "icon": "📚",
                "category": "basic"
            }
        }
    
    async def generate_representation(
        self,
        content: str,
        mode: str,
        user_preferences: Optional[Dict] = None
    ) -> RepresentationResult:
        """Generate representation based on mode"""
        
        if mode not in self.available_modes:
            mode = "plain_text"
        
        # Route to specific representation handler
        handler_map = {
            "plain_text": self._generate_plain_text,
            "color_coded": self._generate_color_coded,
            "collapsible_concepts": self._generate_collapsible_concepts,
            "knowledge_graph": self._generate_knowledge_graph,
            "analogical": self._generate_analogical,
            "persona_eli5": self._generate_persona_based,
            "persona_expert": self._generate_persona_based,
            "persona_layman": self._generate_persona_based,
            "cinematic": self._generate_cinematic,
            "interactive": self._generate_interactive,
            "timeline": self._generate_timeline,
            "comparison": self._generate_comparison,
            "summary": self._generate_summary,
            "detailed": self._generate_detailed
        }
        
        handler = handler_map.get(mode, self._generate_plain_text)
        return await handler(content, user_preferences or {})
    
    async def _generate_plain_text(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate plain text representation"""
        return RepresentationResult(
            mode="plain_text",
            content={
                "text": content,
                "formatted": content.replace('\n', '<br>')
            },
            metadata={
                "word_count": len(content.split()),
                "estimated_read_time": f"{len(content.split()) // 200 + 1} min"
            },
            css_classes=["plain-text", "readable"]
        )
    
    async def _generate_color_coded(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate color-coded representation with legend"""
        
        # Extract different types of content
        sections = self._extract_color_coded_sections(content)
        
        return RepresentationResult(
            mode="color_coded",
            content={
                "sections": sections,
                "legend": {
                    "facts": {"color": "blue", "label": "Key Facts", "icon": "📊"},
                    "assumptions": {"color": "yellow", "label": "Assumptions", "icon": "❓"},
                    "examples": {"color": "green", "label": "Examples", "icon": "💡"},
                    "warnings": {"color": "red", "label": "Warnings/Risks", "icon": "⚠️"}
                }
            },
            metadata={
                "sections_count": len(sections),
                "dominant_type": max(sections.keys(), key=lambda k: len(sections[k])) if sections else "facts"
            },
            css_classes=["color-coded", "with-legend"]
        )
    
    async def _generate_collapsible_concepts(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate collapsible concept tree"""
        
        concepts = self._extract_hierarchical_concepts(content)
        
        return RepresentationResult(
            mode="collapsible_concepts",
            content={
                "concepts": concepts,
                "max_depth": self._get_max_depth(concepts)
            },
            metadata={
                "total_concepts": self._count_concepts(concepts),
                "complexity": "high" if len(concepts) > 5 else "medium" if len(concepts) > 2 else "low"
            },
            css_classes=["collapsible-concepts", "hierarchical"],
            javascript_code="initializeCollapsibleConcepts();"
        )
    
    async def _generate_knowledge_graph(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate knowledge graph representation"""
        
        entities, relationships = self._extract_entities_and_relationships(content)
        
        graph_data = {
            "nodes": [
                {
                    "id": entity["id"],
                    "label": entity["name"],
                    "type": entity.get("type", "concept"),
                    "description": entity.get("description", ""),
                    "size": entity.get("importance", 1) * 10
                }
                for entity in entities
            ],
            "edges": [
                {
                    "from": rel["source"],
                    "to": rel["target"],
                    "label": rel["relationship"],
                    "type": rel.get("type", "relates_to")
                }
                for rel in relationships
            ]
        }
        
        return RepresentationResult(
            mode="knowledge_graph",
            content={
                "graph_data": graph_data,
                "entities": entities,
                "relationships": relationships
            },
            metadata={
                "node_count": len(entities),
                "edge_count": len(relationships),
                "complexity": "high" if len(entities) > 10 else "medium"
            },
            css_classes=["knowledge-graph", "interactive-viz"],
            javascript_code="initializeKnowledgeGraph(graphData);"
        )
    
    async def _generate_analogical(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate analogical representation"""
        
        analogies = self._extract_analogies(content)
        
        return RepresentationResult(
            mode="analogical",
            content={
                "primary_analogy": analogies[0] if analogies else None,
                "all_analogies": analogies,
                "original_content": content
            },
            metadata={
                "analogy_count": len(analogies),
                "creativity_score": len(analogies) * 0.2
            },
            css_classes=["analogical", "creative"]
        )
    
    async def _generate_persona_based(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate persona-based representation"""
        
        return RepresentationResult(
            mode="persona_based",
            content={
                "content": content,
                "persona_style": "eli5" if "eli5" in preferences.get("mode", "") else "expert"
            },
            metadata={
                "complexity_level": "beginner" if "eli5" in preferences.get("mode", "") else "advanced",
                "target_audience": preferences.get("mode", "general")
            },
            css_classes=["persona-based", preferences.get("mode", "general")]
        )
    
    async def _generate_cinematic(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate cinematic narrative representation"""
        
        narrative_elements = self._extract_narrative_elements(content)
        
        return RepresentationResult(
            mode="cinematic",
            content={
                "narrative": narrative_elements,
                "acts": self._structure_into_acts(content),
                "dramatic_arc": True
            },
            metadata={
                "narrative_style": "dramatic",
                "engagement_level": "high"
            },
            css_classes=["cinematic", "narrative"],
            javascript_code="initializeCinematicView();"
        )
    
    async def _generate_interactive(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate interactive representation"""
        
        interactive_elements = self._create_interactive_elements(content)
        
        return RepresentationResult(
            mode="interactive",
            content={
                "elements": interactive_elements,
                "scenarios": self._extract_scenarios(content)
            },
            metadata={
                "interaction_count": len(interactive_elements),
                "engagement_type": "hands_on"
            },
            css_classes=["interactive", "engaging"],
            javascript_code="initializeInteractiveElements();"
        )
    
    async def _generate_timeline(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate timeline representation"""
        
        timeline_events = self._extract_timeline_events(content)
        
        return RepresentationResult(
            mode="timeline",
            content={
                "events": timeline_events,
                "start_date": timeline_events[0]["date"] if timeline_events else None,
                "end_date": timeline_events[-1]["date"] if timeline_events else None
            },
            metadata={
                "event_count": len(timeline_events),
                "time_span": "variable"
            },
            css_classes=["timeline", "chronological"],
            javascript_code="initializeTimeline();"
        )
    
    async def _generate_comparison(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate comparison representation"""
        
        comparisons = self._extract_comparisons(content)
        
        return RepresentationResult(
            mode="comparison",
            content={
                "comparisons": comparisons,
                "perspectives": self._extract_perspectives(content)
            },
            metadata={
                "comparison_count": len(comparisons),
                "perspective_count": len(self._extract_perspectives(content))
            },
            css_classes=["comparison", "multi-perspective"]
        )
    
    async def _generate_summary(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate summary representation"""
        
        key_points = self._extract_key_points(content)
        
        return RepresentationResult(
            mode="summary",
            content={
                "key_points": key_points,
                "tldr": key_points[0] if key_points else "No summary available",
                "full_content": content
            },
            metadata={
                "compression_ratio": round(len(' '.join(key_points)) / len(content), 2),
                "key_point_count": len(key_points)
            },
            css_classes=["summary", "condensed"]
        )
    
    async def _generate_detailed(self, content: str, preferences: Dict) -> RepresentationResult:
        """Generate detailed representation"""
        
        sections = self._create_detailed_sections(content)
        
        return RepresentationResult(
            mode="detailed",
            content={
                "sections": sections,
                "full_analysis": True
            },
            metadata={
                "section_count": len(sections),
                "detail_level": "comprehensive"
            },
            css_classes=["detailed", "comprehensive"]
        )
    
    # Helper methods for content extraction and processing
    
    def _extract_color_coded_sections(self, content: str) -> Dict[str, List[str]]:
        """Extract content sections for color coding"""
        sections = {
            "facts": [],
            "assumptions": [],
            "examples": [],
            "warnings": []
        }
        
        # Simple heuristic-based extraction
        sentences = content.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            lower_sentence = sentence.lower()
            
            if any(word in lower_sentence for word in ['fact', 'data', 'research', 'study', 'evidence']):
                sections["facts"].append(sentence)
            elif any(word in lower_sentence for word in ['assume', 'likely', 'probably', 'might', 'could']):
                sections["assumptions"].append(sentence)
            elif any(word in lower_sentence for word in ['example', 'instance', 'such as', 'like', 'for example']):
                sections["examples"].append(sentence)
            elif any(word in lower_sentence for word in ['warning', 'risk', 'danger', 'caution', 'avoid']):
                sections["warnings"].append(sentence)
            else:
                sections["facts"].append(sentence)  # Default to facts
        
        return sections
    
    def _extract_hierarchical_concepts(self, content: str) -> List[Dict]:
        """Extract hierarchical concepts for collapsible tree"""
        # Simple extraction based on paragraph structure
        paragraphs = content.split('\n\n')
        concepts = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                concept = {
                    "id": f"concept_{i}",
                    "title": paragraph.split('.')[0][:50] + "..." if len(paragraph.split('.')[0]) > 50 else paragraph.split('.')[0],
                    "content": paragraph.strip(),
                    "level": 1,
                    "children": []
                }
                concepts.append(concept)
        
        return concepts
    
    def _extract_entities_and_relationships(self, content: str) -> tuple:
        """Extract entities and relationships for knowledge graph"""
        # Simple entity extraction (would be enhanced with NLP)
        entities = []
        relationships = []
        
        # Extract potential entities (capitalized words)
        import re
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Create entity objects
        for i, entity in enumerate(set(potential_entities)):
            entities.append({
                "id": f"entity_{i}",
                "name": entity,
                "type": "concept",
                "importance": content.lower().count(entity.lower())
            })
        
        # Simple relationship extraction (would need more sophisticated NLP)
        for i in range(len(entities) - 1):
            relationships.append({
                "source": entities[i]["id"],
                "target": entities[i + 1]["id"],
                "relationship": "relates_to",
                "type": "conceptual"
            })
        
        return entities, relationships
    
    def _extract_analogies(self, content: str) -> List[Dict]:
        """Extract analogies from content"""
        analogies = []
        
        # Look for analogy patterns
        analogy_patterns = [
            r'like\s+(.+?)(?=\.|,|$)',
            r'similar to\s+(.+?)(?=\.|,|$)',
            r'analogous to\s+(.+?)(?=\.|,|$)',
            r'imagine\s+(.+?)(?=\.|,|$)'
        ]
        
        for pattern in analogy_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                analogies.append({
                    "analogy": match.strip(),
                    "type": "comparison"
                })
        
        return analogies
    
    def _extract_narrative_elements(self, content: str) -> Dict:
        """Extract narrative elements for cinematic representation"""
        return {
            "setting": "Knowledge exploration",
            "characters": ["User", "Information"],
            "conflict": "Understanding complex concepts",
            "resolution": "Clear comprehension"
        }
    
    def _structure_into_acts(self, content: str) -> List[Dict]:
        """Structure content into dramatic acts"""
        paragraphs = content.split('\n\n')
        total_paragraphs = len(paragraphs)
        
        acts = [
            {
                "act": 1,
                "title": "Introduction",
                "content": ' '.join(paragraphs[:total_paragraphs//3])
            },
            {
                "act": 2,
                "title": "Development",
                "content": ' '.join(paragraphs[total_paragraphs//3:2*total_paragraphs//3])
            },
            {
                "act": 3,
                "title": "Resolution",
                "content": ' '.join(paragraphs[2*total_paragraphs//3:])
            }
        ]
        
        return acts
    
    def _create_interactive_elements(self, content: str) -> List[Dict]:
        """Create interactive elements"""
        return [
            {
                "type": "question",
                "content": "What would you like to explore further?",
                "options": ["Details", "Examples", "Related Topics"]
            },
            {
                "type": "scenario",
                "content": "Consider this situation...",
                "interactive": True
            }
        ]
    
    def _extract_scenarios(self, content: str) -> List[Dict]:
        """Extract scenarios for interactive representation"""
        return [
            {
                "scenario": "Practical application",
                "description": "How would you use this information?",
                "options": ["Personal use", "Professional use", "Academic use"]
            }
        ]
    
    def _extract_timeline_events(self, content: str) -> List[Dict]:
        """Extract timeline events"""
        # Simple date/time extraction
        import re
        
        events = []
        date_patterns = [
            r'\b(\d{4})\b',  # Years
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # Dates
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b'
        ]
        
        sentences = content.split('.')
        for sentence in sentences:
            for pattern in date_patterns:
                matches = re.findall(pattern, sentence)
                if matches:
                    events.append({
                        "date": matches[0] if isinstance(matches[0], str) else matches[0][0],
                        "event": sentence.strip(),
                        "importance": 1
                    })
                    break
        
        return events
    
    def _extract_comparisons(self, content: str) -> List[Dict]:
        """Extract comparisons from content"""
        comparisons = []
        
        # Look for comparison keywords
        comparison_patterns = [
            r'compared to\s+(.+?)(?=\.|,|$)',
            r'versus\s+(.+?)(?=\.|,|$)',
            r'while\s+(.+?)(?=\.|,|$)',
            r'however\s+(.+?)(?=\.|,|$)'
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                comparisons.append({
                    "comparison": match.strip(),
                    "type": "contrast"
                })
        
        return comparisons
    
    def _extract_perspectives(self, content: str) -> List[Dict]:
        """Extract different perspectives"""
        return [
            {
                "perspective": "Technical",
                "content": "From a technical standpoint..."
            },
            {
                "perspective": "Practical",
                "content": "In practical terms..."
            }
        ]
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points for summary"""
        sentences = content.split('.')
        # Simple extraction - first sentence of each paragraph
        paragraphs = content.split('\n\n')
        key_points = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                first_sentence = paragraph.split('.')[0] + '.'
                key_points.append(first_sentence.strip())
        
        return key_points[:5]  # Limit to 5 key points
    
    def _create_detailed_sections(self, content: str) -> List[Dict]:
        """Create detailed sections"""
        paragraphs = content.split('\n\n')
        sections = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                sections.append({
                    "title": f"Section {i + 1}",
                    "content": paragraph.strip(),
                    "analysis": "Detailed analysis would go here",
                    "related_concepts": []
                })
        
        return sections
    
    def _get_max_depth(self, concepts: List[Dict]) -> int:
        """Get maximum depth of concept hierarchy"""
        return max([concept.get("level", 1) for concept in concepts], default=1)
    
    def _count_concepts(self, concepts: List[Dict]) -> int:
        """Count total concepts including children"""
        total = len(concepts)
        for concept in concepts:
            total += len(concept.get("children", []))
        return total
    
    def get_available_modes(self) -> Dict[str, Any]:
        """Get list of available representation modes"""
        return self.available_modes
    
    def health_check(self) -> bool:
        """Check representation engine health"""
        return True
