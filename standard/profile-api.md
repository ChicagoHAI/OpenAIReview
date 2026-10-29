# Hosted API profile

This profile is for closed systems the benchmark cannot run itself. The system exposes an HTTP endpoint. The benchmark submits each paper, polls until the review is ready, and reads the result.

A review takes minutes, so this is a job-style API. Submit returns immediately with an id, and the result is fetched by polling.

## Endpoints

### Submit a review

```
POST /v1/reviews
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "paper": { "text": "<full paper text>" },
  "options": { }
}
```

Response:

```json
{ "session_id": "abc123", "status": "queued" }
```

- `paper` carries the paper. Supporting `{"text": "..."}` is the minimum. A system may also accept `{"url": "..."}` or a multipart file upload, and the benchmark sends whichever the system declares.
- `options` is an open object for any parameters the system exposes (review mode, depth). It can be omitted when there are none.
- `status` is the job state (see below).

### Fetch a review

```
GET /v1/reviews/{session_id}
Authorization: Bearer <api-key>
```

Response while running:

```json
{ "session_id": "abc123", "status": "running" }
```

Response when done:

```json
{
  "session_id": "abc123",
  "status": "completed",
  "result": {
    "standard_version": "1.0",
    "comments": [
      { "quote": "...", "explanation": "..." }
    ]
  }
}
```

The `result` object is a payload in the [Anchored Review Format](README.md). Returning the standard field names (`quote`, `explanation`) is what lets the benchmark call the API with no per-system adapter. 

## Status values


| Status      | Meaning                                   |
| ----------- | ----------------------------------------- |
| `queued`    | Accepted, not started.                    |
| `running`   | In progress. Keep polling.                |
| `completed` | Done. `result` holds the payload.         |
| `failed`    | Terminal error. Include an `error` field. |


Any other terminal-sounding value is treated as done or failed on a best-effort basis, but the four above keep the interaction unambiguous.

## Authentication

The example uses a bearer token. When an API uses a different header (for example `x-api-key`), the system declares the header name and the benchmark sets it. One scheme per system is sufficient.

## Reference client

`[reference/review_client.py](reference/review_client.py)` is a standalone client for this profile. It submits a paper, polls until the job is terminal, and returns the validated payload. It uses only the Python standard library, so the system's creators can run it against a staging endpoint to check that their output is compatible with the benchmark:

```bash
python reference/review_client.py --base-url https://your-api.example.com --api-key <key> paper.txt
```

It prints the returned payload and the validator's verdict.

## Notes

- Reviews are long-running. The client polls with a default timeout that can be raised for slow systems.
- The benchmark may submit several papers at once. Each `session_id` is independent.

