# Director Workflow

This product is a control system for AI filmmaking. It does not replace Higgsfield. It prepares better Higgsfield prompts, stores every attempt, records why a shot passed or failed, and uses that history to improve the next prompt.

## What The Fields Do

- Director Instruction: the shot you want, written in normal language.
- Scene: the story context loaded from the database.
- Camera: the lens, angle, movement, aspect ratio, and film look.
- Environment: the stored location, time, weather, architecture, and lighting.
- Lighting: the shot-specific lighting request.
- Emotion: the character performance state.
- Pose: the body/action state for the shot.
- GPT Prompt: the Higgsfield prompt drafted by the OpenAI adapter.
- Claude Prompt: the Higgsfield prompt drafted by the Anthropic adapter.
- Higgsfield Prompt: the prompt selected for copying into Higgsfield.
- Image URL: where the Higgsfield image result is stored.
- Video URL: where the Higgsfield video result is stored.
- Review Reasons: why the generated result failed, such as face drift, costume drift, wrong lighting, or wrong environment.

## How To Use It

1. Add your Film Bible, characters, environments, cameras, props, and scenes.
2. Open Director Workflow.
3. Write the Director Instruction.
4. Select scene, camera, and environment.
5. Click Generate Prompt.
6. Copy the Higgsfield Prompt into Higgsfield.
7. Paste the Higgsfield result image/video URL into the app.
8. Click AI Evaluation to store continuity scores.
9. Click Approved if the shot is correct.
10. Click Rejected if it is wrong, add Review Reasons, and use the improved prompt.

## What Gets Stored

Every workflow stores:

- the original director instruction,
- the database context loaded for the prompt,
- GPT prompt,
- Claude prompt,
- selected Higgsfield prompt,
- uploaded image/video URLs,
- AI evaluation scores,
- approval or rejection status,
- rejection reasons,
- improved GPT and Claude prompts,
- workflow events.

Approved shots are also saved into shot records and visual memory. Rejected shots stay in the database with the rejection reason, so the system can learn what should not be repeated.

## Real GPT And Claude Calls

By default the app uses deterministic local prompt drafts so the product works without API keys.

To enable real model calls, set:

```env
ENABLE_REAL_LLM_CALLS=true
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=your_openai_model
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=your_anthropic_model
```

Keep Higgsfield as the generation tool for now: copy the Higgsfield Prompt manually, generate, then upload the result back into Victory. A direct Higgsfield adapter can be added once you have reliable API access.
