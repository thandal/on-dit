# Working on On dit

The README covers the project's goals, notation, file layout and authoring syntax. Read it first.

## Process

- Work directly on `main`. No feature branches, no pull requests.
- The user reviews the working copy, not commits. After changing anything in `grammaire/`, republish it to the preview artifact before committing:
  - URL: https://claude.ai/artifact/EypYPVNf24W89bMXBW8xH1
  - Publish `grammaire/index.html` with `url` set to the link above, and pass the other pages, `on-dit.css` and `on-dit.js` through `files` under their bare names (`04-present.html`, …). Include any new chapter page.
- Commit and push to `main` once the user is happy with the change.

## Writing

- Keep prose about the grammar itself. No paragraphs explaining the project to itself (what the name means, why it's in English).
- The site has no project status (what's drafted, what's planned). Status lives only in the README.
- Assume no prior French. When a word or example's meaning matters to the point, say what it means, even for common words (nous = "we", pas = "not").
- Follow the notation rules in the README: respell as little as possible, star only what the reading rules can't predict, and show liaison only with ‿.
