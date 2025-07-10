// static/js/representations.js
// Enhanced JavaScript for Knowledge Representation Engine

/**
 * Knowledge Representation Visualizer
 * Provides enhanced visualization and interaction capabilities
 */
class KnowledgeRepresentationVisualizer {
    constructor() {
        this.initialized = false;
        this.animations = [];
        this.observers = {};
        this.themes = {
            light: {
                background: '#ffffff',
                primary: '#2563eb',
                secondary: '#7c3aed',
                text: '#1f2937',
                border: '#e5e7eb'
            },
            dark: {
                background: '#1f2937',
                primary: '#60a5fa',
                secondary: '#a78bfa',
                text: '#f9fafb',
                border: '#374151'
            }
        };
        this.currentTheme = 'light';
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        this.setupEventListeners();
        this.setupIntersectionObserver();
        this.setupThemeDetection();
        this.setupAccessibility();
        this.initialized = true;
        
        console.log('🧠 Knowledge Representation Visualizer initialized');
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="#"]')) {
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });

        // Enhanced form interactions
        document.addEventListener('focus', (e) => {
            if (e.target.matches('.form-input')) {
                e.target.parentElement.classList.add('focused');
            }
        });

        document.addEventListener('blur', (e) => {
            if (e.target.matches('.form-input')) {
                e.target.parentElement.classList.remove('focused');
            }
        });

        // Keyboard navigation for cards
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                if (e.target.matches('.enhanced-card[tabindex]')) {
                    e.preventDefault();
                    e.target.click();
                }
            }
        });
    }

    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        this.observers.animation = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, options);

        // Observe all cards and content sections
        document.querySelectorAll('.enhanced-card, .representation-container').forEach(el => {
            this.observers.animation.observe(el);
        });
    }

    setupThemeDetection() {
        // Detect system theme preference
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        this.updateTheme(mediaQuery.matches ? 'dark' : 'light');
        
        mediaQuery.addEventListener('change', (e) => {
            this.updateTheme(e.matches ? 'dark' : 'light');
        });
    }

    updateTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update any active visualizations
        this.refreshVisualizations();
    }

    setupAccessibility() {
        // Add focus management for modals and dropdowns
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const activeModal = document.querySelector('.modal.active');
                if (activeModal) {
                    this.closeModal(activeModal);
                }
            }
        });

        // Announce dynamic content changes to screen readers
        this.ariaLiveRegion = document.createElement('div');
        this.ariaLiveRegion.setAttribute('aria-live', 'polite');
        this.ariaLiveRegion.setAttribute('aria-atomic', 'true');
        this.ariaLiveRegion.className = 'sr-only';
        document.body.appendChild(this.ariaLiveRegion);
    }

    announceToScreenReader(message) {
        this.ariaLiveRegion.textContent = message;
        setTimeout(() => {
            this.ariaLiveRegion.textContent = '';
        }, 1000);
    }

    // Knowledge Graph Visualization
    initializeKnowledgeGraph(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container || !data) return;

        const defaultOptions = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: { 
                    size: 14, 
                    color: this.themes[this.currentTheme].text 
                },
                borderWidth: 2,
                shadow: true,
                color: {
                    background: this.themes[this.currentTheme].primary,
                    border: this.themes[this.currentTheme].border
                }
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: { type: 'continuous' },
                color: {
                    color: this.themes[this.currentTheme].border,
                    hover: this.themes[this.currentTheme].primary
                }
            },
            physics: {
                enabled: true,
                stabilization: { iterations: 100 },
                barnesHut: {
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 300,
                hideEdgesOnDrag: false
            }
        };

        const networkOptions = { ...defaultOptions, ...options };
        
        try {
            const network = new vis.Network(container, data, networkOptions);
            
            // Add interaction handlers
            network.on('click', (params) => {
                if (params.nodes.length > 0) {
                    this.handleNodeClick(params.nodes[0], data);
                }
            });

            network.on('hoverNode', (params) => {
                this.highlightConnectedNodes(network, params.node);
            });

            network.on('blurNode', () => {
                this.resetNodeHighlight(network);
            });

            // Store reference for theme updates
            this.activeNetworks = this.activeNetworks || [];
            this.activeNetworks.push({ network, container, data, options: networkOptions });

            return network;
        } catch (error) {
            console.error('Error initializing knowledge graph:', error);
            this.showError(container, 'Failed to load knowledge graph');
        }
    }

    handleNodeClick(nodeId, data) {
        const node = data.nodes.find(n => n.id === nodeId);
        if (node) {
            this.showNodeDetails(node);
        }
    }

    showNodeDetails(node) {
        const modal = this.createModal('Node Details', `
            <div class="node-details">
                <h3>${node.label}</h3>
                <p><strong>Type:</strong> ${node.type || 'Unknown'}</p>
                <p><strong>Description:</strong> ${node.description || 'No description available'}</p>
                <div class="node-connections">
                    <h4>Connections:</h4>
                    <ul id="node-connections-list"></ul>
                </div>
            </div>
        `);
        
        this.showModal(modal);
    }

    highlightConnectedNodes(network, nodeId) {
        const connectedNodes = network.getConnectedNodes(nodeId);
        const connectedEdges = network.getConnectedEdges(nodeId);
        
        const updateOptions = {
            nodes: {
                color: {
                    background: this.themes[this.currentTheme].background,
                    border: this.themes[this.currentTheme].border
                }
            },
            edges: {
                color: { color: this.themes[this.currentTheme].border }
            }
        };

        // Highlight connected nodes
        connectedNodes.forEach(id => {
            network.updateCluster(id, {
                color: {
                    background: this.themes[this.currentTheme].secondary,
                    border: this.themes[this.currentTheme].primary
                }
            });
        });
    }

    resetNodeHighlight(network) {
        // Reset all nodes to default styling
        network.setOptions({
            nodes: {
                color: {
                    background: this.themes[this.currentTheme].primary,
                    border: this.themes[this.currentTheme].border
                }
            }
        });
    }

    // Timeline Visualization
    initializeTimeline(containerId, events, options = {}) {
        const container = document.getElementById(containerId);
        if (!container || !events) return;

        container.innerHTML = '';
        container.className = 'timeline-container-enhanced';

        const timeline = document.createElement('div');
        timeline.className = 'timeline-enhanced';

        events.forEach((event, index) => {
            const eventElement = this.createTimelineEvent(event, index);
            timeline.appendChild(eventElement);
        });

        container.appendChild(timeline);
        this.animateTimeline(timeline);
    }

    createTimelineEvent(event, index) {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'timeline-event-enhanced';
        eventDiv.style.animationDelay = `${index * 0.1}s`;

        eventDiv.innerHTML = `
            <div class="timeline-marker-enhanced"></div>
            <div class="timeline-content-enhanced">
                <div class="timeline-date">${event.date}</div>
                <div class="timeline-title">${event.title || event.event}</div>
                <div class="timeline-description">${event.description || ''}</div>
            </div>
        `;

        return eventDiv;
    }

    animateTimeline(timeline) {
        const events = timeline.querySelectorAll('.timeline-event-enhanced');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slide-in-left');
                }
            });
        }, { threshold: 0.1 });

        events.forEach(event => observer.observe(event));
    }

    // Collapsible Concepts
    initializeCollapsibleConcepts(containerId, concepts) {
        const container = document.getElementById(containerId);
        if (!container || !concepts) return;

        container.innerHTML = '';
        container.className = 'collapsible-concepts-enhanced';

        concepts.forEach(concept => {
            const conceptElement = this.createCollapsibleConcept(concept);
            container.appendChild(conceptElement);
        });
    }

    createCollapsibleConcept(concept) {
        const conceptDiv = document.createElement('div');
        conceptDiv.className = 'concept-item-enhanced';

        const header = document.createElement('div');
        header.className = 'concept-header-enhanced';
        header.innerHTML = `
            <div class="concept-title">
                <span class="concept-icon">${concept.icon || '📝'}</span>
                <span class="concept-name">${concept.title || concept.name}</span>
            </div>
            <div class="concept-toggle">
                <i class="fas fa-chevron-down"></i>
            </div>
        `;

        const content = document.createElement('div');
        content.className = 'concept-content-enhanced';
        content.innerHTML = `
            <p>${concept.content || concept.description}</p>
            ${concept.children ? this.renderConceptChildren(concept.children) : ''}
        `;

        header.addEventListener('click', () => {
            this.toggleConcept(conceptDiv, content);
        });

        conceptDiv.appendChild(header);
        conceptDiv.appendChild(content);

        return conceptDiv;
    }

    toggleConcept(conceptDiv, content) {
        const isOpen = conceptDiv.classList.contains('open');
        const toggle = conceptDiv.querySelector('.concept-toggle i');
        
        if (isOpen) {
            conceptDiv.classList.remove('open');
            content.style.maxHeight = '0';
            toggle.style.transform = 'rotate(0deg)';
        } else {
            conceptDiv.classList.add('open');
            content.style.maxHeight = content.scrollHeight + 'px';
            toggle.style.transform = 'rotate(180deg)';
        }
    }

    renderConceptChildren(children) {
        if (!children || children.length === 0) return '';
        
        return `
            <div class="concept-children">
                ${children.map(child => `
                    <div class="concept-child">
                        <strong>${child.title || child.name}:</strong>
                        ${child.content || child.description}
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Interactive Elements
    initializeInteractiveElements(containerId, elements) {
        const container = document.getElementById(containerId);
        if (!container || !elements) return;

        container.innerHTML = '';
        container.className = 'interactive-elements-container';

        elements.forEach(element => {
            const elementDiv = this.createInteractiveElement(element);
            container.appendChild(elementDiv);
        });
    }

    createInteractiveElement(element) {
        const elementDiv = document.createElement('div');
        elementDiv.className = 'interactive-element-enhanced';

        switch (element.type) {
            case 'question':
                return this.createQuestionElement(element);
            case 'scenario':
                return this.createScenarioElement(element);
            case 'quiz':
                return this.createQuizElement(element);
            default:
                return this.createDefaultInteractiveElement(element);
        }
    }

    createQuestionElement(element) {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'interactive-question';
        questionDiv.innerHTML = `
            <h4>${element.question}</h4>
            <div class="question-options">
                ${element.options.map((option, index) => `
                    <button class="option-btn" data-option="${index}">
                        ${option}
                    </button>
                `).join('')}
            </div>
        `;

        questionDiv.addEventListener('click', (e) => {
            if (e.target.matches('.option-btn')) {
                this.handleQuestionAnswer(e.target, element);
            }
        });

        return questionDiv;
    }

    handleQuestionAnswer(button, element) {
        const selectedOption = parseInt(button.dataset.option);
        
        // Visual feedback
        button.classList.add('selected');
        
        // Show result or next step
        if (element.onAnswer) {
            element.onAnswer(selectedOption);
        } else {
            this.showToast(`You selected: ${element.options[selectedOption]}`, 'info');
        }
    }

    // Utility Methods
    createModal(title, content, className = '') {
        const modal = document.createElement('div');
        modal.className = `modal ${className}`;
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        modal.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal(modal);
        });

        modal.querySelector('.modal-backdrop').addEventListener('click', () => {
            this.closeModal(modal);
        });

        return modal;
    }

    showModal(modal) {
        document.body.appendChild(modal);
        modal.classList.add('active');
        
        // Focus management
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }

    closeModal(modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            document.body.removeChild(modal);
        }, 300);
    }

    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close">&times;</button>
            </div>
        `;

        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });

        document.body.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            this.removeToast(toast);
        }, duration);
    }

    removeToast(toast) {
        toast.classList.add('removing');
        setTimeout(() => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        }, 300);
    }

    showError(container, message) {
        container.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
    }

    // Performance and cleanup
    refreshVisualizations() {
        if (this.activeNetworks) {
            this.activeNetworks.forEach(({ network, options }) => {
                network.setOptions({
                    ...options,
                    nodes: {
                        ...options.nodes,
                        color: {
                            background: this.themes[this.currentTheme].primary,
                            border: this.themes[this.currentTheme].border
                        }
                    }
                });
            });
        }
    }

    cleanup() {
        // Remove event listeners and observers
        Object.values(this.observers).forEach(observer => {
            observer.disconnect();
        });

        // Clean up active networks
        if (this.activeNetworks) {
            this.activeNetworks.forEach(({ network }) => {
                network.destroy();
            });
        }

        // Remove aria live region
        if (this.ariaLiveRegion && this.ariaLiveRegion.parentNode) {
            document.body.removeChild(this.ariaLiveRegion);
        }
    }
}

// Utility functions for common operations
const RepresentationUtils = {
    // Format text for display
    formatText(text, maxLength = 100) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    // Extract keywords from text
    extractKeywords(text, maxKeywords = 10) {
        if (!text) return [];
        
        const stopWords = ['the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'there', 'here', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'whose', 'whom', 'an', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'];
        
        const words = text.toLowerCase()
            .replace(/[^\w\s]/g, '')
            .split(/\s+/)
            .filter(word => word.length > 3 && !stopWords.includes(word));
        
        const frequency = {};
        words.forEach(word => {
            frequency[word] = (frequency[word] || 0) + 1;
        });
        
        return Object.entries(frequency)
            .sort((a, b) => b[1] - a[1])
            .slice(0, maxKeywords)
            .map(([word]) => word);
    },

    // Generate color palette
    generateColorPalette(count = 5) {
        const colors = [];
        const hueStep = 360 / count;
        
        for (let i = 0; i < count; i++) {
            const hue = i * hueStep;
            const color = `hsl(${hue}, 70%, 50%)`;
            colors.push(color);
        }
        
        return colors;
    },

    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function for performance
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize the visualizer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.knowledgeViz = new KnowledgeRepresentationVisualizer();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { KnowledgeRepresentationVisualizer, RepresentationUtils };
}

// Global functions for template use
window.initializeKnowledgeGraph = (containerId, data, options) => {
    return window.knowledgeViz.initializeKnowledgeGraph(containerId, data, options);
};

window.initializeTimeline = (containerId, events, options) => {
    return window.knowledgeViz.initializeTimeline(containerId, events, options);
};

window.initializeCollapsibleConcepts = (containerId, concepts) => {
    return window.knowledgeViz.initializeCollapsibleConcepts(containerId, concepts);
};

window.initializeInteractiveElements = (containerId, elements) => {
    return window.knowledgeViz.initializeInteractiveElements(containerId, elements);
};