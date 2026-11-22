# Elbow Muscle Review

*PT 611 elbow muscles: identify, origin, insertion, action, nerve*

A live, Kahoot-style multiplayer quiz. Students join from their own phones
(no account, no sign-in, no app): open the link or scan the host's QR code, type a name, and answer.

Every picture is a Blender render of the right arm from the open
[Z-Anatomy](https://www.z-anatomy.com/) 3D atlas (CC BY-SA 4.0). The muscle in question is orange;
the other arm muscles are see-through so deep muscles (brachialis, supinator) stay visible.
Answer wording follows the PT 611 "The Elbow" muscle cards.

## The 10 questions

| # | Picture | Asks | Answer |
|---|---------|------|--------|
| 1 | Brachialis | Identify | Brachialis |
| 2 | Brachioradialis | Nerve | Radial C5, 6 |
| 3 | Biceps brachii | Insertion | Tuberosity of the radius and aponeurosis of the biceps brachii |
| 4 | Anconeus | Identify | Anconeus |
| 5 | Pronator quadratus | Action | Pronate the forearm |
| 6 | Supinator | Origin | Lateral epicondyle, RCL, annular ligament and supinator crest of the ulna |
| 7 | Pronator teres | Identify | Pronator teres |
| 8 | Triceps long head | Which head + extra action | Long head: also extends and adducts the shoulder |
| 9 | Brachialis | Nerve | Musculocutaneous, small branch from radial C5, 6 |
| 10 | Pronator teres | Insertion | Middle of the lateral surface of the radius |

Images: `render/eq_shots.py` (Blender 5.2 on Z-Anatomy `Startup.blend`) then `render/post.py img`.
Backend: shared Supabase project (see `config.js`, `schema.sql`).
