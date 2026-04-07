# vinkius-labs_mcp-fusion_ Reduce MCP tool count by 10-100x. TypeScript framework that groups related operations behind discri

*Converted from: vinkius-labs_mcp-fusion_ Reduce MCP tool count by 10-100x. TypeScript framework that groups related operations behind discri.PDF*



---
*Page 1*


mcp-fusion
Code Issues 5 More
Watch 0
Reduce MCP tool count by 10-100x. TypeScript framework that groups related operations behind discriminators, with automatic schema generation,
type-safe validation, token-optimized descriptions, and hierarchical grouping for enterprise-scale APIs.
Apache-2.0 license
Code of conduct
Contributing
Security policy
42 stars 1 fork 0 watching 1Branch 9Tags Activity Custom properties
Public repository
main 1Branch 9Tags Go to file t Go to file Add file Code
renatomarinho chore: bump version to 0.7.0 6896dd0 · 1 hour ago
.github Add CI & publish workflows; rebrand to vinkius-c… last week
docs v0.5.0: idiomatic TypeScript naming, ESLint integ… 4 hours ago
src dx: comprehensive JSDoc across entire codebase 1 hour ago
tests test: add createTool + Result monad tests, updat… 1 hour ago
.gitignore chore: initial release v0.1.0 last week
CHANGELOG.md v0.6.0: strict TypeScript, immutable data models,… 3 hours ago
CODE_OF_CONDUCT.md chore: initial release v0.1.0 last week
CONTRIBUTING.md chore: release v0.1.1 last week
LICENSE chore: initial release v0.1.0 last week
README.md chore: remove external company references, upd… 2 hours ago
SECURITY.md chore: initial release v0.1.0 last week
eslint.config.js refactor: bounded context architecture (Anthropi… 2 hours ago
llms.txt dx: add llms.txt for AI-assisted development 1 hour ago
package-lock.json v0.5.0: idiomatic TypeScript naming, ESLint integ… 4 hours ago
package.json chore: bump version to 0.7.0 1 hour ago
release-notes.md v0.6.0: strict TypeScript, immutable data models,… 3 hours ago
tsconfig.json refactor: bounded context architecture (Anthropi… 2 hours ago
⚡ mcp-fusion
The Enterprise Multiplexer for MCP. Route 5,000+ endpoints through a single LLM tool.


---
*Page 2*


npm v0.7.0 TypeScript 5.7+ MCP Standard License Apache2.0
Stop registering hundreds of individual Model Context Protocol (MCP) tools. Ship ONE.
mcp-fusion is an advanced TypeScript framework that consolidates related MCP operations into a single tool behind a discriminator field.
Built with a strict domain model layer for hierarchical entity management and a build-time strategy engine designed to scale to 5,000+
endpoints.
Fewer tools mean less context pressure on the LLM, zero routing hallucinations, and radically cleaner server code.
npm install @vinkius-core/mcp-fusion zod
🚨 The Architectural Bottleneck: Context Collapse
Standard MCP servers that expose individual tools for every CRUD operation (create_project, update_project, delete_project,
list_projects) create two cascading system failures:
1. Context Exhaustion: Every tool definition burns expensive tokens in the LLM's context window. At 30+ tools, API costs explode and the
model's memory degrades.
2. Routing Confusion: Semantically similar tools compete for selection. The LLM hallucinates parameters or picks update_project when it
should pick create_project.
The workaround is writing fewer, bloated tools — or rotating tool sets per conversation. Both are brittle.
✅ The Solution: Build-Time Multiplexing & Context Gating
Group related operations under a single tool. The LLM sees ONE tool and selects the exact operation through an enum.
platform action
The framework handles description generation, schema composition, annotation aggregation, middleware compilation, strict validation, and
error formatting — all at build time.
mcp-fusion - Enterprise Gate
LLM
Sees ONE Tool
Gateway
Context Gating
🤯 The "Aha!" Moment: What the LLM Actually Sees
Instead of flooding the LLM with 50 fragile JSON schemas, mcp-fusion uses Zod AST introspection to cross-reference every field across all
actions. Five individual tools become one registered tool.
The LLM simply sees this mathematically perfect, auto-generated prompt:
Action: list | create | delete
- 'list': Requires: workspace_id. For: list


---
*Page 3*


- 'create': Requires: workspace_id, name. For: create
- 'delete': Requires: workspace_id, project_id ⚠ DESTRUCTIVE
No guessing. No hallucinated parameters. Absolute routing precision.
🚀 Quick Start (Frictionless Setup)
import { GroupedToolBuilder, ToolRegistry, success, error } from '@vinkius-core/mcp-fusion';
import { z } from 'zod';
const projects = new GroupedToolBuilder<AppContext>('projects')
.description('Manage projects')
// Shared parameters injected into every action safely
.commonSchema(z.object({
workspace_id: z.string().describe('Workspace identifier'),
}))
.action({
name: 'list',
readOnly: true,
schema: z.object({ status: z.enum(['active', 'archived']).optional() }),
handler: async (ctx, args) => {
// args is fully typed: { workspace_id: string, status?: 'active' | 'archived' }
const projects = await ctx.db.projects.findMany({ where: { workspaceId: args.workspace_id, status: args.s
return success(projects);
},
})
.action({
name: 'create',
schema: z.object({ name: z.string(), description: z.string().optional() }),
handler: async (ctx, args) => {
const project = await ctx.db.projects.create({ data: { workspaceId: args.workspace_id, name: args.name, d
return success(project);
},
})
.action({
name: 'delete',
destructive: true, // Auto-appends ⚠ DESTRUCTIVE to LLM description
schema: z.object({ project_id: z.string() }),
handler: async (ctx, args) => {
await ctx.db.projects.delete({ where: { id: args.project_id } });
return success('Project deleted');
},
});
// Attach to ANY standard MCP Server (Duck-typed)
const registry = new ToolRegistry<AppContext>();
registry.register(projects);
registry.attachToServer(server, {
contextFactory: (extra) => createAppContext(extra),
});
→ Read the full Getting Started Guide
🏗 Enterprise Engineering Core
This is not a simple utility wrapper. mcp-fusion is a high-performance routing engine built for massive scale, strict security boundaries, and
zero-allocation runtime execution.
Token Management at Scale — Tag-Based Selective Exposure
"5,000 endpoints — won't that blow up the token context?" No.
The framework uses a 3-layer Context Gating strategy to keep token usage strictly under control:


---
*Page 4*


1. Layer 1 — Grouping reduces tool count: Instead of 5,000 individual tools, a platform tool with 50 actions is ONE tool definition in
tools/list. The LLM sees 1 tool, not 50.
2. Layer 2 — Tag filtering controls what the LLM sees: You do NOT expose all tools at once. Each builder has .tags(), and
attachToServer() accepts a filter with tags (include) and exclude options.
3. Layer 3 — TOON compresses descriptions: For tools that ARE exposed, metadata is compressed.
// Register 5,000 endpoints across domain-specific grouped tools
const usersTool = new GroupedToolBuilder<AppContext>('users').tags('core').group(...);
const adminTool = new GroupedToolBuilder<AppContext>('admin').tags('admin', 'internal').group(...);
registry.registerAll(usersTool, adminTool);
// Conversation about user management? Expose only core tools:
registry.attachToServer(server, { filter: { tags: ['core'] } }); // LLM sees: 1 tool
// Full access, but never internal tools:
registry.attachToServer(server, { filter: { exclude: ['internal'] } });
Tag filtering acts as a context gate — you control exactly what the LLM sees, per session.
Two-Layer Architecture
1. Layer 1 — Domain Model: A hierarchical entity model for MCP primitives (Group, Tool, Prompt, Resource, PromptArgument) with tree
traversal, multi-parent leaves, fully-qualified names (dot-separated, configurable separator), metadata maps, icons, and bidirectional type
converters. This is the structural backbone — think of it as the AST for your MCP server.
2. Layer 2 — Build-Time Strategy Engine: GroupedToolBuilder orchestrates six pure-function strategy modules to generate a single MCP
tool definition. All heavy computation happens at build time. At runtime, execute() does a single Map.get() lookup and calls a pre-
compiled function.
Per-Field Annotation Intelligence (4-Tier System)
The SchemaGenerator analyzes every field across every action directly from Zod isOptional() introspection, cross-referencing them to
produce 4 annotation tiers automatically:
Tier Condition Generated Annotation LLM Reads As
Field is in commonSchema and
Always Required (always required) "I must always send this field"
required
Required-For Required in every action that uses it Required for: create, update "I need this for specific actions"
Required + Required in some, optional in Required for: create. For: "Required for create, optional for
Optional others update update"
For Optional in all actions that use it For: list, search "Only relevant for these actions"
Zod Parameter Stripping (Built-In Security Layer)
When the LLM sends arguments, execute() merges commonSchema + action.schema using Zod's .merge().strip(), then runs
safeParse().
1. Unknown/injected fields are silently stripped.
2. Type coercion happens safely through Zod.
3. The handler receives exactly the shape it declared. The LLM cannot inject parameters that your schema does not declare. This is a
security boundary, not just validation.
Hierarchical Grouping for Large API Surfaces
For massive API surfaces, actions support module.action compound keys. Flat mode (.action()) and hierarchical mode (.group()) are
mutually exclusive on the same builder.
new GroupedToolBuilder<AppContext>('platform')
.tags('core')
.group('users', 'User management', g => {


---
*Page 5*


g.use(requireAdmin) // Group-scoped middleware
.action({ name: 'list', readOnly: true, handler: listUsers })
.action({ name: 'ban', destructive: true, schema: banSchema, handler: banUser });
})
.group('billing', 'Billing operations', g => {
g.action({ name: 'refund', destructive: true, schema: refundSchema, handler: issueRefund });
});
The discriminator enum automatically becomes: users.list | users.ban | billing.refund.
Pre-Compiled Middleware Chains
Middleware follows the next() pattern. But unlike Express.js, chains are compiled at build time. The MiddlewareCompiler wraps handlers
right-to-left into nested closures and stores the result. At runtime, execute() calls this._compiledChain.get(action.key). Zero chain
assembly, zero closure allocation per request. Supports both Global and Group-scoped execution.
TOON Token Optimization (Slash API Costs)
Descriptions and responses can be encoded in TOON (Token-Oriented Object Notation) via @toon-format/toon — a compact pipe-delimited
format that eliminates repeated JSON keys:
builder.toonDescription(); // Token-optimized prompts (saves tokens on tools/list)
return toonSuccess(users); // Slashes token cost on array responses back to LLM
Type-Safe Common Schema Propagation
propagates types through generics. The return type narrows from
commonSchema() GroupedToolBuilder<TContext, Record<string,
to . Every subsequent handler receives —
never>> GroupedToolBuilder<TContext, TSchema["_output"]> TSchema["_output"] & TCommon
checked at compile time, not runtime. No , no type assertions needed.
as any
Duck-Typed Server Resolution
accepts and performs runtime duck-type detection:
attachToServer() unknown
1. Has .server.setRequestHandler ? → McpServer (high-level SDK).
2. Has .setRequestHandler directly? → Server (low-level SDK). Zero peer dependency coupling to MCP server internals. If the SDK
restructures its exports, this framework does not break. Returns a for clean teardown testing.
DetachFn
Conservative Annotation Aggregation
MCP tool annotations operate at the tool level, but actions have individual behavioral properties. The framework resolves this safely:
if any action is destructive (worst case assumption).
destructiveHint: true
only if all actions are read-only.
readOnlyHint: true
only if all actions are idempotent. (Also supports and via manual overrides).
idempotentHint: true openWorldHint returnDirect
⚠ DESTRUCTIVE Warnings & Error Handling
Safety Signal: When an action is marked destructive: true, the DescriptionGenerator appends a literal ⚠ DESTRUCTIVE warning.
LLMs trained on safety data recognize this and request user confirmation.
Error Isolation: Every error includes the [toolName/action] prefix for instant LLM self-correction (e.g., Error: action is required.
Available: list, create, delete).
Freeze-After-Build Immutability
Once buildToolDefinition() is called, the builder is permanently frozen. The _actions array is sealed with Object.freeze(). All mutation
methods throw. This eliminates an entire class of bugs where tools are accidentally mutated after registration — adopting the same pattern
Protocol Buffers uses.
Introspection API
Need programmatic documentation, compliance audits, or dashboard generation?


---
*Page 6*


const meta = builder.getActionMetadata();
// Returns: [{ key, actionName, groupName, description, destructive, readOnly, requiredFields, hasMiddleware }]
🔬 Architecture & Internals
Project Structure
The codebase is organized into bounded contexts with shallow nesting (max 2 levels):
src/
├── domain/ → Pure immutable domain models
├── converters/ → Domain-to-DTO converters
├── framework/
│ ├── types.ts → ALL contracts & shared types (single file)
│ ├── result.ts → Result<T> monad (cross-cutting)
│ ├── response.ts → Response helpers (cross-cutting)
│ ├── builder/ → GroupedToolBuilder, ActionGroupBuilder, Compiler
│ ├── execution/ → ExecutionPipeline, MiddlewareCompiler
│ ├── schema/ → Schema, Description, Annotation strategies
│ ├── registry/ → ToolRegistry, ToolFilterEngine
│ └── server/ → ServerResolver, ServerAttachment
└── index.ts → Public API barrel
Domain Model Layer (src/domain/)
The package provides a full domain model for MCP primitives:
Class Purpose
Group Tree node with parent/child relationships, configurable name separator, recursive FQN
Tool Leaf node with input/output schemas and ToolAnnotations
Prompt Leaf node with PromptArgument list
Resource Leaf node with URI, size, mimeType, and Annotations (audience, priority)
BaseModel Name, title, description, meta, icons
GroupItem Multi-parent group support, root traversal
Features Bidirectional converters (ToolConverterBase, GroupConverterBase, etc.) with null filtering for clean conversion to external
representations.
Strategy Modules
Six pure-function modules organized by bounded context. Every module is independently testable and replaceable. Zero shared state.
Context Module Responsibility
schema/ SchemaGenerator 4-tier per-field annotations from Zod schemas
schema/ DescriptionGenerator 3-layer descriptions with ⚠ DESTRUCTIVE warnings
schema/ ToonDescriptionGenerator TOON-encoded descriptions via @toon-format/toon
schema/ AnnotationAggregator Conservative behavioral hint aggregation
execution/ MiddlewareCompiler Right-to-left closure composition at build time
schema/ SchemaUtils Zod field extraction + build-time schema collision detection


---
*Page 7*


🛠 Key Capabilities Matrix
Capability What It Solves
Action Consolidation Reduces tool count, improves LLM routing accuracy
Hierarchical Groups Namespace 5,000+ actions with module.action compound keys
4-Tier Field Annotations LLM knows exactly which fields to send per action
Zod .merge().strip() Type-safe schema composition + unknown field stripping
Common Schema Propagation Shared fields with compile-time generic inference
Pre-Compiled Middleware Auth, rate limiting, audit — zero runtime chain assembly
Group-Scoped Middleware Different middleware per namespace (e.g., admin-only for users)
TOON Encoding Token reduction on descriptions and responses
Conservative Annotations Safe MCP behavioral hints from per-action properties
⚠ DESTRUCTIVE Warnings Safety signal in LLM tool descriptions
Tag Filtering Include/exclude tags for selective tool exposure
Introspection API Runtime metadata for compliance, dashboards, audit trails
Freeze-After-Build Object.freeze() prevents mutation bugs after registration
Error Isolation [tool/action] prefixed errors for instant debugging
Duck-Typed Server Works with Server and McpServer — zero import coupling
Detach Function Clean teardown for testing via DetachFn
Domain Model Hierarchical tree with multi-parent, FQN, converters
Auto-Build on Execute execute() triggers buildToolDefinition() if not called
Schema Collision Detection Build-time error when field types conflict across actions
📚 Official Guides
Ready to build production agents? Dive into the documentation:
Guide What You Will Learn
🏁 Getting Started First tool, context, common schema, groups, TOON — complete examples.
🏗 Architecture Domain model mapping, Strategy pattern, build-time engine, execution flow.
📈 Scaling Guide How tag filtering, TOON, and unification prevent hallucination at 5,000+ endpoints.
🛡 Middleware Global, group-scoped, pre-compilation, real patterns (auth, rate-limit, audit).
🔍 Introspection Runtime metadata extraction for Enterprise compliance.
📖 API Reference Comprehensive typings, methods, and class structures.
Requirements
Node.js 18+
TypeScript 5.7+
@modelcontextprotocol/sdk ^1.12.1 (peer dependency)


---
*Page 8*


README More
Releases 7
v0.7.0 — DX Excellence + Architecture Refactoring Latest
1 hour ago
+ 6 releases
Packages
No packages published
Languages
TypeScript99.5% JavaScript0.5%