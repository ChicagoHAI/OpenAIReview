# Command-line profile

This profile is for systems the benchmark can run itself, such as an open-source repository or a locally installable package. The system provides a command that reviews one paper. The benchmark runs it on each paper and reads the review it writes.

This is the simplest way to connect a system. There is no endpoint to host and no inference cost for the system's authors, since the benchmark supplies the compute.

## The contract

The system provides a single command that:

1. Takes the path to a paper file as input.
2. Writes one review payload, conforming to the [Anchored Review Format](README.md), to a specified path.
3. Exits `0` on success and non-zero on failure.

The benchmark invokes the command once per paper:

```bash
your-review-command <paper-path> --out <output-json-path>
```

- `<paper-path>` is a file the benchmark provides. The system declares which formats it accepts (for example PDF, Markdown, or LaTeX source), and the benchmark sends that format.
- `--out <output-json-path>` is where the command writes the payload.

Any configuration the system needs (model choice, API keys for its own backend, review depth) can come from command-line flags or environment variables.

## Format validation

The system's creators can run this check to see if their output format is compatible with the benchmark.

```bash
python validate.py <output-json-path>
```

## Worked example

The reference system in this repository, `openaireview`, satisfies this profile with:

```bash
openaireview review paper.pdf --out review.json
```

The benchmark runs that command per paper and scores the `review.json` it produces. Another system's command takes its place, with whatever name and flags fit the tool.

## Notes

- The benchmark may run several papers in parallel, so each invocation should be independent and write only to its own `--out` path.
- A nondeterministic run is fine. The benchmark reports the run it observes. If the command exposes a seed, please document it to help us with reproducibility.

