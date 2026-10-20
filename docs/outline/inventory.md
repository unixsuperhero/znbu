# Inventory

Status: target, not shipped. Inventory is a first-class conceptual category requested by the user during this consolidation. [B-100](../todo/inventory.md#b-100) owns the open design and implementation acceptance. Existing inventories are useful baselines, not evidence that this broader category exists in the product.

Inventory describes the things that work can refer to and the relationships among those things. The same item can matter in several scenarios. Some children always belong under their parent; other items, especially dirs and files, are useful across scenarios without copies.

## Requested kinds

The groups below help readers find the requested kinds. They are not a final taxonomy, module split, or ownership matrix. Preserve every listed kind, including provider-specific distinctions.

| Reading group | Exact requested kinds |
| --- | --- |
| Documents and references | docs; snippets; links; notes |
| Provider-specific documents and references | pastry docs/links; google docs/sheets |
| Infrastructure and source locations | servers/services; repos; remotes; branches; dirs; files |
| Work and provider-specific work references | PRs; linear tickets; jira tickets; slack threads; todo items; tasks |
| Configuration and AI assets | dotfiles; harnesses; skills; agents; mcp servers; commands |
| Time | date/times (dates, deadlines, reminders, birthdays, ...?) |

`pastry docs/links` retains its named identity. It is not silently renamed to generic docs/links or interpreted as another provider. Likewise, `google docs/sheets`, `linear tickets`, `jira tickets`, and `slack threads` remain distinguishable. A provider-specific item can relate to a general kind without losing its provider identity. These names do not establish a connector or integration.

Todo items and tasks remain separate concepts. Existing [lightweight todos and promotion](work.md#b-13) explain their current distinction; Inventory must not collapse the two. Temporal examples retain dates, deadlines, reminders, and birthdays. The trailing `...?` leaves the time taxonomy open rather than requiring every temporal item to schedule delivery.

## Owned children and shared links

An owned-child relationship means that the child belongs under its parent, rather than being an independent item arbitrarily duplicated under several parents. Some children must always remain nested. Design must identify which kinds and relationships have that rule before extending behavior. The exact per-kind matrix, allowed reparenting, and lifecycle consequences remain open.

A shared-link relationship refers to the same item from several contexts. Linking a dir or file to another scenario does not make a second dir, file, or item identity. Removing one scenario's association is conceptually distinct from deleting the shared item or its underlying resource. This distinction is a target requirement, not a claim about implemented Inventory deletion commands.

Identity distinguishes the item from its label, its placement, and each relationship to it. A similar title alone does not prove two items are the same. Keep parent and provider context where identity depends on them. Existing [Git inventory identity](work.md#gitcatalog) is a concrete baseline: repository identity uses the canonical common Git directory, independent clones stay distinct, and branch identity includes the full ref. Inventory does not replace those identities with a title-only match. Identity rules for other kinds remain design work.

### One directory and file in several scenarios

This JavaScript example illustrates reference reuse only. It is not a proposed database schema, persistence format, command API, or shipped feature. The scenarios are examples, not new required product entities.

```js
const dir = { kind: "dir", path: "/work/shared-library" };
const file = { kind: "file", path: "/work/shared-library/README.md" };

const implementation = { name: "Implement a change", links: [dir, file] };
const review = { name: "Review the change", links: [dir, file] };
const onboarding = { name: "Understand the library", links: [dir, file] };

implementation.links[0] === review.links[0]; // true: the same dir
review.links[1] === onboarding.links[1]; // true: the same file

review.links = review.links.filter(item => item !== file);
implementation.links.includes(file); // true: its link remains
onboarding.links.includes(file); // true: its link remains
```

The file remains inside its real directory while several scenarios refer to it. Filesystem containment and scenario association answer different questions. Shared use does not imply that every parent-child relationship can be shared.

## Existing boundaries to reuse

Inventory is a conceptual category, not a decision to build one giant unit or one unit per kind. These existing boundaries guide design without assigning every requested kind to a new owner:

- [Work, projects, and tasks](work.md) owns work scope and the task tree. [Lightweight todos](work.md#b-13) retain their separate lifecycle and promotion to tasks. The broader [Place target](work.md#places) already considers directories shared across projects.
- [Git and GitHub inventories](work.md#gitcatalog) provide the existing shared repo, remote, branch, and PR baseline. Reuse those records and identity rules rather than introduce a parallel Git inventory. Their implemented subset does not complete B-100.
- [Knowledge](knowledge.md) covers saved [context](knowledge.md#context), [notes](knowledge.md#b-05), [documents](knowledge.md#b-11), files, and editor sessions. Arbitrary-owner notes remain an open extension, not a capability supplied by naming Inventory.
- [Agents and AI assets](agents.md#aiassets) covers harnesses, skills, agents, and the remaining disk/config/plugin catalog. Its partial catalog and [MCP harvest target](agents.md#harvest) do not establish coverage for every Inventory kind or provider.
- [Automation and attention](automation.md) covers action-item behavior, [reminders](automation.md#reminders), and schedules. Matomeru's own [MCP server](automation.md#b-12) is distinct from inventorying external mcp servers. Recording a date, provider reference, or service does not imply polling, delivery, synchronization, or execution.
- [Common verbs and nested palette choices](forms.md#commonverbs) own the shared create/new, edit, and delete vocabulary and verb-first navigation target. Inventory should reuse that contract where an operation applies, not define another palette or promise every verb for every kind.

## Open design decisions

[B-100](../todo/inventory.md#b-100) retains these decisions explicitly:

- The exact ownership matrix, including children that must stay nested, independently reusable items, and relationship lifecycle rules.
- Category-versus-unit placement, including which existing units keep ownership and which concepts, if any, need a different unit boundary. A conceptual category is not necessarily a page or a unit.
- The final taxonomy and identity rules, including overlap among generic kinds, provider-specific kinds, and date/times. The requested kinds above must remain traceable through any grouping.
- Provider integration scope and representation. Listing pastry, Google, PR, Linear, Jira, Slack, or MCP references does not approve authentication, ingestion, synchronization, or a new external integration.

No speculative database schema, ingestion pipeline, retry policy, new page, or external integration is required by this conceptual request. Those are not implied acceptance criteria. This document records the new user request; existing-topic links supply boundaries and current evidence, not proof that Inventory has shipped.
