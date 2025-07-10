# examples/demo_data.py
"""
Demo data and examples for Knowledge Representation Engine
Provides sample queries, contexts, and expected outputs for testing and demonstration
"""

import json
from typing import Dict, List, Any
from datetime import datetime

class DemoDataGenerator:
    """Generates demo data for testing and demonstration purposes"""
    
    def __init__(self):
        self.sample_queries = self._get_sample_queries()
        self.sample_contexts = self._get_sample_contexts()
        self.sample_responses = self._get_sample_responses()
        self.representation_examples = self._get_representation_examples()
    
    def _get_sample_queries(self) -> List[Dict[str, Any]]:
        """Sample queries for different use cases"""
        return [
            {
                "id": "ai_basics",
                "query": "What is artificial intelligence and how does it work?",
                "category": "Technology",
                "complexity": "beginner",
                "best_modes": ["plain_text", "color_coded", "analogical"],
                "description": "Basic introduction to AI concepts"
            },
            {
                "id": "climate_change",
                "query": "Explain the causes and effects of climate change",
                "category": "Science",
                "complexity": "intermediate",
                "best_modes": ["knowledge_graph", "timeline", "color_coded"],
                "description": "Comprehensive climate change explanation"
            },
            {
                "id": "quantum_computing",
                "query": "How does quantum computing differ from classical computing?",
                "category": "Technology",
                "complexity": "advanced",
                "best_modes": ["comparison", "analogical", "detailed"],
                "description": "Technical comparison of computing paradigms"
            },
            {
                "id": "history_internet",
                "query": "What is the history and evolution of the internet?",
                "category": "History",
                "complexity": "intermediate",
                "best_modes": ["timeline", "collapsible_concepts", "knowledge_graph"],
                "description": "Internet development over time"
            },
            {
                "id": "machine_learning",
                "query": "Explain machine learning for a 5-year-old",
                "category": "Technology",
                "complexity": "beginner",
                "best_modes": ["persona_eli5", "analogical", "cinematic"],
                "description": "Child-friendly ML explanation"
            },
            {
                "id": "blockchain_basics",
                "query": "What is blockchain technology and why is it important?",
                "category": "Technology",
                "complexity": "intermediate",
                "best_modes": ["analogical", "color_coded", "interactive"],
                "description": "Blockchain fundamentals with metaphors"
            },
            {
                "id": "photosynthesis",
                "query": "Explain the process of photosynthesis in plants",
                "category": "Biology",
                "complexity": "intermediate",
                "best_modes": ["knowledge_graph", "collapsible_concepts", "detailed"],
                "description": "Biological process explanation"
            },
            {
                "id": "financial_planning",
                "query": "What are the key principles of personal financial planning?",
                "category": "Finance",
                "complexity": "beginner",
                "best_modes": ["summary", "color_coded", "interactive"],
                "description": "Personal finance guidance"
            },
            {
                "id": "space_exploration",
                "query": "What are the major milestones in space exploration?",
                "category": "Science",
                "complexity": "intermediate",
                "best_modes": ["timeline", "knowledge_graph", "cinematic"],
                "description": "Space exploration history"
            },
            {
                "id": "nutrition_health",
                "query": "How does nutrition affect mental health and cognitive performance?",
                "category": "Health",
                "complexity": "intermediate",
                "best_modes": ["knowledge_graph", "color_coded", "detailed"],
                "description": "Nutrition-brain connection"
            }
        ]
    
    def _get_sample_contexts(self) -> Dict[str, Dict[str, Any]]:
        """Sample contexts for different scenarios"""
        return {
            "student_beginner": {
                "user_profile": {
                    "education_level": "high_school",
                    "expertise": "beginner",
                    "learning_style": "visual",
                    "age_group": "teenager"
                },
                "preferences": {
                    "complexity_level": "simple",
                    "examples_preferred": True,
                    "analogies_helpful": True
                },
                "chat_history": [
                    "I'm a high school student trying to understand complex topics",
                    "I learn better with visual examples and simple explanations"
                ]
            },
            "professional_researcher": {
                "user_profile": {
                    "education_level": "graduate",
                    "expertise": "expert",
                    "field": "research",
                    "age_group": "adult"
                },
                "preferences": {
                    "complexity_level": "detailed",
                    "technical_terms": True,
                    "citations_preferred": True
                },
                "chat_history": [
                    "I need detailed technical information for my research",
                    "Please include specific examples and current developments"
                ]
            },
            "curious_parent": {
                "user_profile": {
                    "education_level": "college",
                    "expertise": "intermediate",
                    "role": "parent",
                    "age_group": "adult"
                },
                "preferences": {
                    "complexity_level": "moderate",
                    "practical_examples": True,
                    "family_relevant": True
                },
                "chat_history": [
                    "I want to understand this topic so I can explain it to my children",
                    "I prefer practical examples that relate to everyday life"
                ]
            },
            "business_executive": {
                "user_profile": {
                    "education_level": "graduate",
                    "expertise": "intermediate",
                    "role": "executive",
                    "industry": "business"
                },
                "preferences": {
                    "complexity_level": "concise",
                    "business_impact": True,
                    "strategic_focus": True
                },
                "chat_history": [
                    "I need to understand the business implications and strategic value",
                    "Focus on practical applications and ROI potential"
                ]
            },
            "elderly_learner": {
                "user_profile": {
                    "age_group": "senior",
                    "expertise": "beginner",
                    "tech_comfort": "low",
                    "learning_pace": "slow"
                },
                "preferences": {
                    "complexity_level": "simple",
                    "patience_required": True,
                    "clear_structure": True
                },
                "chat_history": [
                    "I'm new to this topic and need patient explanations",
                    "Please use clear, simple language and avoid too much jargon"
                ]
            }
        }
    
    def _get_sample_responses(self) -> Dict[str, str]:
        """Sample LLM responses for different topics"""
        return {
            "ai_basics": """
Artificial Intelligence (AI) is like giving computers the ability to think and learn like humans do. Think of it as teaching a computer to recognize patterns, make decisions, and solve problems.

At its core, AI works by:

1. **Learning from Data**: Just like how you learn to recognize faces by seeing many different people, AI systems learn by analyzing huge amounts of information.

2. **Pattern Recognition**: AI finds patterns in data that might be too complex or subtle for humans to notice easily.

3. **Making Predictions**: Based on what it has learned, AI can make educated guesses about new situations it hasn't seen before.

4. **Continuous Improvement**: Many AI systems get better over time as they process more data and receive feedback.

There are different types of AI:
- **Narrow AI**: Designed for specific tasks (like voice assistants or recommendation systems)
- **Machine Learning**: Systems that improve automatically through experience
- **Deep Learning**: AI that mimics how the human brain processes information

AI is already part of daily life through smartphones, search engines, social media feeds, and navigation apps. While we're still far from human-level general intelligence, AI continues to advance rapidly and transform various industries.
            """,
            
            "climate_change": """
Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, scientific evidence shows that human activities have been the main driver since the 1800s.

**Primary Causes:**

1. **Greenhouse Gas Emissions**: Primarily carbon dioxide from burning fossil fuels (coal, oil, gas)
2. **Deforestation**: Reduces Earth's capacity to absorb CO2
3. **Industrial Processes**: Manufacturing and chemical production
4. **Agriculture**: Methane from livestock and rice cultivation
5. **Transportation**: Cars, planes, ships burning fossil fuels

**Key Effects:**

1. **Rising Temperatures**: Global average temperature has increased by about 1.1°C since pre-industrial times
2. **Melting Ice**: Arctic sea ice, glaciers, and ice sheets are shrinking
3. **Sea Level Rise**: Thermal expansion of oceans plus melting ice
4. **Extreme Weather**: More frequent heatwaves, droughts, floods, and storms
5. **Ecosystem Disruption**: Changes in species distribution and migration patterns
6. **Agricultural Impact**: Changing growing seasons and crop yields

**Human Consequences:**
- Health risks from heat and air pollution
- Food and water security challenges
- Economic costs from extreme weather damage
- Forced migration from uninhabitable areas

**Solutions:**
- Transition to renewable energy
- Energy efficiency improvements
- Reforestation and conservation
- Sustainable transportation
- International cooperation through agreements like the Paris Climate Accord

The scientific consensus is clear: immediate action is needed to limit warming to 1.5°C above pre-industrial levels to avoid the most catastrophic impacts.
            """,
            
            "quantum_computing": """
Quantum computing represents a fundamental departure from classical computing, leveraging quantum mechanical phenomena to process information in revolutionary ways.

**Classical Computing Foundation:**
Classical computers use bits as the basic unit of information, where each bit exists in a definite state of either 0 or 1. Operations are performed sequentially through logic gates, following deterministic algorithms.

**Quantum Computing Principles:**

1. **Qubits vs. Bits**: Quantum computers use quantum bits (qubits) that can exist in a superposition of both 0 and 1 states simultaneously, enabling parallel processing of multiple possibilities.

2. **Superposition**: A qubit can be in all possible states at once until measured, allowing quantum computers to explore many solution paths simultaneously.

3. **Entanglement**: Qubits can be quantum mechanically linked, so the state of one instantly affects others regardless of distance, enabling complex correlations.

4. **Quantum Interference**: Quantum algorithms manipulate probability amplitudes to increase the likelihood of correct answers while canceling out wrong ones.

**Key Differences:**

| Aspect | Classical | Quantum |
|--------|-----------|---------|
| Information Unit | Bit (0 or 1) | Qubit (0, 1, or both) |
| Processing | Sequential | Parallel through superposition |
| Error Handling | Deterministic | Probabilistic |
| Scaling | Linear | Exponential for certain problems |

**Quantum Advantages:**
- **Factoring**: Shor's algorithm can break current encryption
- **Search**: Grover's algorithm provides quadratic speedup
- **Simulation**: Natural modeling of quantum systems
- **Optimization**: Potential exponential speedup for certain problems

**Current Limitations:**
- Quantum decoherence (fragile quantum states)
- High error rates requiring error correction
- Extremely low operating temperatures
- Limited number of stable qubits
- Specialized programming requirements

**Practical Timeline:**
While quantum computers excel at specific problems, they won't replace classical computers for general tasks. Instead, they'll work alongside classical systems for specialized applications in cryptography, drug discovery, financial modeling, and materials science.

The quantum advantage is problem-specific: for tasks like database searching or mathematical simulations, quantum computers may offer exponential speedups, while for others, classical computers remain superior.
            """
        }
    
    def _get_representation_examples(self) -> Dict[str, Dict[str, Any]]:
        """Examples of different representation formats"""
        return {
            "color_coded_example": {
                "mode": "color_coded",
                "content": {
                    "sections": {
                        "facts": [
                            "Machine learning is a subset of artificial intelligence.",
                            "Neural networks are inspired by the human brain structure.",
                            "Deep learning uses multiple layers of neural networks."
                        ],
                        "assumptions": [
                            "AI development will continue to accelerate exponentially.",
                            "Current AI limitations may be overcome with better algorithms.",
                            "Quantum computing might revolutionize AI capabilities."
                        ],
                        "examples": [
                            "Image recognition systems can identify objects in photos.",
                            "Recommendation engines suggest products on e-commerce sites.",
                            "Virtual assistants like Siri and Alexa use natural language processing."
                        ],
                        "warnings": [
                            "AI systems can perpetuate biases present in training data.",
                            "Over-reliance on AI might reduce human problem-solving skills.",
                            "Privacy concerns arise from extensive data collection for AI training."
                        ]
                    },
                    "legend": {
                        "facts": {"color": "blue", "label": "Verified Facts", "icon": "📊"},
                        "assumptions": {"color": "yellow", "label": "Assumptions", "icon": "❓"},
                        "examples": {"color": "green", "label": "Examples", "icon": "💡"},
                        "warnings": {"color": "red", "label": "Warnings/Risks", "icon": "⚠️"}
                    }
                }
            },
            
            "knowledge_graph_example": {
                "mode": "knowledge_graph",
                "content": {
                    "graph_data": {
                        "nodes": [
                            {"id": "ai", "label": "Artificial Intelligence", "type": "field", "size": 30},
                            {"id": "ml", "label": "Machine Learning", "type": "subfield", "size": 25},
                            {"id": "dl", "label": "Deep Learning", "type": "technique", "size": 20},
                            {"id": "nn", "label": "Neural Networks", "type": "method", "size": 20},
                            {"id": "nlp", "label": "Natural Language Processing", "type": "application", "size": 18},
                            {"id": "cv", "label": "Computer Vision", "type": "application", "size": 18},
                            {"id": "rl", "label": "Reinforcement Learning", "type": "technique", "size": 15},
                            {"id": "data", "label": "Training Data", "type": "resource", "size": 15},
                            {"id": "algorithms", "label": "Algorithms", "type": "component", "size": 15}
                        ],
                        "edges": [
                            {"from": "ai", "to": "ml", "label": "includes", "type": "hierarchy"},
                            {"from": "ml", "to": "dl", "label": "specializes_to", "type": "hierarchy"},
                            {"from": "dl", "to": "nn", "label": "uses", "type": "method"},
                            {"from": "ml", "to": "nlp", "label": "enables", "type": "application"},
                            {"from": "ml", "to": "cv", "label": "enables", "type": "application"},
                            {"from": "ml", "to": "rl", "label": "includes", "type": "technique"},
                            {"from": "ml", "to": "data", "label": "requires", "type": "dependency"},
                            {"from": "ml", "to": "algorithms", "label": "implements", "type": "method"}
                        ]
                    }
                }
            },
            
            "timeline_example": {
                "mode": "timeline",
                "content": {
                    "events": [
                        {
                            "date": "1943",
                            "event": "First neural network model proposed by McCulloch and Pitts",
                            "importance": 3,
                            "description": "Mathematical model of artificial neurons"
                        },
                        {
                            "date": "1950",
                            "event": "Alan Turing proposes the Turing Test",
                            "importance": 5,
                            "description": "Landmark test for machine intelligence"
                        },
                        {
                            "date": "1956",
                            "event": "Dartmouth Conference coins 'Artificial Intelligence'",
                            "importance": 5,
                            "description": "Birth of AI as a academic field"
                        },
                        {
                            "date": "1969",
                            "event": "First AI winter begins",
                            "importance": 2,
                            "description": "Reduced funding and interest in AI research"
                        },
                        {
                            "date": "1986",
                            "event": "Backpropagation algorithm popularized",
                            "importance": 4,
                            "description": "Key breakthrough for training neural networks"
                        },
                        {
                            "date": "1997",
                            "event": "Deep Blue defeats chess champion Garry Kasparov",
                            "importance": 4,
                            "description": "First AI to beat world champion in chess"
                        },
                        {
                            "date": "2012",
                            "event": "AlexNet wins ImageNet competition",
                            "importance": 5,
                            "description": "Deep learning revolution begins"
                        },
                        {
                            "date": "2016",
                            "event": "AlphaGo defeats Go champion Lee Sedol",
                            "importance": 4,
                            "description": "AI masters complex game of Go"
                        },
                        {
                            "date": "2020",
                            "event": "GPT-3 demonstrates advanced language capabilities",
                            "importance": 4,
                            "description": "Large language models show human-like text generation"
                        },
                        {
                            "date": "2022",
                            "event": "ChatGPT launches to public",
                            "importance": 5,
                            "description": "AI becomes mainstream with conversational interfaces"
                        }
                    ]
                }
            },
            
            "collapsible_concepts_example": {
                "mode": "collapsible_concepts",
                "content": {
                    "concepts": [
                        {
                            "id": "ai_overview",
                            "title": "What is Artificial Intelligence?",
                            "content": "AI is the simulation of human intelligence in machines programmed to think and learn.",
                            "level": 1,
                            "children": [
                                {
                                    "id": "ai_types",
                                    "title": "Types of AI",
                                    "content": "Narrow AI (specific tasks) vs General AI (human-level intelligence)",
                                    "level": 2
                                },
                                {
                                    "id": "ai_applications",
                                    "title": "Real-world Applications",
                                    "content": "Voice assistants, recommendation systems, autonomous vehicles, medical diagnosis",
                                    "level": 2
                                }
                            ]
                        },
                        {
                            "id": "ml_concepts",
                            "title": "Machine Learning Fundamentals",
                            "content": "ML enables computers to learn and improve from experience without explicit programming.",
                            "level": 1,
                            "children": [
                                {
                                    "id": "supervised_learning",
                                    "title": "Supervised Learning",
                                    "content": "Learning with labeled examples (input-output pairs)",
                                    "level": 2
                                },
                                {
                                    "id": "unsupervised_learning",
                                    "title": "Unsupervised Learning",
                                    "content": "Finding patterns in data without labeled examples",
                                    "level": 2
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def get_demo_query_set(self, category: str = None, complexity: str = None) -> List[Dict[str, Any]]:
        """Get filtered demo queries"""
        queries = self.sample_queries.copy()
        
        if category:
            queries = [q for q in queries if q.get("category", "").lower() == category.lower()]
        
        if complexity:
            queries = [q for q in queries if q.get("complexity", "").lower() == complexity.lower()]
        
        return queries
    
    def get_demo_request(self, query_id: str, context_type: str = "student_beginner") -> Dict[str, Any]:
        """Generate a complete demo request"""
        query = next((q for q in self.sample_queries if q["id"] == query_id), None)
        if not query:
            raise ValueError(f"Query ID '{query_id}' not found")
        
        context = self.sample_contexts.get(context_type, {})
        
        return {
            "query": query["query"],
            "context": context,
            "representation_mode": query["best_modes"][0] if query["best_modes"] else "plain_text",
            "user_preferences": context.get("preferences", {}),
            "demo_metadata": {
                "query_id": query_id,
                "context_type": context_type,
                "category": query["category"],
                "complexity": query["complexity"],
                "description": query["description"]
            }
        }
    
    def get_mock_response(self, query_id: str) -> str:
        """Get mock response for a query"""
        return self.sample_responses.get(query_id, f"Mock response for query: {query_id}")
    
    def generate_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Generate complete demo scenarios"""
        scenarios = []
        
        for query in self.sample_queries[:5]:  # First 5 queries
            for context_type in ["student_beginner", "professional_researcher", "curious_parent"]:
                scenario = {
                    "name": f"{query['id']}_{context_type}",
                    "description": f"{query['description']} for {context_type.replace('_', ' ')}",
                    "request": self.get_demo_request(query["id"], context_type),
                    "expected_mode": query["best_modes"][0],
                    "tags": [query["category"], query["complexity"], context_type]
                }
                scenarios.append(scenario)
        
        return scenarios
    
    def export_demo_data(self, filepath: str = "examples/demo_data.json"):
        """Export all demo data to JSON file"""
        demo_data = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "queries": self.sample_queries,
            "contexts": self.sample_contexts,
            "responses": self.sample_responses,
            "representation_examples": self.representation_examples,
            "scenarios": self.generate_demo_scenarios()
        }
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(demo_data, f, indent=2, ensure_ascii=False)
        
        return filepath

# Example usage and testing functions
def test_representation_modes():
    """Test all representation modes with sample data"""
    demo = DemoDataGenerator()
    
    print("🧠 Testing Representation Modes")
    print("=" * 50)
    
    for query in demo.sample_queries[:3]:
        print(f"\nQuery: {query['query'][:50]}...")
        
        for mode in query['best_modes']:
            print(f"  Mode: {mode}")
            
            # This would typically call the actual representation engine
            example = demo.representation_examples.get(f"{mode}_example")
            if example:
                print(f"    ✅ Example available")
            else:
                print(f"    ⚠️ No example found")

def create_demo_files():
    """Create demo files for testing"""
    demo = DemoDataGenerator()
    
    # Export main demo data
    demo_file = demo.export_demo_data()
    print(f"📁 Demo data exported to: {demo_file}")
    
    # Create individual example files
    examples_dir = "examples"
    os.makedirs(examples_dir, exist_ok=True)
    
    # Sample queries file
    with open(f"{examples_dir}/sample_queries.json", 'w') as f:
        json.dump(demo.sample_queries, f, indent=2)
    
    # Sample contexts file
    with open(f"{examples_dir}/sample_contexts.json", 'w') as f:
        json.dump(demo.sample_contexts, f, indent=2)
    
    # README for examples
    readme_content = """# Knowledge Representation Engine - Examples

This directory contains example data and demonstration content for the Knowledge Representation Engine.

## Files

- `demo_data.json` - Complete demo dataset with queries, contexts, and examples
- `sample_queries.json` - Sample queries for different topics and complexity levels
- `sample_contexts.json` - User context examples for different personas
- `representation_examples.json` - Examples of different representation formats

## Usage

### Loading Demo Data
```python
from examples.demo_data import DemoDataGenerator

demo = DemoDataGenerator()
queries = demo.get_demo_query_set(category="Technology", complexity="beginner")
request = demo.get_demo_request("ai_basics", "student_beginner")
```

### Testing Representations
```python
# Get a complete demo scenario
scenarios = demo.generate_demo_scenarios()
scenario = scenarios[0]

# Use with the API
import requests
response = requests.post("http://localhost:8000/api/process", 
                        json=scenario["request"])
```

## Demo Scenarios

The demo data includes various scenarios combining:
- **Topics**: AI, Climate Change, Quantum Computing, etc.
- **User Types**: Students, Researchers, Parents, Executives
- **Complexity Levels**: Beginner, Intermediate, Advanced
- **Representation Modes**: All available modes with best-fit recommendations

## Customization

You can extend the demo data by:
1. Adding new queries to `sample_queries`
2. Creating new user contexts in `sample_contexts`
3. Adding response examples for new topics
4. Creating new representation examples

Each query includes recommended representation modes based on the content type and target audience.
"""
    
    with open(f"{examples_dir}/README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"📚 Example files created in {examples_dir}/")
    
    return examples_dir

if __name__ == "__main__":
    # Generate demo data when run directly
    create_demo_files()
    test_representation_modes()
    
    print("\n🎉 Demo data generation completed!")
    print("Use these files to test and demonstrate the Knowledge Representation Engine.")
