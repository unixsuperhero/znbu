
# Goal

I want all tasks/subtasks, and the noise that action items are extracted
from to be funneled into a single app so that they can be managed and reviewed from one
central system.

I want to treat getting things done as the central mode.
The mode is always...now.  Not later, or what's next.

# User Stories

## I wants

- a tui
- possibly a terminal multiplexer...but maybe we don't need it, since we're
mostly worried about just kicking off cmds or agents/prompts and capturing
inputs/outputs...we might not need a full multiplexer, but if we should...just
because we can and shouldn't restrict ourselves. then it should be based on
herdr or tuios, but ideally i think i want to use the go based one that uses
charm.

- the webui, if there is one, to function **EXACTLY** like the tui, but be easier on the eyes
- to see things from different levels of abstraction, but only one at a time, and not mix them...only rare exceptions
- i want all actions a user can make to be gated by, and associated with, a task or subtask.
- should i introduce the concept of a project as a way to group tasks?
- i want a generic selector, that can search any/all collections
- i want items in collecions or associations to be a type and metadata.
- i want it to be keyboard driven and modal, like vim
- When i think about a system for getting things done, i've focused too much on being flexible.  because of that, 
- if it is sitting idle past a threshold, it sends a notification, or gets my attention to redirect me.
- for the greater software industry,
  - I want to build the abstraciton layer of Human Time, Effort, Attention, and Context (things i need or want)
  - i want to build the system that owns and defines the shape of these abstractions and how they work.
- i want to track everything, one way to track things is a raw event log
- different types of tasks: - to know - to do/to finish
- entire app's theme is based on the task's theme.  this is the main mode: the task.
- all actions are managed by the app, which lets us gate on infinitives
- i want to be encouraged to write and document
- i don't want to live in a world that has restrictions and gates on when or why
someone does anything.  thinking that there's a right time and a wrong time to
write code is a bad system.  i don't want tasks or gates to be based on when or
why

## ambitions

- SEPARATE: I want to build the system that treats task as a mode.
- SEPARATE: i want to build systems
- SEPARATE: I want to enjoy building things.
- SEPARATE: I don't want it to be a compulsion, or a need driven by external forces , or something that drags me around.  Take ownership.

## it looks like

After picking a task...if idle for more than 3min, the task is reset/unset.  if
working for more than 15min with 0 one-minute breaks, reset the task, this
gives me the opportunity to change tasks and get something else done.  but when
picking a task, the goal is to complete one task, or subtask iem.

 no task is off the table. because... getting tasks done is our main mode. so when we're cranking things out, nothing's off the table. i shouldn't have to worry about, you know, should there be something, is there a higher priority item that i should be working on right now?

instead of thinking about what i should be doing, thinking about what i should be creating or returning, right? just, like, software, and how to design that. stop thinking about what you wanna do, and start thinking about the thing you wanna produce, or finish, or check off a list.

## prompt

if you had to build an app like this, what would it look like? how would it facilitate the goal of just completing tasks, no matter how small they are as quickly as possible, and changing often, but changing often because we're finishing things, not because we're spending too much time on it?

so that's the goal. is to check as many small things off... as possible within a
day. check all things off. i don't want anyone to even be able to think that i
should have worked on something different, or even think that they should for a
second ell me what or how i work on something to be unthinkabvle because i just
get so much done.


## i want...

to be able to kick off like a "learn about x for y" prompts that are considered
throw away and the result is a list of motivation to work on something later.
that i'm strictly not allowed to work on until later.  these things are the
things i don't **need** now, but are nice to haves.



## important concepts and modes

- Git
  - Repo
  - Workgree
  - Branch
  - Remote
- Github
  - Ownwe
  - Repo
  - PR
  - CI
- Terminal Multiplexers
  - Session
  - Workspace
  - Pane
  - Tab
- Tasks
  - Task
  - Subtask
- Context
- Shell
  - Bin
  - Path
  - Dir
  - File
  - Command
    - ExitStats
    - STDIN/OUT/ERR
- AI
  - Provider
  - Model
  - Agent
  - Session
  - Turn
    - Prompt
    - Response
