# Anchored Review Format

This is a small, open standard for the output of an AI paper-review system. If a system adopts this standard, the benchmark can run it directly, with no custom integration code needed.

A review in this standard is a list of comments, where every comment is anchored to a **verbatim quote** from the paper and paired with an **explanation** of the issue. A system connects in one of two ways:

- **Command line** (open systems the benchmark can run): the system provides a command that takes a paper and writes a review. See `[profile-cli.md](profile-cli.md)`.
- **Hosted API** (closed systems the benchmark calls over the network): the system exposes an endpoint the benchmark submits papers to and polls for results. See `[profile-api.md](profile-api.md)`.

Both return the same review payload, described below.

## Payload format

A review payload looks like this:

```json
{
  "standard_version": "1.0",
  "comments": [
    {
      "quote": "we achieve a 51% improvement over the baseline",
      "explanation": "The 51% figure is not supported by Table 3, which reports a 5.1% relative gain. This looks like a misplaced decimal."
    }
  ]
}
```

Two top-level fields are required: `standard_version` and `comments`. Each comment requires `quote` and `explanation`. This is everything the standard requires.

Validate a payload with the bundled checker, which needs only Python:

```bash
python validate.py your_review.json
```

A passing payload prints `✓ VALID` and exits 0.

## Why these two fields

The benchmark seeds known errors into clean papers and measures how many a system catches. To decide whether a comment caught a seeded error, the benchmark does two things:

1. Match the comment's `quote` against the region of the paper that was changed. This match is fuzzy, but it works best when the quote is **exactly from the paper text**.
2. Read the comment's `explanation` and judge whether it identifies the same error that was seeded.

So `quote` should be extracted verbatim from the paper, and `explanation` should say what is wrong and why. Those are the only fields the score depends on.

## Full specification

One payload is one system's review of one paper.

### Top-level fields


| Field              | Required    | Type   | Meaning                                                                                                                                  |
| ------------------ | ----------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `standard_version` | yes         | string | Version of this standard, currently `"1.0"`.                                                                                             |
| `comments`         | yes         | array  | The list of comments. See below.                                                                                                         |
| `standard`         | recommended | string | The constant `"anchored-review"`, so the payload is self-identifying.                                                                    |
| `paper_id`         | recommended | string | An id for the paper, such as an arXiv id or a slug.                                                                                      |
| `system`           | recommended | string | The name of the review system.                                                                                                           |
| `model`            | optional    | string | The underlying model id, if there is one.                                                                                                |
| `overall_feedback` | optional    | string | A high-level assessment of the paper.                                                                                                    |
| `paragraphs`       | optional    | array  | The paper split into paragraphs. Include this only if the comments use `paragraph_index`. Each item is `{"index": int, "text": string}`. |


### Comment fields


| Field             | Required    | Type            | Meaning                                                       |
| ----------------- | ----------- | --------------- | ------------------------------------------------------------- |
| `quote`           | yes         | string          | A span copied from the paper that the comment is about.       |
| `explanation`     | yes         | string          | What is wrong with the quoted span and why.                   |
| `title`           | recommended | string          | A short label for the comment.                                |
| `severity`        | optional    | string          | A free-text tier such as `major`, `moderate`, or `minor`.     |
| `paragraph_index` | optional    | integer or null | A 0-based index into `paragraphs`, if that array is provided. |
| `id`              | optional    | string          | A stable id for the comment.                                  |


Extra fields are preserved and ignored by the benchmark, so a system can carry its own metadata without breaking anything.

## Connecting a system

Each profile matches a different way a system runs. Both deliver the same payload above.

- **Open source, or otherwise runnable by the benchmark:** the [command-line profile](profile-cli.md). The benchmark runs the system locally, so there is no hosting or inference cost for its authors, and this is the simplest to adopt.
- **Closed source:** the [hosted API profile](profile-api.md). The system runs behind an endpoint the benchmark calls. This is the option when the benchmark cannot run the system's code, such as for proprietary systems.

## Examples

- `[examples/minimal.json](examples/minimal.json)`: the smallest valid payload, with only the required fields.
- `[examples/full.json](examples/full.json)`: every field populated, including paragraphs and per-comment metadata.
- `[examples/invalid-missing-quote.json](examples/invalid-missing-quote.json)`: a payload that fails, showing what the validator reports.

## Validating

```bash
python validate.py examples/full.json
```

The checker reports two kinds of findings. **Errors** mean the payload does not conform and will not score. **Warnings** flag recommended fields that were left out, which are fine to ignore. To enforce the recommended fields too, treat warnings as failures:

```bash
python validate.py your_review.json --strict
```

The checker uses only the Python standard library, so any Python 3 install can run it as is.

## Versioning

The `standard_version` field tracks the standard. Version `1.0` is the current release. Additions that keep older payloads valid will bump the minor version (`1.1`, `1.2`). Changes that can break older payloads will bump the major version (`2.0`). A system keeps emitting the version it built against, and its payloads stay readable.

## Questions

This standard grew out of the OpenAIReview project. If a field does not map cleanly onto what a system produces, or a field should be added, open an issue. The standard is meant to stay small, so the bar for new required fields is high, but new optional fields are welcome.