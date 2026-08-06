---
name: runbook-writer
description: 'Maintain a clean, step-by-step runbook of exactly what was done to accomplish a task, so it can be followed by hand later with zero surprises. Use whenever the user (or an agent acting for them, e.g. a Hermes agent) carries out a multi-step task — installing software, configuring a server, setting up networking, changing system settings, deploying something, setting up an account or SaaS tool — and wants a record of it. Also trigger on "document this", "write down what you did", "add this to my notes/runbook", "keep a log of the steps", or a reference to an existing project doc to update. Trigger proactively even without the word "document" whenever a task involves configuration, installation, or troubleshooting someone might need to redo by hand later. Not limited to command-line or server work — applies to any step-by-step process worth preserving, technical or not.'
---

# Runbook Writer

## The idea

There are two audiences for this document: the person doing the task right now, and someone (maybe the same person, months later) who wants to redo it by hand from scratch. The second audience is who the final document is written for. They will not see the false starts, the command that errored out, or the config that almost worked. They will only see a sequence they can follow top to bottom and land on the same result. That's the bar for everything below.

This means the document Claude produces is not a transcript or a log of "what happened in order" — it's a distillation of "what someone would need to do, knowing what we now know."

## Workflow

### 1. Find the master document

Documentation for a given project/server/system lives in **one growing document**, organized by topic — not a new file per task and not a chronological journal. Before starting:

- Check whether this conversation, the repo, or the filesystem already has one (common patterns: `*-runbook.md`, `RUNBOOK.md`, `docs/runbook.md`, or whatever the user has referenced before in this project). Read it if it exists.
- If it's genuinely unclear which document this belongs to (new project, ambiguous context), ask the user once for a name/path, then proceed without re-asking for the rest of the session.
- If there's no persistent filesystem in this context (e.g. plain chat with no file access), keep the growing document as an artifact for the session and tell the user explicitly that they'll need to save/merge it into their own copy — don't pretend it's been saved somewhere it hasn't.

### 2. Do the task, keeping a private scratch log

While actually performing the work, informally track every command run, file edited, setting changed, and choice made, along with why. This scratch log is working memory — it is *not* the output, and it does not need to be shown to the user unless they ask.

Include dead ends here too: the command that failed, the config that needed a different value than expected, the approach that got abandoned. You need this raw material in order to do step 3 correctly, but none of it survives into the final document.

Only count a step as part of the working path once you've actually seen it work — ran the command and it succeeded, checked a status, read a config back. A step that seems right but wasn't checked is a guess, not a documented fact, and guesses dressed up as tested steps are exactly the kind of surprise this document exists to prevent.

### 3. When something fails and the approach changes

Don't patch a caveat onto the failed step ("try X, but if that doesn't work, do Y instead"). Cut the failed path entirely. The final section should read as if the working method were known from the start. If a workaround for a real quirk is genuinely necessary (e.g., "must reboot after this step or the interface won't rename"), keep *that* — it's part of the working path, not a failed attempt.

Keep iterating until the task actually works before moving to step 4.

### 4. Distill the scratch log into final steps

Reduce the scratch log to the minimal ordered sequence that reproduces the working result. Each step should be something a human can literally execute by hand:

- A single command to type
- A file to edit, with the exact content to put in it
- A UI path to click through
- A decision to make, with the value to choose

Add a short inline note only when the *why* genuinely isn't obvious from the step itself (e.g. why a reboot is required, why a particular flag matters). Don't narrate the obvious — every extra sentence is something the future reader has to read past.

Where there's any way to check, end the sequence with one: a status command, a smoke test, a value to look for in the output. A step for "how do I know this actually worked" is often the single most useful line in the whole section — without it, the reader finds out something was wrong three steps later with no idea which one.

### 5. When you can't verify a step yourself

Sometimes there's no way to actually run the task — no credentials for the account in question, a UI you don't have access to, or the user is describing something they already did rather than asking you to do it live. In that case, still write the document, but say plainly that it's unverified rather than presenting it with the same confidence as a tested step. A short flagged note at the top of the section is enough (see `references/format-example.md`). Do the best research you can first (check current docs rather than relying purely on memory, since UIs and menus drift), but the honesty about what was and wasn't confirmed matters more than getting every field name exactly right.

### 6. Format and insert into the master document

Follow the conventions below. See `references/format-example.md` for a full worked example. Insert the new material under the matching existing topic/heading, or create a new one if this is new territory — organize by subject, the same way you'd organize a reference manual, not by the date the work happened.

If this task changes something already documented elsewhere in the file (a setting gets tuned, an approach gets replaced), edit that existing section in place rather than adding a second one. A reader should only ever find one answer per topic — if there are two, they won't know which one is current.

### 7. Show the user what changed

Point out the section you added or modified so they can sanity-check it — this matters most the first few times, before they've built trust in the output.

## Formatting conventions

- **Heading hierarchy**: top-level category (`#` or `##`) → sub-area → specific task. Steps live under the most specific heading. A one-line note under a task heading is fine when it clarifies when/why to use that section (e.g. "Best used for SSD storage backing VMs").
- **Steps are numbered lists.** Nest numbered sub-lists for a multi-part step (e.g. step 1 has three sub-steps 1.1–1.3).
- **Single commands go inline** as code: `` `nano /etc/resolv.conf` ``.
- **Multi-line content (file contents, scripts, command blocks) goes in fenced code blocks**, with a language tag when one clearly applies (`bash`, `ini`, etc.) and no tag (or `text`) for generic config/file contents.
- **UI-based steps** (clicking through a web console, an app's settings screen) are written the same way as CLI steps — plain numbered instructions, e.g. "Go to Datacenter > Node > Disks > Wipe Disk" — not forced into a fake command form.
- **Placeholders** for anything that varies by setup use angle brackets: `<Hard-Disk>`, `<Network-Card>`, `<IP-Address>`. Keep the same placeholder name consistent if it's reused across steps in the same task.
- **No narrative filler.** No "First we'll..." or "Great, that worked!" — just the steps, in the voice of an instruction manual.
- **Never write a real secret into the document.** Passwords, API keys, tokens, account numbers — even if the real value was used while doing the task, the document gets a placeholder (`<API-Key>`, `<Bank-Account-Number>`). The runbook may end up pasted somewhere less trusted than the original conversation.
- **Flag anything unverified.** If a section is based on documentation or memory rather than something actually confirmed working (see workflow step 5), open it with a short bolded note, e.g. `**Not verified live — based on Stripe's documented flow; confirm field names against your account.**` Untested and tested steps should never look identical on the page.

## Adapting to the environment

- **Real filesystem access to the actual system being configured** (e.g. an agent working directly on a server, or Claude Code in a repo): read and write the actual master file on disk, so it persists across sessions the same way the configuration itself does.
- **Sandboxed or no persistent filesystem** (e.g. a chat-only context): maintain the document as an artifact for this conversation, and say plainly that the user needs to save it themselves — don't imply it's stored anywhere durable that it isn't.
- **Working environment isn't the real target** (testing in a disposable sandbox before writing docs for a production server, staging vs. live, a container standing in for bare metal): document what's correct for the target, not quirks of wherever the work actually happened. A container without systemd failing to start a service is not a fact about the target server. If it's unclear whether something is a real target-side step or just an artifact of where the work happened to run, say so rather than guessing either way.
- Either way, the formatting rules and the "only the clean working path" rule apply the same.
