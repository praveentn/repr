# representations/knowledge_graph.py
from typing import Dict, Any, List, Tuple
import re
import json
from .base import BaseRepresentation, RepresentationResult

class KnowledgeGraphRepresentation(BaseRepresentation):
    """Knowledge Graph representation using vis.js"""
    
    def get_mode_name(self) -> str:
        return "knowledge_graph"
    
    def get_description(self) -> str:
        return "Interactive visual network of interconnected concepts"
    
    def get_icon(self) -> str:
        return "🧠"
    
    def get_category(self) -> str:
        return "visual"
    
    async def process(self, content: str, user_preferences: Dict = None) -> RepresentationResult:
        """Process content into knowledge graph format"""
        if not self.validate_content(content):
            return self.get_error_result("Content too short for knowledge graph generation")
        
        try:
            # Extract entities and relationships
            entities = self.extract_entities_enhanced(content)
            relationships = self.extract_relationships_enhanced(entities, content)
            
            # Create vis.js compatible data structure
            nodes, edges = self.format_for_visjs(entities, relationships)
            
            # Calculate graph metrics
            node_count = len(nodes)
            edge_count = len(edges)
            complexity = self.calculate_complexity(node_count, edge_count)
            
            graph_data = {
                'nodes': nodes,
                'edges': edges
            }
            
            return RepresentationResult(
                mode=self.mode_name,
                content={
                    'graph_data': graph_data,
                    'entities': entities,
                    'relationships': relationships,
                    'stats': {
                        'node_count': node_count,
                        'edge_count': edge_count,
                        'complexity': complexity
                    }
                },
                metadata={
                    'node_count': node_count,
                    'edge_count': edge_count,
                    'complexity': complexity,
                    'processing_method': 'enhanced_nlp'
                },
                css_classes=['knowledge-graph', 'interactive-viz'],
                javascript_code='initializeKnowledgeGraph',
                frontend_config={
                    'container_id': 'knowledge-graph',
                    'auto_resize': True,
                    'physics_enabled': True,
                    'interaction_enabled': True
                }
            )
            
        except Exception as e:
            return self.get_error_result(f"Failed to generate knowledge graph: {str(e)}")
    
    def extract_entities_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced entity extraction with better classification"""
        entities = []
        
        # Multi-pattern entity extraction
        patterns = {
            'proper_nouns': r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b',
            'technical_terms': r'\b(?:AI|API|CPU|GPU|ML|IoT|VR|AR|5G|HTTP|JSON|XML|SQL|NoSQL)\b',
            'concepts': r'\b(?:algorithm|framework|methodology|principle|concept|theory|model|system|process|technique)\w*\b',
            'entities_with_determiners': r'\b(?:the|a|an)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        }
        
        # Extract using all patterns
        all_entities = set()
        
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            if pattern_type == 'entities_with_determiners':
                # Extract the captured group (entity without determiner)
                all_entities.update(matches)
            else:
                all_entities.update(matches)
        
        # Create entity objects with enhanced classification
        for i, entity_name in enumerate(all_entities):
            if len(entity_name) < 3:  # Skip very short entities
                continue
                
            entity_type = self.classify_entity_enhanced(entity_name, content)
            importance = self.calculate_entity_importance(entity_name, content)
            
            entities.append({
                'id': f'node_{i}',
                'name': entity_name,
                'type': entity_type,
                'importance': importance,
                'description': self.generate_entity_description(entity_name, content),
                'color': self.get_entity_color(entity_type),
                'size': min(max(10, importance * 5), 30)  # Size between 10-30
            })
        
        # Sort by importance and limit to prevent overcrowding
        entities.sort(key=lambda x: x['importance'], reverse=True)
        return entities[:20]  # Limit to top 20 entities
    
    def classify_entity_enhanced(self, entity: str, content: str) -> str:
        """Enhanced entity classification with context awareness"""
        entity_lower = entity.lower()
        context_lower = content.lower()
        
        # Technology classification
        tech_keywords = {
            'ai': ['artificial', 'intelligence', 'machine', 'learning', 'neural', 'deep'],
            'computing': ['computer', 'cpu', 'gpu', 'quantum', 'cloud', 'server'],
            'software': ['application', 'program', 'software', 'framework', 'library'],
            'data': ['database', 'data', 'analytics', 'big data', 'dataset'],
            'web': ['website', 'web', 'internet', 'html', 'css', 'javascript'],
            'mobile': ['mobile', 'app', 'android', 'ios', 'smartphone']
        }
        
        for category, keywords in tech_keywords.items():
            if any(keyword in entity_lower for keyword in keywords):
                return f'technology_{category}'
        
        # Science classification
        science_keywords = {
            'physics': ['atom', 'electron', 'photon', 'quantum', 'particle', 'energy'],
            'biology': ['cell', 'dna', 'protein', 'gene', 'organism', 'species'],
            'chemistry': ['molecule', 'compound', 'reaction', 'element', 'chemical'],
            'mathematics': ['equation', 'algorithm', 'formula', 'calculation', 'number']
        }
        
        for category, keywords in science_keywords.items():
            if any(keyword in entity_lower for keyword in keywords):
                return f'science_{category}'
        
        # Business/Organization
        business_keywords = ['company', 'corporation', 'business', 'organization', 'enterprise', 'firm']
        if any(keyword in entity_lower for keyword in business_keywords):
            return 'organization'
        
        # People/Names (often capitalized and used with personal context)
        if entity[0].isupper() and any(indicator in context_lower for indicator in ['founder', 'ceo', 'scientist', 'researcher', 'inventor']):
            return 'person'
        
        # Location
        location_keywords = ['city', 'country', 'state', 'region', 'area', 'location']
        if any(keyword in context_lower for keyword in location_keywords):
            return 'location'
        
        # Process/Method
        process_keywords = ['process', 'method', 'technique', 'approach', 'procedure', 'strategy']
        if any(keyword in entity_lower for keyword in process_keywords):
            return 'process'
        
        # Default to concept
        return 'concept'
    
    def calculate_entity_importance(self, entity: str, content: str) -> int:
        """Calculate entity importance based on frequency and context"""
        content_lower = content.lower()
        entity_lower = entity.lower()
        
        # Base frequency count
        frequency = content_lower.count(entity_lower)
        
        # Context boost
        importance_indicators = [
            'important', 'key', 'main', 'primary', 'central', 'core', 'fundamental',
            'essential', 'critical', 'significant', 'major', 'crucial'
        ]
        
        context_boost = 0
        for indicator in importance_indicators:
            pattern = rf'\b{indicator}\b.*?\b{re.escape(entity_lower)}\b|\b{re.escape(entity_lower)}\b.*?\b{indicator}\b'
            if re.search(pattern, content_lower):
                context_boost += 2
        
        # Position boost (entities mentioned early are often more important)
        first_occurrence = content_lower.find(entity_lower)
        position_boost = max(0, 3 - (first_occurrence / len(content_lower)) * 3)
        
        return frequency + context_boost + int(position_boost)
    
    def generate_entity_description(self, entity: str, content: str) -> str:
        """Generate description for entity based on surrounding context"""
        entity_lower = entity.lower()
        content_lower = content.lower()
        
        # Find sentences containing the entity
        sentences = self.extract_sentences(content)
        relevant_sentences = [s for s in sentences if entity_lower in s.lower()]
        
        if relevant_sentences:
            # Use the first relevant sentence, truncated
            description = relevant_sentences[0]
            if len(description) > 100:
                description = description[:97] + "..."
            return description
        
        return f"Concept: {entity}"
    
    def get_entity_color(self, entity_type: str) -> str:
        """Get color for entity type"""
        color_map = {
            'technology_ai': '#3B82F6',      # Blue
            'technology_computing': '#6366F1', # Indigo
            'technology_software': '#8B5CF6',  # Violet
            'technology_data': '#06B6D4',     # Cyan
            'technology_web': '#10B981',      # Emerald
            'technology_mobile': '#F59E0B',   # Amber
            'science_physics': '#EF4444',     # Red
            'science_biology': '#84CC16',     # Lime
            'science_chemistry': '#F97316',   # Orange
            'science_mathematics': '#EC4899', # Pink
            'organization': '#6B7280',        # Gray
            'person': '#DC2626',              # Red
            'location': '#059669',            # Emerald
            'process': '#7C3AED',             # Violet
            'concept': '#4B5563'              # Default gray
        }
        
        return color_map.get(entity_type, '#4B5563')
    
    def extract_relationships_enhanced(self, entities: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """Enhanced relationship extraction with better pattern matching"""
        relationships = []
        
        # Enhanced relationship patterns with more variety
        relationship_patterns = [
            # Basic relationships
            (r'(\w+(?:\s+\w+)*)\s+(?:is|are)\s+(?:a|an|the)?\s*(\w+(?:\s+\w+)*)', 'is_a'),
            (r'(\w+(?:\s+\w+)*)\s+(?:has|have|contains?|includes?)\s+(\w+(?:\s+\w+)*)', 'has'),
            (r'(\w+(?:\s+\w+)*)\s+(?:uses?|utilizes?|employs?)\s+(\w+(?:\s+\w+)*)', 'uses'),
            (r'(\w+(?:\s+\w+)*)\s+(?:creates?|produces?|generates?|builds?)\s+(\w+(?:\s+\w+)*)', 'creates'),
            (r'(\w+(?:\s+\w+)*)\s+(?:enables?|allows?|facilitates?)\s+(\w+(?:\s+\w+)*)', 'enables'),
            (r'(\w+(?:\s+\w+)*)\s+(?:requires?|needs?|depends on)\s+(\w+(?:\s+\w+)*)', 'requires'),
            
            # Advanced relationships
            (r'(\w+(?:\s+\w+)*)\s+(?:implements?|realizes?)\s+(\w+(?:\s+\w+)*)', 'implements'),
            (r'(\w+(?:\s+\w+)*)\s+(?:extends?|inherits? from)\s+(\w+(?:\s+\w+)*)', 'extends'),
            (r'(\w+(?:\s+\w+)*)\s+(?:communicates? with|interacts? with)\s+(\w+(?:\s+\w+)*)', 'interacts_with'),
            (r'(\w+(?:\s+\w+)*)\s+(?:processes?|handles?|manages?)\s+(\w+(?:\s+\w+)*)', 'processes'),
            (r'(\w+(?:\s+\w+)*)\s+(?:stores?|contains? data about)\s+(\w+(?:\s+\w+)*)', 'stores'),
            (r'(\w+(?:\s+\w+)*)\s+(?:connects? to|links? to)\s+(\w+(?:\s+\w+)*)', 'connects_to'),
            
            # Conjunctive relationships
            (r'(\w+(?:\s+\w+)*)\s+(?:and|with|plus)\s+(\w+(?:\s+\w+)*)', 'related_to'),
            (r'(\w+(?:\s+\w+)*)\s+(?:or|versus|vs)\s+(\w+(?:\s+\w+)*)', 'alternative_to')
        ]
        
        entity_names = [entity['name'] for entity in entities]
        
        for rel_id, (pattern, rel_type) in enumerate(relationship_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches:
                source_name = match[0].strip()
                target_name = match[1].strip()
                
                # Find matching entities (fuzzy matching)
                source_entity = self.find_best_entity_match(entities, source_name)
                target_entity = self.find_best_entity_match(entities, target_name)
                
                if source_entity and target_entity and source_entity['id'] != target_entity['id']:
                    relationship_strength = self.calculate_relationship_strength(source_name, target_name, content)
                    
                    relationships.append({
                        'id': f'edge_{rel_id}_{len(relationships)}',
                        'from': source_entity['id'],
                        'to': target_entity['id'],
                        'label': rel_type.replace('_', ' '),
                        'relationship': rel_type,
                        'strength': relationship_strength,
                        'type': 'semantic',
                        'color': self.get_relationship_color(rel_type),
                        'width': min(max(1, relationship_strength), 4)
                    })
        
        return relationships
    
    def find_best_entity_match(self, entities: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
        """Find best matching entity using fuzzy matching"""
        name_lower = name.lower().strip()
        
        # Exact match first
        for entity in entities:
            if entity['name'].lower() == name_lower:
                return entity
        
        # Partial match (entity name in search name or vice versa)
        for entity in entities:
            entity_name_lower = entity['name'].lower()
            if (name_lower in entity_name_lower or 
                entity_name_lower in name_lower or
                self.words_overlap(name_lower, entity_name_lower)):
                return entity
        
        return None
    
    def words_overlap(self, text1: str, text2: str) -> bool:
        """Check if words overlap between two texts"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        return len(words1.intersection(words2)) > 0
    
    def calculate_relationship_strength(self, source: str, target: str, content: str) -> int:
        """Calculate strength of relationship based on context"""
        content_lower = content.lower()
        
        # Co-occurrence frequency
        co_occurrence_count = 0
        sentences = self.extract_sentences(content)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if source.lower() in sentence_lower and target.lower() in sentence_lower:
                co_occurrence_count += 1
        
        # Proximity boost (closer words = stronger relationship)
        proximity_boost = 0
        source_pos = content_lower.find(source.lower())
        target_pos = content_lower.find(target.lower())
        
        if source_pos != -1 and target_pos != -1:
            distance = abs(source_pos - target_pos)
            proximity_boost = max(0, 3 - (distance / 100))  # Closer = higher boost
        
        return max(1, co_occurrence_count + int(proximity_boost))
    
    def get_relationship_color(self, rel_type: str) -> str:
        """Get color for relationship type"""
        color_map = {
            'is_a': '#3B82F6',           # Blue
            'has': '#10B981',            # Green
            'uses': '#F59E0B',           # Amber
            'creates': '#EF4444',        # Red
            'enables': '#8B5CF6',        # Violet
            'requires': '#EC4899',       # Pink
            'implements': '#06B6D4',     # Cyan
            'extends': '#84CC16',        # Lime
            'interacts_with': '#F97316', # Orange
            'processes': '#6366F1',      # Indigo
            'stores': '#059669',         # Emerald
            'connects_to': '#DC2626',    # Red
            'related_to': '#6B7280',     # Gray
            'alternative_to': '#7C3AED'  # Violet
        }
        
        return color_map.get(rel_type, '#6B7280')
    
    def format_for_visjs(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
        """Format entities and relationships for vis.js"""
        
        # Format nodes
        nodes = []
        for entity in entities:
            nodes.append({
                'id': entity['id'],
                'label': entity['name'],
                'title': entity['description'],  # Tooltip
                'group': entity['type'],
                'size': entity['size'],
                'color': {
                    'background': entity['color'],
                    'border': '#2D3748',
                    'highlight': {
                        'background': '#FBBF24',
                        'border': '#92400E'
                    }
                },
                'font': {
                    'size': 12,
                    'color': '#1F2937'
                },
                'physics': True,
                'value': entity['importance']
            })
        
        # Format edges
        edges = []
        for relationship in relationships:
            edges.append({
                'id': relationship['id'],
                'from': relationship['from'],
                'to': relationship['to'],
                'label': relationship['label'],
                'title': f"{relationship['relationship']}: {relationship['label']}",
                'width': relationship['width'],
                'color': {
                    'color': relationship['color'],
                    'highlight': '#F59E0B'
                },
                'arrows': {
                    'to': {
                        'enabled': True,
                        'scaleFactor': 0.8
                    }
                },
                'smooth': {
                    'enabled': True,
                    'type': 'continuous'
                },
                'physics': True
            })
        
        return nodes, edges
    
    def calculate_complexity(self, node_count: int, edge_count: int) -> str:
        """Calculate graph complexity level"""
        total_elements = node_count + edge_count
        
        if total_elements < 10:
            return 'low'
        elif total_elements < 25:
            return 'medium'
        else:
            return 'high'

