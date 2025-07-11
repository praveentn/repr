# core/representations.py
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import all representation modules
from representations.base import BaseRepresentation, RepresentationResult
from representations.knowledge_graph import KnowledgeGraphRepresentation
from representations.plain_text import PlainTextRepresentation
from representations.color_coded import ColorCodedRepresentation
from representations.collapsible_concepts import CollapsibleConceptsRepresentation
from representations.summary import SummaryRepresentation
from representations.timeline import TimelineRepresentation
from representations.puzzle_based import PuzzleBasedRepresentation

logger = logging.getLogger(__name__)

class RepresentationEngine:
    """Enhanced representation engine with modular architecture"""
    
    def __init__(self):
        self.representations = {}
        self.available_modes = {}
        self._initialize_representations()
        
    def _initialize_representations(self):
        """Initialize all representation modules"""
        representation_classes = [
            PlainTextRepresentation,
            ColorCodedRepresentation,
            CollapsibleConceptsRepresentation,
            KnowledgeGraphRepresentation,
            SummaryRepresentation,
            TimelineRepresentation,
            PuzzleBasedRepresentation
        ]
        
        for rep_class in representation_classes:
            try:
                rep_instance = rep_class()
                mode_name = rep_instance.get_mode_name()
                
                # Store representation instance
                self.representations[mode_name] = rep_instance
                
                # Store mode information
                self.available_modes[mode_name] = rep_instance.get_info()
                
                logger.info(f"✅ Initialized representation: {mode_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize representation {rep_class.__name__}: {e}")
        
        logger.info(f"🎨 Representation engine initialized with {len(self.representations)} modes")
    
    async def generate_representation(
        self,
        content: str,
        mode: str,
        user_preferences: Optional[Dict] = None
    ) -> RepresentationResult:
        """Generate representation using modular system"""
        
        if not content or len(content.strip()) < 10:
            return self._get_error_result("Content too short for processing", mode)
        
        # Get representation handler
        representation = self.representations.get(mode)
        
        if not representation:
            logger.warning(f"Unknown representation mode: {mode}, falling back to plain_text")
            representation = self.representations.get('plain_text')
            
        if not representation:
            return self._get_error_result("No suitable representation found", mode)
        
        try:
            # Process using the specific representation
            result = await representation.process(content, user_preferences or {})
            
            # Add engine metadata
            result.metadata['engine_version'] = '2.0'
            result.metadata['processing_engine'] = 'modular'
            
            logger.info(f"✅ Generated {mode} representation successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating {mode} representation: {e}")
            return self._get_error_result(f"Error generating representation: {str(e)}", mode)
    
    def get_available_modes(self) -> Dict[str, Any]:
        """Get all available representation modes"""
        return self.available_modes.copy()
    
    def get_mode_info(self, mode: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific mode"""
        return self.available_modes.get(mode)
    
    def is_mode_available(self, mode: str) -> bool:
        """Check if a representation mode is available"""
        return mode in self.representations
    
    def get_modes_by_category(self, category: str) -> Dict[str, Any]:
        """Get all modes in a specific category"""
        return {
            mode: info for mode, info in self.available_modes.items()
            if info.get('category') == category
        }
    
    def health_check(self) -> bool:
        """Check if representation engine is healthy"""
        try:
            # Check if we have essential representations
            essential_modes = ['plain_text', 'summary']
            for mode in essential_modes:
                if mode not in self.representations:
                    return False
            
            return len(self.representations) > 0
            
        except Exception:
            return False
    
    def _get_error_result(self, message: str, mode: str) -> RepresentationResult:
        """Create error result"""
        return RepresentationResult(
            mode=mode,
            content={
                'error': True,
                'message': message,
                'fallback_content': 'Unable to process content for this representation mode.'
            },
            metadata={
                'error': True,
                'processing_time': 0,
                'engine_version': '2.0'
            },
            css_classes=['error-state'],
            frontend_config={'show_error': True}
        )

# Legacy compatibility functions (for backward compatibility)
async def _generate_plain_text(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for plain text"""
    rep = PlainTextRepresentation()
    return await rep.process(content, preferences)

async def _generate_color_coded(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for color coded"""
    rep = ColorCodedRepresentation()
    return await rep.process(content, preferences)

async def _generate_collapsible_concepts(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for collapsible concepts"""
    rep = CollapsibleConceptsRepresentation()
    return await rep.process(content, preferences)

async def _generate_knowledge_graph(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for knowledge graph"""
    rep = KnowledgeGraphRepresentation()
    return await rep.process(content, preferences)

async def _generate_summary(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for summary"""
    rep = SummaryRepresentation()
    return await rep.process(content, preferences)

async def _generate_timeline(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for timeline"""
    rep = TimelineRepresentation()
    return await rep.process(content, preferences)

async def _generate_puzzle_based(content: str, preferences: Dict) -> RepresentationResult:
    """Legacy compatibility for puzzle based"""
    rep = PuzzleBasedRepresentation()
    return await rep.process(content, preferences)