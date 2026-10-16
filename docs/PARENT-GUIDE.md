# Parent and caregiver guide

Tarka v3 provides short, prepared maths and reading practice. An adult should try the lessons first and stay available to explain, take a break or stop. It is a prototype, not a substitute for a teacher or a professional assessment.

## Set up together

1. Open Tarka and read the adult setup explanation.
2. Choose a nickname that does not identify the child. Do not enter a full name, school, address or birth date.
3. Choose the closest broad age band: 6–8, 9–11 or 12–15. Age bands are a starting point, not a judgement of ability.
4. Create a six-digit household PIN and keep it private. The PIN protects this browser's parent controls; it does not prove that the person using it is a parent.
5. Leave optional AI off initially. Authored hints and the lessons work without it.

The prototype uses a browser session rather than a recoverable family account. Access expires **30 days after the profile session is created**, even if you keep using it. Clearing cookies or changing devices also loses access. Export useful work before expiry or changing devices. After expiry the app starts a new learning space; there is no recovery or import feature.

Expiry is not deletion. The old server records remain, and the old profile's parent export/delete controls become inaccessible. Ask the deployment operator about their retention/deletion process before using real child data. This limitation must be resolved or explicitly managed for a supervised trial. Do not treat this version as a permanent school record.

## During practice

The child chooses from prepared answers. If they are unsure, they can request an authored hint, try again or ask you for help. After practice, a different transfer question checks whether they can apply the idea again.

An independent result requires the applicable first-attempt, no-hint and no-transfer-narration conditions. Assisted completion is still useful practice. Neither a quiz result nor an age band measures the child's general intelligence or worth.

Practice sessions default to fifteen minutes; parent settings also offer ten or twenty minutes. At the selected limit, the app requires a sixty-second break before continuing. You can stop earlier or take a longer break. This timing is a prototype design choice, not a recommended amount of daily screen time.

## What optional AI does

If you opt in and the operator has configured and funded Nebius access, an NVIDIA model can choose between allowed hints that were authored for the question. The app displays the prepared hint text, not newly generated teaching prose.

The app is not an open-ended chatbot. Children cannot type a conversation, upload material or ask it to search the web. It should not claim to be a friend, trusted adult or perfect teacher. Encourage the child to question explanations and ask you when something seems wrong.

Relevant structured learning context may be sent to Nebius only when the AI selection feature is enabled. The intended provider context is limited to the coarse age band, authored question/hint choices and necessary answer/assistance information. Nicknames, household PINs and browser credentials should not be included. See [the data-flow checklist](SAFETY-AND-PRIVACY.md); real provider behavior and retention still need checking before a child study or public release.

## Parent controls

- **AI opt-in:** turn optional hint selection on or off. Turning it off should stop subsequent AI requests; previously sent data is not recalled from a provider.
- **Export:** download the child work associated with this session. Keep the file private; exported copies are outside the app's deletion controls.
- **Delete child work:** remove the profile/work covered by the delete action. Read the confirmation text before accepting it. Operator billing reservations remain so deletion cannot reset spending limits.

Deleting work does not automatically erase backups, access logs or any data already held by a provider. The deployment operator must describe and manage those separately.

## Before involving other children

Have an educator independently review the lesson wording, answer keys, hints and difficulty. Obtain the appropriate adult permissions and the child's willing agreement for the specific setting. A six-digit PIN and an acknowledgement checkbox are not proof that those requirements have been met.

Report confusing, inaccurate or inappropriate lesson content to the project team through the adult running the trial. Stop a lesson if it causes distress. The prototype has no clinical assessment, safeguarding-response service or emergency-contact workflow.

## Listening to a lesson

Device voice starts off and is separate from optional AI. An adult may enable it during setup or in parent settings. Choose a voice and comfortable pace together. Listening starts only when a button is pressed; use Pause, Resume or Stop at any time. Changing question, leaving the lesson, opening parent controls or taking a break stops playback. A transcript stays visible during listening, and the ordinary text works without audio.

Only installed English voices identified as local by the browser are offered. If none are available, continue with text and check the device's speech settings. No microphone permission is needed. This is device speech, not an NVIDIA voice. Quality and pronunciation of maths symbols should be reviewed on the intended device.

Listening to the transfer question counts as support in the progress record, even if playback fails. This is deliberately conservative. Speech is an accessibility aid, and a supported result is useful practice rather than a poor score. Narration counts in the parent view are requested readings, not listening time or attention measurements.
