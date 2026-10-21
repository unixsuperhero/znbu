

# Non-negotiable Features

## Search, Filter, Sort, and Grouping

- There are various arbitrary concepts that matomeru tracks inventory of, and it
  potentially grows daily.

- any data point with a finite list of possible values, but can grow (tags,
concept types, statuses, etc.) all of these should be filterable.  Form fields for
creating, editing or updating, should always implicitly make new ones if any
values entered don't match pre-existing values.

- each list should be groupable, scopable to specific groups etc.
- i should be able to type a specific letter and cycle the groups and the
capital version of that letter should open a modal to let me customize it

# cli

- accept 3rd party subcommands named with `mtm-subcmd` or
`<current_bin_name>-<subcommand_name>`
  - these are executable binaries found on the `PATH` environment variable
    list (like `git-foo` for `git foo`), not plugins or config entries
  - built-in subcommands and registered concepts/units win; an external binary
    only runs when the first word is not known to mtm
  - the json explore tui is built into mtm as the `mtm json` subcommand, not a
    3rd party binary

- DO NOT print json by default as output for any subcommand especially help


## subcommands

- json explore/search/filter tui
