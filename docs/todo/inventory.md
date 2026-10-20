# Inventory remaining work

[Inventory concept and existing boundaries](../outline/inventory.md). Inventory is a first-class conceptual category requested during documentation consolidation, not a shipped feature. Existing Git, work, knowledge, agents, and automation behavior does not close this request.

<a id="b-100"></a>
## B-100 Inventory kinds, identity, and interconnected relationships

Status: open, target design and implementation. B-100 owns this request. Priority and size are not assigned.

The user wants interconnected kinds, with some children always nested under their parent and other items useful across scenarios. A directory or file must be reusable through links rather than copied for each scenario. Inventory need not be one giant unit or one unit per kind.

### Kind coverage acceptance

Every exact requested kind must remain identifiable in the design and resulting behavior. The following groups are a coverage checklist, not an approved taxonomy. A generic label does not satisfy a provider-specific kind by erasing that distinction.

- [ ] Cover docs, snippets, links, and notes as identifiable kinds, even when their storage or operations overlap.
- [ ] Cover pastry docs/links without replacing the pastry identity with generic documents or another provider.
- [ ] Cover google docs/sheets without erasing the Google provider distinction or the document/sheet distinction.
- [ ] Cover servers/services, repos, remotes, branches, dirs, and files. Reuse the [existing Git/repo/branch inventory](../outline/work.md#gitcatalog) and [directory baseline](../outline/work.md#rankedpaths) where applicable rather than build competing inventories.
- [ ] Cover PRs, linear tickets, jira tickets, and slack threads with their source/provider identities distinguishable. A generic ticket or URL label alone is not full coverage.
- [ ] Cover dotfiles, harnesses, skills, agents, mcp servers, and commands. Respect the [AI asset catalog boundary](../outline/agents.md#aiassets), [knowledge boundary](../outline/knowledge.md), and [MCP/automation boundary](../outline/automation.md#b-12).
- [ ] Cover date/times (dates, deadlines, reminders, birthdays, ...?). Retain each named temporal example and leave additional temporal kinds open. A recorded date does not inherently become an automated reminder.
- [ ] Cover todo items and tasks separately. Preserve their [existing distinction and promotion relationship](../outline/work.md#b-13) rather than treat them as synonyms.

### Relationship and reuse acceptance

- [ ] Describe which relationships require owned children to remain nested under their parent. Preserve that nesting in the resulting behavior without treating every association as ownership. The exact per-kind ownership matrix is a design decision, not supplied by this checklist.
- [ ] Distinguish an item's identity from its display label and from its links to scenarios. Retain provider or parent context where identity depends on it. Reuse existing Git identity rules; do not equate independent clones or same-named branches across repositories.
- [ ] Demonstrate meaningful reuse of one dir and one file in several scenarios without copies. Each scenario refers to the same item, rather than an independent record that happens to share a path or title. The [illustrative JavaScript example](../outline/inventory.md#one-directory-and-file-in-several-scenarios) explains the intended result without prescribing persistence.
- [ ] Show that removing one shared association leaves the item and its other associations intact. Distinguish unlinking from deleting the underlying resource. Settle owned-child lifecycle rules separately rather than infer them from shared-link behavior.
- [ ] Keep relationships among different requested kinds meaningful without flattening provider identity, filesystem containment, or owned-child nesting into interchangeable labels.
- [ ] Reuse [common verbs and nested palette choices](../outline/forms.md#commonverbs) where applicable. Keep B-33 responsible for that shared interaction contract; B-100 does not require a separate Inventory page or a duplicate command implementation.

### Decisions still open

- Exact ownership matrix and owned-child versus shared-link rules by kind, including lifecycle and reparenting.
- Category-versus-unit placement and the precise division of responsibility among existing work, knowledge, agents, and automation units. Neither one giant unit nor one unit per kind is preselected.
- Final taxonomy, provider-qualified identity, and the representation of temporal examples. Groupings above preserve coverage; they do not settle these choices.
- Provider integration scope. Naming pastry, Google, PRs, Linear, Jira, Slack, or external MCP servers is not approval to add connectors or claim existing access.

Acceptance describes observable kinds and relationships, not a speculative database schema, ingestion or synchronization system, retry policy, new page, or external integration. Those mechanisms are not required by B-100. Resolve design choices explicitly before claiming implementation coverage. No product checks, builds, or application tests ran for this documentation-only addition.
