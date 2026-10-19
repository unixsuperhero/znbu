# Go source documentation for review

Decision: use free tools before building a documentation browser. Start with pkgsite for browsable API documentation and go doc for private-symbol inspection. Evaluate Golds for richer relationships, but do not make it mandatory without checking the project's Go version. Keep deck docs for the registry's pages, actions and payloads; it does not replace source documentation.

This is a tool-selection decision, not an installed service. No documentation browser was installed or compatibility-tested in this update.

## Review requirements

- Browse modules and packages, including internal packages and command packages.
- Search types, structs, fields, tags, embedded fields, interfaces, methods, functions, constants and variables; include unexported declarations.
- Follow source locations, package dependencies, interface implementations and type usages where the tool supports them. Distinguish inferred relationships from explicit declarations.
- Show comments next to signatures and fields. Missing comments remain visibly undocumented; do not generate authoritative-sounding behavior descriptions from names alone.
- Identify the source revision, Go version and build context. A static snapshot must be labeled; loader/type errors must not yield a deceptively complete report.
- Run locally or on VPS without publishing private source. Bind review servers to loopback, use an SSH tunnel if needed, and never auto-open a browser on the user's desktop during verification.

## Free options

| Tool | Strength | Limitation / fit |
| --- | --- | --- |
| [pkgsite](https://github.com/golang/pkgsite) — BSD-style | Official pkg.go.dev source and local documentation server; familiar package, declaration and source browsing | Baseline browser. Do not assume it supplies a comprehensive private-symbol or implementation/usage graph; validate those requirements separately |
| [go doc](https://pkg.go.dev/cmd/doc) — bundled Go tool | -all -u includes unexported symbols, methods and fields; -src shows declaration source; -cmd includes command-package symbols | Excellent inspection fallback, not a complete architecture explorer. The locally installed Go 1.27.1 also advertises -http for HTML serving; older toolchains may not |
| [Golds](https://github.com/go101/golds) — MIT | Local browser and static HTML; private declarations, promoted selectors, implementation relations, type uses and statistics | Closest feature match for comprehensive structural review. Maintainer warns it is poorly maintained and may crash or omit information with newer Go ASTs; test against this project before adoption |
| [gomarkdoc](https://github.com/princjef/gomarkdoc) — MIT | Generates Markdown for packages, including exported and unexported symbols; templates and a check mode support committed reference docs | Useful for reviewable snapshots, not a complete interactive relationship browser. Generated reference belongs beside, not inside, hand-authored design decisions |

The primary READMEs and Golds/gomarkdoc licenses were read for this comparison; go help doc was run locally. Features above are maintainer-documented capabilities, not verified results on deck. Golds also documents incomplete test-package analysis and re-running after source changes.

## Adoption gate

1. In the implementation repository, exercise the free browser on representative packages: panes.Pane, prompts.QueuedPrompt, a private type, a command package and an interface with implementations. Confirm signatures, fields, comments and source links against actual code.
2. Capture which review requirements each tool meets and any loader errors. Check the project's pinned Go/build settings; do not substitute an older compiler merely to produce a clean-looking report.
3. Use pkgsite plus go doc if that meets the review need. Add Golds only if its extra relationships are correct on the current project. Use gomarkdoc when a committed, diffable reference is wanted.
4. Only if those free options leave confirmed requirements unmet, build the missing view. Reuse go/packages, go/ast and go/types for loading and typed relationships; do not implement another Go parser or infer types from regex. Scope the custom tool to the documented gaps.

Example inspection, from an implementation package directory:

    go doc -all -u
    go doc -src Pane

These are examples, not commands run against deck in this update. Install and server commands must be run through a launcher with finite enforced timeouts. Do not use an unbounded documentation server as a verification step. Anything exceeding 15 minutes requires a stated reason and explicit permission.

## Sources

- [pkgsite README and local server instructions](https://github.com/golang/pkgsite#pkgsite-a-documentation-server)
- [Go doc command reference](https://pkg.go.dev/cmd/doc) and the installed tool's go help doc output
- [Golds capabilities and maintenance warning](https://github.com/go101/golds#readme), [license](https://github.com/go101/golds/blob/master/LICENSE)
- [gomarkdoc documentation and CLI flags](https://github.com/princjef/gomarkdoc#readme), [license](https://github.com/princjef/gomarkdoc/blob/master/LICENSE)

See [the outline](outline.md) for application requirements and [UI state visibility](ui-state-visibility.md) for the state inventory that source reference alone cannot explain.
