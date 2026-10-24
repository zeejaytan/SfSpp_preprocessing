# 04: Decide each of the 22 unmerged branches: merge, keep as a named rescue, or delete

**What to build:** Every branch on GitHub is either merged, a deliberately kept `rescue/` line with a one-line reason in this ticket, or deleted after its content is shown to be on main or not wanted.

**Answers:** none (workbench routine).

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

Amendment 1.4. On 2026-10-24 GitHub held 22 branches here, 20 of them 90 to 579 commits away from main (`exp-218/220/221`, `pristine*`, `dchain-port`, `merge-237`, `paper-split-chain`, `rescue/sfs-*`, two old `claude/*`). A branch nobody will merge is the git form of a numbered tree. Test ancestry against a freshly fetched canonical checkout (rule 13), never against the branch itself.

- [ ] A table here: branch, commits off main, verdict, reason
- [ ] Deleted branches' tips recorded in the table before deletion
