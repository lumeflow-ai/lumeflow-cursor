# Parameter Summary

The quote stage in [workflow.md](workflow.md) is the single confirmation point. Query price after preparing valid parameters, then show one summary with cost and estimated time.

- Show all user-facing parameters supported by the selected model/mode, including defaults; omit unsupported controls and internal constants.
- Use readable model names and the user's language. Show choices only for parameters the user needs to choose or change, using concrete names/values from the selected model profile. Do not list the entire model catalog by default.
- Preserve the full prompt in the request file. For a long prompt already visible in the conversation, refer to it in the summary instead of reproducing it; show any changes and obtain confirmation.
- Recompute valid options when model, mode, duration or resolution changes. Do not silently replace explicit unsupported selections.

Example (translate to the user's language):

| Parameter | Value |
|---|---|
| Model | Pixverse C1 |
| Prompt | The prompt above, unchanged |
| Ratio | 1:1 |
| Duration | 5s |
| Resolution | 720P |
| Audio | On |
| Outputs | 1 |

Estimated cost: use the API quote. Estimated time: video typically 5–10 minutes, image about 1 minute; describe these as estimates. Ask the user to confirm the displayed parameters and cost or request changes.
