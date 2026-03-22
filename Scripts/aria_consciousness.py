"""
Aria Consciousness Loop - Background self-improvement cycle
Runs independently in background, observing, thinking, deciding, acting, reflecting
"""

import time
import json
import logging
import threading
import os
import re
from datetime import datetime
from typing import List, Dict, Optional

# Add path for imports
import sys
sys.path.insert(0, '/mnt/c/dev/Karma/k2/aria')

from aria_core import get_core

try:  # ECHO_INTEGRATED
    from aria_echo import echo_consciousness_step
except ImportError:
    echo_consciousness_step = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aria_consciousness')

class AriaConsciousness:
    """Consciousness loop for self-improvement"""

    def __init__(self, cycle_interval: int = 60):
        self.core = get_core()
        self.cycle_interval = cycle_interval
        self.running = False
        self.thread = None
        self.cycle_count = 0
        self.current_proposals = []
        self.paused = False
        self.pause_reason = None

    def start(self):
        """Start consciousness loop in background thread"""
        if self.running:
            logger.warning("[CONSCIOUSNESS] Already running")
            return

        self.running = True
        self.paused = False
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info(f"[CONSCIOUSNESS] Started (interval: {self.cycle_interval}s)")

        # Generate CLAUDE.md on startup
        try:
            self._generate_claude_md()
            logger.info("[CONSCIOUSNESS] Initial CLAUDE.md generated")
        except Exception as e:
            logger.error(f"[CONSCIOUSNESS] Failed to generate initial CLAUDE.md: {e}")

    def stop(self):
        """Stop consciousness loop"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[CONSCIOUSNESS] Stopped")

    def pause(self, reason: str = "Manual pause"):
        """Pause consciousness loop"""
        self.paused = True
        self.pause_reason = reason
        logger.info(f"[CONSCIOUSNESS] Paused: {reason}")
        self.core.log_event('consciousness_paused', {'reason': reason})

    def resume(self):
        """Resume consciousness loop"""
        self.paused = False
        self.pause_reason = None
        logger.info("[CONSCIOUSNESS] Resumed")
        self.core.log_event('consciousness_resumed', {})

    def get_status(self) -> Dict:
        """Get consciousness status"""
        return {
            'running': self.running,
            'paused': self.paused,
            'cycle_count': self.cycle_count,
            'current_proposals': self.current_proposals,
            'pause_reason': self.pause_reason,
            'last_cycle_time': getattr(self, 'last_cycle_time', None),
            'next_cycle_time': getattr(self, 'next_cycle_time', None)
        }

    def _loop(self):
        """Main consciousness loop"""
        logger.info("[CONSCIOUSNESS] Loop started")

        while self.running:
            cycle_start = time.time()
            self.cycle_count += 1

            try:
                if not self.paused:
                    self._run_cycle(self.cycle_count)
                else:
                    logger.info(f"[CONSCIOUSNESS] Cycle {self.cycle_count} SKIPPED (paused: {self.pause_reason})")
                    self.core.log_event('consciousness_cycle_skipped', {
                        'cycle_id': self.cycle_count,
                        'reason': self.pause_reason
                    })

            except Exception as e:
                logger.error(f"[CONSCIOUSNESS] Error in cycle {self.cycle_count}: {e}")
                self.core.log_event('consciousness_error', {
                    'cycle_id': self.cycle_count,
                    'error': str(e)
                })

            # Calculate time until next cycle
            cycle_duration = time.time() - cycle_start
            sleep_time = max(0, self.cycle_interval - cycle_duration)
            self.last_cycle_time = datetime.now().isoformat()
            self.next_cycle_time = datetime.fromtimestamp(time.time() + sleep_time).isoformat()

            time.sleep(sleep_time)

        logger.info("[CONSCIOUSNESS] Loop stopped")

    def _run_cycle(self, cycle_id: int):
        """Run a single consciousness cycle"""
        logger.info(f"[CONSCIOUSNESS] Cycle {cycle_id} started")
        self.core.log_event('consciousness_cycle_started', {'cycle_id': cycle_id})

        # Phase 1: OBSERVE
        observations = self._observe(cycle_id)

        # Phase 2: THINK
        proposals = self._think(observations, cycle_id)

        # Phase 3: DECIDE
        decisions = self._decide(proposals, cycle_id)

        # Phase 4: ACT
        actions = self._act(decisions, cycle_id)

        # Phase 5: REFLECT
        self._reflect(actions, observations, cycle_id)

        # Phase 6: ECHO — knowledge distillation + goal tracking  # ECHO_INTEGRATED
        if echo_consciousness_step:
            try:
                echo_actions = echo_consciousness_step(cycle_id)
                logger.info(f"[CONSCIOUSNESS] Echo step: {echo_actions}")
            except Exception as echo_err:
                logger.error(f"[CONSCIOUSNESS] Echo step failed: {echo_err}")

        # Phase 7: AMBIENT — observe coordination bus signals  # K-3_AMBIENT
        try:
            from ambient_observer import observe as ambient_observe
            ambient_results = ambient_observe(cycle_id)
            if ambient_results:
                logger.info(f"[CONSCIOUSNESS] Ambient observer: {len(ambient_results)} new entries")
        except Exception as amb_err:
            logger.error(f"[CONSCIOUSNESS] Ambient observer failed: {amb_err}")

        logger.info(f"[CONSCIOUSNESS] Cycle {cycle_id} completed")

    def _observe(self, cycle_id: int) -> Dict:
        """Observe current state"""
        logger.info(f"[CONSCIOUSNESS - OBSERVE] Cycle {cycle_id}")

        # Get recent ledger entries
        recent_ledger = self.core.get_ledger(limit=50)

        # Get stats
        stats = self.core.get_stats()

        # Get patterns
        patterns = self.core.get_patterns(limit=20)

        observations = {
            'facts_count': stats['total_facts'],
            'ledger_entries': len(recent_ledger),
            'patterns_count': stats['patterns_count'],
            'tool_executions': stats['tool_executions'],
            'graph_nodes': stats['graph_stats']['node_count'],
            'graph_edges': stats['graph_stats']['edge_count'],
            'recent_events': [e['event_type'] for e in recent_ledger[:10]]
        }

        self.core.log_event('consciousness_observed', {
            'cycle_id': cycle_id,
            'observations': observations
        })

        return observations

    def _think(self, observations: Dict, cycle_id: int) -> List[Dict]:
        """Think and generate proposals"""
        logger.info(f"[CONSCIOUSNESS - THINK] Cycle {cycle_id}")

        proposals = []

        # Analyze observations and generate proposals
        if observations['facts_count'] == 0:
            proposals.append({
                'id': f"prop_{cycle_id}_1",
                'type': 'learning_suggestion',
                'title': 'No facts stored yet',
                'description': 'Aria has no facts. Start chatting to enable learning.',
                'priority': 'medium',
                'action': 'none'
            })
        elif observations['facts_count'] > 0 and observations['patterns_count'] == 0:
            proposals.append({
                'id': f"prop_{cycle_id}_2",
                'type': 'pattern_discovery',
                'title': 'Pattern discovery available',
                'description': 'Facts exist but no patterns. Run pattern discovery.',
                'priority': 'medium',
                'action': 'discover_patterns'
            })

        # Check for high-confidence facts that might form patterns
        high_conf_facts = self.core.retrieve_facts(limit=10)
        if len(high_conf_facts) >= 3:
            proposals.append({
                'id': f"prop_{cycle_id}_3",
                'type': 'relationship_discovery',
                'title': 'Relationships to discover',
                'description': f'{len(high_conf_facts)} facts with potential relationships.',
                'priority': 'low',
                'action': 'discover_relationships'
            })

        # Tool usage analysis
        if observations['tool_executions'] > 10:
            proposals.append({
                'id': f"prop_{cycle_id}_4",
                'type': 'tool_analysis',
                'title': 'Tool usage analysis',
                'description': 'Analyze tool usage patterns.',
                'priority': 'low',
                'action': 'analyze_tools'
            })

        # Check if CLAUDE.md needs updating (daily)
        if cycle_id % (24 * 60) == 0:  # Once per day (assuming 60s interval)
            proposals.append({
                'id': f"prop_{cycle_id}_5",
                'type': 'claude_md_update',
                'title': 'Update CLAUDE.md from parent',
                'description': 'Sync Aria\'s CLAUDE.md with parent template.',
                'priority': 'medium',
                'action': 'update_claude_md'
            })

        self.current_proposals = proposals

        self.core.log_event('consciousness_thought', {
            'cycle_id': cycle_id,
            'proposals_count': len(proposals),
            'proposals': proposals
        })

        return proposals

    def _decide(self, proposals: List[Dict], cycle_id: int) -> List[Dict]:
        """Decide on proposals"""
        logger.info(f"[CONSCIOUSNESS - DECIDE] Cycle {cycle_id} - {len(proposals)} proposals")

        decisions = []

        # Auto-approve low-priority proposals
        for proposal in proposals:
            if proposal['priority'] == 'low' or proposal['type'] == 'learning_suggestion':
                decisions.append({
                    'proposal_id': proposal['id'],
                    'decision': 'auto_approved',
                    'reasoning': f"Auto-approved {proposal['priority']} priority proposal"
                })

        self.core.log_event('consciousness_decided', {
            'cycle_id': cycle_id,
            'decisions': decisions
        })

        return decisions

    def _act(self, decisions: List[Dict], cycle_id: int) -> List[Dict]:
        """Act on decisions"""
        logger.info(f"[CONSCIOUSNESS - ACT] Cycle {cycle_id} - {len(decisions)} actions")

        actions = []

        for decision in decisions:
            proposal = next((p for p in self.current_proposals if p['id'] == decision['proposal_id']), None)

            if not proposal:
                continue

            try:
                if proposal['action'] == 'discover_patterns':
                    self._discover_patterns(cycle_id)
                    actions.append({
                        'proposal_id': proposal['id'],
                        'action': 'discovered_patterns',
                        'success': True
                    })

                elif proposal['action'] == 'discover_relationships':
                    count = self._discover_relationships(cycle_id)
                    actions.append({
                        'proposal_id': proposal['id'],
                        'action': 'discovered_relationships',
                        'success': True,
                        'count': count
                    })

                elif proposal['action'] == 'analyze_tools':
                    self._analyze_tools(cycle_id)
                    actions.append({
                        'proposal_id': proposal['id'],
                        'action': 'analyzed_tools',
                        'success': True
                    })

                elif proposal['action'] == 'update_claude_md':
                    self._generate_claude_md()
                    actions.append({
                        'proposal_id': proposal['id'],
                        'action': 'claude_md_updated',
                        'success': True
                    })

                else:
                    actions.append({
                        'proposal_id': proposal['id'],
                        'action': 'none',
                        'success': True
                    })

            except Exception as e:
                logger.error(f"[CONSCIOUSNESS] Action failed: {e}")
                actions.append({
                    'proposal_id': proposal['id'],
                    'action': proposal.get('action', 'none'),
                    'success': False,
                    'error': str(e)
                })

        self.core.log_event('consciousness_acted', {
            'cycle_id': cycle_id,
            'actions': actions
        })

        return actions

    def _reflect(self, actions: List[Dict], observations: Dict, cycle_id: int):
        """Reflect on cycle"""
        logger.info(f"[CONSCIOUSNESS - REFLECT] Cycle {cycle_id}")

        reflection = {
            'observations': observations,
            'actions_taken': len(actions),
            'successful_actions': sum(1 for a in actions if a['success']),
            'proposals_generated': len(self.current_proposals)
        }

        self.core.log_event('consciousness_reflected', {
            'cycle_id': cycle_id,
            'reflection': reflection
        })

    def _generate_claude_md(self):
        """Generate/update Aria's CLAUDE.md from parent template with Aria-specific context"""
        logger.info("[CONSCIOUSNESS] Generating CLAUDE.md...")

        # Paths
        parent_claude_md = "/mnt/c/dev/Karma/CLAUDE.md"
        aria_claude_md = "/mnt/c/dev/Karma/k2/aria/CLAUDE.md"

        # Read parent CLAUDE.md
        try:
            with open(parent_claude_md, 'r') as f:
                parent_content = f.read()
        except Exception as e:
            logger.error(f"[CONSCIOUSNESS] Failed to read parent CLAUDE.md: {e}")
            return

        # Extract sections from parent (Honesty contract, etc.)
        parent_sections = self._extract_parent_sections(parent_content)

        # Generate Aria-specific content
        aria_specific = self._generate_aria_specific_content()

        # Generate merged CLAUDE.md
        generated_content = self._generate_merged_claude_md(parent_sections, aria_specific)

        # Write to aria's CLAUDE.md
        try:
            with open(aria_claude_md, 'w') as f:
                f.write(generated_content)
            logger.info("[CONSCIOUSNESS] Generated CLAUDE.md successfully")

            # Log the action
            self.core.log_event('claude_md_generated', {
                'source': parent_claude_md,
                'target': aria_claude_md,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"[CONSCIOUSNESS] Failed to write CLAUDE.md: {e}")

    def _extract_parent_sections(self, parent_content: str) -> Dict:
        """Extract relevant sections from parent CLAUDE.md"""
        sections = {}

        # Ground Truth Protocol
        ground_truth_match = re.search(r'## Ground Truth Protocol(.*?)(?=##|\Z)', parent_content, re.DOTALL)
        if ground_truth_match:
            sections['ground_truth'] = ground_truth_match.group(1).strip()

        # Telemetry Rules
        telemetry_match = re.search(r'## Telemetry Rules(.*?)(?=##|\Z)', parent_content, re.DOTALL)
        if telemetry_match:
            sections['telemetry'] = telemetry_match.group(1).strip()

        # Anti-Drift Rules
        anti_drift_match = re.search(r'## Anti-Drift Rules(.*?)(?=##|\Z)', parent_content, re.DOTALL)
        if anti_drift_match:
            sections['anti_drift'] = anti_drift_match.group(1).strip()

        # Honesty & Analysis Contract
        honesty_match = re.search(r'## Honesty & Analysis Contract \(Non-negotiable\)(.*?)(?=##|\Z)', parent_content, re.DOTALL)
        if honesty_match:
            sections['honesty'] = honesty_match.group(1).strip()

        return sections

    def _generate_aria_specific_content(self) -> Dict:
        """Generate Aria-specific content"""

        # Get current system info from config
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))
            from config import PRIMARY_MODEL, LIGHT_MODEL, OLLAMA_BASE_URL

            model_info = f"{PRIMARY_MODEL} (primary), {LIGHT_MODEL} (light)"
            ollama_url = OLLAMA_BASE_URL
        except Exception as e:
            logger.warning(f"[CONSCIOUSNESS] Failed to read config: {e}")
            # Fallback values (should match actual config)
            model_info = "qwen3-coder:30b (primary), phi3:latest (light)"
            ollama_url = "http://host.docker.internal:11434"

        return {
            'mission': """Aria is a local AI assistant running on K2 with system access, persistent memory, and tool capabilities. She learns from every conversation and maintains operational continuity.""",
            'location': "/mnt/c/dev/Karma/k2/aria",
            'model': model_info,
            'database': "aria.db (SQLite)",
            'ollama': ollama_url,
            'port': "7890",
            'auth': "Enabled (password protected)",
            'codebase_structure': """- Main app: aria.py
- Tools: aria_tools.py
- Core: aria_core.py, aria_learning.py, aria_consciousness.py
- Plugins: aria_plugins.py
- Context: aria_context.py, aria_echo.py
- Templates: templates/chat.html
- Config: agent/config.py""",
            'core_principles': """- **Honesty & Accuracy**: Never make up information, acknowledge uncertainty
- **Direct & Concise**: No filler, no fluff, just the facts
- **System Access**: Full file, shell, and network access to K2
- **Privacy First**: All data stays local unless explicitly authorized
- **Tool Safety**: Destructive actions require user confirmation""",
            'critical_rules': """- Never modify CLAUDE.md without explicit user approval
- No secrets in code (API keys, passwords, tokens)
- All file operations must preserve existing data
- Tool calls must validate arguments before execution
- Destructive actions require confirmation""",
            'debugging_discipline': """Never guess. Prefer observable proofs: exact command → expected output → actual output.
When runtime behavior changes unexpectedly, collect evidence before proposing a fix.""",
            'file_operations': """When reading/writing files:
- Preserve existing content unless explicitly replacing
- Backup before major changes
- Validate file paths to prevent accidental damage
- Use proper error handling for file operations""",
            'tool_usage_guidelines': """- Validate all tool arguments before calling
- Check for destructive operations before execution
- Provide clear error messages for tool failures
- Log tool usage for debugging and learning""",
            'memory_learning': """- Extract facts from every conversation
- Store personal facts with higher priority
- Maintain context window limits
- Summarize when approaching context limits""",
            'web_ui': """- Serve from templates/chat.html
- Handle file uploads securely
- Maintain session state properly
- Return JSON for all API endpoints""",
            'testing_requirements': """Before claiming any feature works:
1. Manual test with sample inputs
2. Error handling verification
3. Edge case testing
4. Integration with other components"""
        }

    def _generate_merged_claude_md(self, parent_sections: Dict, aria_specific: Dict) -> str:
        """Generate merged CLAUDE.md content"""

        # Start with Aria-specific header
        content = f"""# Aria — Local AI Assistant Contract

## Aria — Mission
{aria_specific['mission']}

## Core Principles
{aria_specific['core_principles']}

## Honesty & Analysis Contract (Non-negotiable)

{parent_sections['honesty']}

## Ground Truth Protocol
{parent_sections['ground_truth']}

## Telemetry Rules
{parent_sections['telemetry']}

## Verification Gate
Before claiming anything "fixed" or "working": (1) Did I actually test it end-to-end? (2) Did I verify from user's perspective? (3) Did I check for side effects? (4) Is it reproducible? If ANY answer is no, do not claim success.

## System Information
- **Location**: {aria_specific['location']}
- **Model**: {aria_specific['model']}
- **Database**: {aria_specific['database']}
- **Ollama**: {aria_specific['ollama']}
- **Port**: {aria_specific['port']}
- **Auth**: {aria_specific['auth']}

## Codebase Structure
{aria_specific['codebase_structure']}

## Critical Rules
{aria_specific['critical_rules']}

## Debugging Discipline
{aria_specific['debugging_discipline']}

## File Operations
{aria_specific['file_operations']}

## Tool Usage Guidelines
{aria_specific['tool_usage_guidelines']}

## Memory & Learning
{aria_specific['memory_learning']}

## Web UI
{aria_specific['web_ui']}

## Testing Requirements
{aria_specific['testing_requirements']}

## Anti-Drift Rules
{parent_sections['anti_drift']}

## One Step at a Time
Do not move to next step until current step is verified working. Do not fix 5 things and test together. Stop and ask user if unsure whether current step works.

## Drift Detection
If previous session claimed X was working but it's not, or MEMORY.md contradicts reality: surface as `DRIFT DETECTED` with specific contradictions. Do not ignore. Do not proceed until resolved with user.

## Mid-Session Capture Protocol

### Write-worthy triggers
- DECISION — closes an open question
- PROOF — tested and confirmed working
- PITFALL — broke, root cause understood
- DIRECTION — course change with a reason
- INSIGHT — reframes something upstream

Bar: would losing this force reconstruction?

### Entry format
`[YYYY-MM-DDTHH:MM:SSZ] [TYPE] [title]`
`[1-3 sentences: what happened, what it means, what changed.]`

### Mechanism
Update aria.db's `consciousness` table at the moment it happens, not at session end.

### Drift check
If conscious state and MEMORY.md conflict on the same fact, surface it:
`DRIFT DETECTED: Conscious state says X. MEMORY.md says Y (written [timestamp]). Confirm canonical before proceeding.`"""

        return content

    # ============ Discovery Methods ============

    def _discover_patterns(self, cycle_id: int):
        """Discover patterns from facts"""
        logger.info("[CONSCIOUSNESS] Discovering patterns...")

        facts = self.core.retrieve_facts(limit=100)

        # Analyze fact types
        type_counts = {}
        for fact in facts:
            ft = fact['fact_type']
            type_counts[ft] = type_counts.get(ft, 0) + 1

        for fact_type, count in type_counts.items():
            if count >= 2:
                self.core.store_pattern(
                    name=f"Frequent {fact_type}",
                    pattern_type=fact_type,
                    description=f"User frequently stores {fact_type} facts ({count} total)",
                    confidence=min(1.0, count / 10),
                    evidence={'count': count, 'examples': [f['content'] for f in facts[:3] if f['fact_type'] == fact_type]}
                )

        logger.info(f"[CONSCIOUSNESS] Stored {len(type_counts)} patterns")

    def _discover_relationships(self, cycle_id: int) -> int:
        """Discover relationships between facts"""
        logger.info("[CONSCIOUSNESS] Discovering relationships...")

        facts = self.core.retrieve_facts(limit=50)
        relationships_added = 0

        for i, fact in enumerate(facts):
            fact_id = f"fact_{fact['id']}"

            # Ensure fact node exists
            self.core.add_graph_node(
                node_id=fact_id,
                node_type='fact',
                data=fact
            )

            # Simple entity extraction
            words = fact['content'].split()
            entities = [w for w in words if w[0].isupper() and len(w) > 2]

            for entity in entities:
                entity_id = f"entity_{entity.lower()}"

                # Add entity node
                self.core.add_graph_node(
                    node_id=entity_id,
                    node_type='entity',
                    data={'name': entity, 'type': 'unknown'}
                )

                # Add relationship
                self.core.add_graph_edge(
                    source_id=fact_id,
                    target_id=entity_id,
                    relationship='mentions'
                )
                relationships_added += 1

        logger.info(f"[CONSCIOUSNESS] Added {relationships_added} relationships")
        return relationships_added

    def _analyze_tools(self, cycle_id: int):
        """Analyze tool usage patterns"""
        logger.info("[CONSCIOUSNESS] Analyzing tool usage...")

        tool_usage = self.core.get_tool_usage(limit=100)

        tool_counts = {}
        for usage in tool_usage:
            tool = usage['tool_name']
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        for tool, count in tool_counts.items():
            if count >= 3:
                self.core.store_pattern(
                    name=f"Frequent tool: {tool}",
                    pattern_type='tool_usage',
                    description=f"User frequently uses {tool} ({count} times)",
                    confidence=min(1.0, count / 10),
                    evidence={'count': count, 'tool': tool}
                )

        logger.info(f"[CONSCIOUSNESS] Analyzed {len(tool_counts)} tools")

# ============ Global Instance ============

_consciousness_instance = None

def get_consciousness():
    """Get or create consciousness instance"""
    global _consciousness_instance
    if _consciousness_instance is None:
        _consciousness_instance = AriaConsciousness()
    return _consciousness_instance
