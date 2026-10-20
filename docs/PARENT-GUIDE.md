# Parent and caregiver guide

Tarka v3 provides short, prepared maths and reading practice. An adult should try the lessons first and stay available to explain, take a break or stop. It is a prototype, not a substitute for a teacher or a professional assessment.

## Set up together

1. Select **Create account**. Choose a made-up parent username and a password of 15–128 characters. Save the password securely. No email address is needed; each account holds one learner.
2. Confirm that you are an adult parent or caregiver. This declaration does not verify your identity or guardianship.
3. Choose a nickname that does not identify the child. Do not enter a full name, school, address or birth date.
4. Choose the closest broad age band: 6–8, 9–11 or 12–15. Age bands are a starting point, not a judgement of ability.
5. Create a separate six-digit household PIN and keep it private. The PIN opens parent controls within the signed-in learning space; the password signs in to the account.
6. Leave optional AI and voice off initially. Authored hints and the lessons work without them.

An account lets you sign in again after changing devices, clearing cookies or session expiry. Sessions last at most seven days and expire after 24 hours without a server request. Expiry or sign-out does not delete saved account progress. **Account** provides password change, sign-out on this device and sign-out everywhere. Password change signs out other devices while keeping the current device signed in with a fresh session.

There is no self-service password reset, email recovery or MFA in this version. The PIN cannot reset the password. Save the password in a password manager or another private, reliable place. Do not treat this prototype as a permanent school record; ask the operator about backups and retention.

If you already have an older unlinked V3 learner, select **Create account** in that same browser and enter its existing parent PIN to keep the record. Those older profiles remain accessible only for their original 30-day cookie lifetime until claimed. Signing in to a different account switches records and does not merge the unlinked learner. Once the old cookie expires or is lost, there is no self-service claim/import path. Expiry does not erase the old server records; the operator must manage them.

## During practice

The child chooses from prepared answers. If they are unsure, they can request an authored hint, try again or ask you for help. After practice, a different transfer question checks whether they can apply the idea again.

An independent result requires a correct first attempt without hints, transfer narration or whiteboard support for that new question. Assisted completion is still useful practice. Neither a quiz result nor an age band measures the child's general intelligence or worth.

Practice sessions default to fifteen minutes; parent settings also offer ten or twenty minutes. At the selected limit, the app requires a sixty-second break before continuing. You can stop earlier or take a longer break. This timing is a prototype design choice, not a recommended amount of daily screen time.

## What optional AI does

If you opt in and the operator has configured and funded Nebius access, an NVIDIA model can choose between allowed hints that were authored for the question. The app displays the prepared hint text, not newly generated teaching prose.

The app is not an open-ended chatbot. Children cannot type a conversation, upload material or ask it to search the web. It should not claim to be a friend, trusted adult or perfect teacher. Encourage the child to question explanations and ask you when something seems wrong.

Relevant structured learning context may be sent to Nebius only when the AI selection feature is enabled. The provider context is limited to the coarse age band, authored question/hint choices and necessary answer/assistance information. Account usernames/passwords, nicknames, household PINs, browser credentials and drawings are excluded. See [the data-flow checklist](SAFETY-AND-PRIVACY.md); real provider behavior and retention still need checking before a child study or public release.

## Parent controls

- **AI opt-in:** turn optional hint selection on or off. Turning it off should stop subsequent AI requests; previously sent data is not recalled from a provider.
- **Export:** download the learning record associated with this account or unlinked profile. Keep the file private; exported copies are outside the app's deletion controls.
- **Delete account and learner:** for a linked account, the deletion removes the parent account, all its sessions, learner profile and learning history. It requires the parent PIN authorization, current account password and explicit confirmation. An unlinked profile uses its PIN authorization and confirmation. Read the confirmation carefully; this cannot be undone. Operator billing reservations remain so deletion cannot reset spending limits.

Deleting work does not automatically erase backups, access logs or any data already held by a provider. The deployment operator must describe and manage those separately.

## Before involving other children

Have an educator independently review the lesson wording, answer keys, hints and difficulty. Obtain the appropriate adult permissions and the child's willing agreement for the specific setting. A six-digit PIN and an acknowledgement checkbox are not proof that those requirements have been met.

Report confusing, inaccurate or inappropriate lesson content to the project team through the adult running the trial. Stop a lesson if it causes distress. The prototype has no clinical assessment, safeguarding-response service or emergency-contact workflow.

## Listening to a lesson

Device voice starts off and is separate from optional AI. An adult may enable it during setup or in parent settings. Choose a voice and comfortable pace together. Listening starts only when a button is pressed; use Pause, Resume or Stop at any time. Changing question, leaving the lesson, opening parent controls or taking a break stops playback. A transcript stays visible during listening, and the ordinary text works without audio.

Only installed English voices identified as local by the browser are offered. If none are available, continue with text and check the device's speech settings. No microphone permission is needed. This is device speech, not an NVIDIA voice. Quality and pronunciation of maths symbols should be reviewed on the intended device.

Listening to the transfer question counts as support in the progress record, even if playback fails. This is deliberately conservative. Speech is an accessibility aid, and a supported result is useful practice rather than a poor score. Narration counts in the parent view are requested readings, not listening time or attention measurements.

## Learning on the maths board

Open the optional whiteboard in a maths lesson to see the worked example one step at a time. The fifteen maths lessons have forty-five authored example steps in total. The board can also show a hint that has already been requested, or feedback after an answer is checked. During a new transfer question, earlier worked examples stay closed so help cannot silently count as independent work.

The drawing space is for the learner's own marks: draw, erase, undo or clear. Drawings stay in browser memory and are not saved, uploaded, graded or interpreted by AI. Leaving the board or reloading can clear them. Ordinary text and diagrams remain usable without drawing.

The teaching steps are prepared lesson content. Optional NVIDIA help can choose an approved hint; the board does not generate new open-ended explanations or make an additional paid call. Board support requests have their own count in the parent record, separate from read-aloud. Requesting support before answering a transfer question means it is recorded as supported practice, even if the board later fails to display.

See [accounts and whiteboard details](ACCOUNTS-AND-WHITEBOARD.md) and [current verification status](../STATUS.md) for what has actually been checked.
