# CONTEXT.md — SfSpp_preprocessing

Vocabulary for this project's objects and artefacts, so an agent that opens this repo alone uses
the same words as the rest of the workspace. The umbrella `docs/glossary.md` is the cross-project
measurement vocabulary and **outranks anything here**: a word used while telling the conservator a
number belongs there, not here. Created 2026-10-25 on the first settled term, which is what this
repo's `AGENTS.md` asks for — the file is never created empty.

| term | what it means in practice |
|---|---|
| **Bl0**, **Bl1** | The two breakline files written per sherd, numbered **by surface cluster size**: `Breakline_0` ← `Surface_0`, `Breakline_1` ← `Surface_1`. The number does **not** say which wall face it carries — the code applies no interior/exterior test, and on the Juglet the largest cluster lands on different faces for different sherds (`.scratch/juglet-breaklines/issues/02-emit-both-wall-faces.md:133`). On the pot corpus Bl0 is the interior and Bl1 the exterior, and that is a property of those sherds, not of the naming. Check the face before reading an edgeline's score as an interior or exterior result. |
| **Surface_0**, **Surface_1** | The two wall faces of one sherd as the mesh splitter names them, largest first. Presentation order only; the Bl0/Bl1 row is the same limitation. |
