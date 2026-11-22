/* Elbow Muscle Review: the 8 PT 611 elbow muscles (flexors, extensors, pronators, supinators).
   Answers use the wording of the PT 611 "The Elbow" slides (Sullivan) muscle cards (O / I / A / N).
   Every picture is a Blender render of the RIGHT arm from the open Z-Anatomy atlas (CC BY-SA 4.0):
   the muscle in question is orange, the other arm muscles are see-through. Scripts: render/.
   correct = 0-based index into options. */
window.MQ_QUESTIONS = [
  {
    q: "Identify the highlighted muscle.",
    img: "img/brachialis.jpg", cap: "Right arm, anterolateral view · orange muscle lies deep to the see-through biceps",
    alt: "Right arm from the front and side, shoulder on the left; an orange muscle covers the lower half of the front of the humerus and crosses the elbow, deep to the see-through biceps.",
    options: ["Biceps brachii", "Brachialis", "Coracobrachialis", "Brachioradialis"],
    correct: 1
  },
  {
    q: "Which nerve innervates the highlighted muscle?",
    img: "img/br.jpg", cap: "Right forearm, anterolateral view",
    alt: "Right forearm from the front and side, elbow on the left; an orange muscle runs from the lower lateral humerus along the thumb side of the forearm to the end of the radius.",
    options: ["Musculocutaneous C5, 6", "Median C6, 7", "Radial C5, 6", "Ulnar C8, T1"],
    correct: 2
  },
  {
    q: "Where does the highlighted muscle insert?",
    img: "img/biceps.jpg", cap: "Right arm, anterior view",
    alt: "Right arm from the front, shoulder on the left; an orange two-headed muscle runs from the scapula down the front of the arm to below the elbow.",
    options: ["Tuberosity and coronoid process of the ulna", "Tuberosity of the radius and aponeurosis of the biceps brachii", "Styloid process of the radius", "Middle of the lateral surface of the radius"],
    correct: 1
  },
  {
    q: "Identify the highlighted muscle.",
    img: "img/anconeus.jpg", cap: "Right elbow, posterolateral view",
    alt: "Back of the right elbow from the outer side; a small orange triangular muscle runs from the lateral epicondyle to the olecranon and upper ulna.",
    options: ["Anconeus", "Supinator", "Extensor carpi ulnaris", "Medial head of triceps brachii"],
    correct: 0
  },
  {
    q: "What is the action of the highlighted muscle?",
    img: "img/pq.jpg", cap: "Right forearm, anterior view",
    alt: "Front of the right forearm, elbow on the left; a small square orange muscle crosses between the ulna and radius just above the wrist.",
    options: ["Supinate the forearm (radioulnar joints)", "Flex the elbow (humeroulnar joint)", "Pronate the forearm (radioulnar joints)", "Flex the wrist (radiocarpal joint)"],
    correct: 2
  },
  {
    q: "Where does the highlighted muscle originate?",
    img: "img/supinator.jpg", cap: "Right elbow, lateral view · overlying wrist extensors and brachioradialis hidden",
    alt: "Right elbow from the outer side, arm on the left; an orange sheet of muscle wraps the upper radius, running from the lateral epicondyle and upper ulna to the radial shaft.",
    options: ["Common flexor tendon from the medial epicondyle and coronoid process of the ulna", "Lateral epicondyle, radial collateral ligament, annular ligament and supinator crest of the ulna", "Proximal two-thirds of the lateral supracondylar ridge of the humerus", "Distal half of the anterior surface of the humerus"],
    correct: 1
  },
  {
    q: "Identify the highlighted muscle.",
    img: "img/pt.jpg", cap: "Right forearm, anterior view",
    alt: "Front of the right forearm, elbow on the left; an orange muscle runs obliquely from the medial elbow across the forearm to the middle of the radius.",
    options: ["Pronator teres", "Flexor carpi radialis", "Brachioradialis", "Pronator quadratus"],
    correct: 0
  },
  {
    q: "This is one head of the triceps. Which head is it, and what else does it do?",
    img: "img/triceps_long.jpg", cap: "Right arm, posterior view",
    alt: "Back of the right arm, shoulder on the left; an orange head of the triceps starts on the scapula just below the shoulder socket and runs down the back of the arm to the olecranon.",
    options: ["Lateral head: elbow extension only", "Medial head: elbow extension only", "Long head: also extends and adducts the shoulder", "Long head: also flexes the shoulder"],
    correct: 2
  },
  {
    q: "Which nerve supply matches the highlighted muscle?",
    img: "img/brachialis.jpg", cap: "Right arm, anterolateral view",
    alt: "Right arm from the front and side, shoulder on the left; the orange muscle covers the lower half of the front of the humerus, deep to the see-through biceps.",
    options: ["Radial C5, 6", "Median C6, 7", "Ulnar C8, T1", "Musculocutaneous, small branch from radial C5, 6"],
    correct: 3
  },
  {
    q: "Where does the highlighted muscle insert?",
    img: "img/pt.jpg", cap: "Right forearm, anterior view",
    alt: "Front of the right forearm, elbow on the left; the orange muscle runs obliquely from the medial elbow to the middle of the radius.",
    options: ["Middle of the lateral surface of the radius", "Lateral, anterior surface of the distal radius", "Styloid process of the radius", "Anterior, lateral surface of the proximal one-third of the radial shaft"],
    correct: 0
  }
];
