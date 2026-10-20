since we monitor output:
- my prompts
- agent responses
- shell commands (stdin) - stdout/sderrr


matchers find a match coming from a source stream or source event

then "initializess i" - attaches metadata 

enum Source
  UserAction action
enum UserAction 
  NewTerminal
  NewPrompt
  NewTerminal
enum ContextMatcher
enum Context
  ContextMatcher matcher

