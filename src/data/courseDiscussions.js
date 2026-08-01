/**
 * Course discussion threads — REPLACEABLE DEMO CONTENT.
 *
 * Per-course Q&A shown in the "Discussion" section of each course page. The
 * threads mix realistic resident / student / fellow questions with instructor
 * answers, in the register of a postgraduate neurology programme.
 *
 * `courseDiscussions[i]` corresponds to `academy.courses[i]` (same index/order).
 * Each entry: { role, name, time, body }. `role` drives the small tag shown next
 * to the author (Instructor is accented). This is decoupled from the locale
 * files for the same reason as src/data/courseMedia.js — it is mock educational
 * content meant to be replaced (or, in future, served per-course from an LMS /
 * moderation backend of the same shape).
 */

export const courseDiscussions = [
  // 0 · Clinical Neurology
  [
    { role: 'Resident', name: 'Dr. P. Ahmadi', time: '2 days ago', body: 'How do you approach localizing a lesion clinically, before any imaging?' },
    { role: 'Instructor', name: 'Dr. N. Farahani', time: '2 days ago', body: 'Separate central from peripheral first, then work by level — cortex, subcortex, brainstem, cord, root, nerve, junction, muscle. The pattern of weakness, the reflexes and any sensory level usually narrow it to one or two sites before you order a single test.' },
    { role: 'Medical student', name: 'S. Rahimi', time: '4 days ago', body: 'Which examination findings carry the most localizing value?' },
    { role: 'Instructor', name: 'Dr. N. Farahani', time: '4 days ago', body: 'Reflex asymmetry, a discrete sensory level, and the distribution of weakness are highest-yield. Pronator drift and observed gait are remarkably sensitive screens when time is short.' },
    { role: 'Resident', name: 'Dr. M. Kazemi', time: '1 week ago', body: 'Any practical rule for separating migraine from a secondary headache in clinic?' },
    { role: 'Fellow', name: 'Dr. L. Hosseini', time: '1 week ago', body: 'Run the red-flag screen first — thunderclap onset, new headache over 50, immunosuppression, focal signs or papilloedema. A stereotyped pattern over years with a normal examination is reassuringly primary.' },
    { role: 'Medical student', name: 'A. Tehrani', time: '2 weeks ago', body: 'Could you add a worked case on the first unprovoked seizure?' },
  ],
  // 1 · Neuroscience
  [
    { role: 'Student', name: 'M. Davari', time: '3 days ago', body: 'How does neuroplasticity actually affect learning?' },
    { role: 'Instructor', name: 'Dr. S. Moradi', time: '3 days ago', body: 'Learning is largely synaptic remodelling — long-term potentiation strengthens active synapses while unused connections weaken. Repetition and salience decide which circuits are consolidated, which is why spaced, meaningful practice works.' },
    { role: 'Resident', name: 'Dr. R. Najafi', time: '5 days ago', body: 'Which neurotransmitters are most important clinically?' },
    { role: 'Instructor', name: 'Dr. S. Moradi', time: '5 days ago', body: 'Dopamine, acetylcholine, GABA, glutamate and serotonin between them underlie most of what we prescribe — from antiparkinsonian and anticholinesterase drugs to antiepileptics and antidepressants.' },
    { role: 'Student', name: 'N. Eskandari', time: '1 week ago', body: 'Is the resting membrane potential maintained mainly by the Na/K pump?' },
    { role: 'Fellow', name: 'Dr. H. Bagheri', time: '1 week ago', body: 'The pump establishes the ionic gradients, but the resting potential is set chiefly by the membrane’s resting permeability to potassium. The pump’s direct electrogenic contribution is small.' },
  ],
  // 2 · Neuroimaging
  [
    { role: 'Resident', name: 'Dr. K. Sadeghi', time: '1 day ago', body: 'What imaging sequence is most useful for acute stroke?' },
    { role: 'Instructor', name: 'Dr. A. Karimi', time: '1 day ago', body: 'DWI remains the most sensitive sequence during the hyperacute phase — restricted diffusion appears within minutes, well before changes are visible on CT or conventional MRI.' },
    { role: 'Student', name: 'F. Mousavi', time: '3 days ago', body: 'When should I choose CT over MRI in the emergency department?' },
    { role: 'Instructor', name: 'Dr. A. Karimi', time: '3 days ago', body: 'CT first for suspected acute haemorrhage, trauma, or an unstable patient — it is fast and highly sensitive to fresh blood. Reach for MRI when you need tissue characterisation or posterior-fossa detail.' },
    { role: 'Resident', name: 'Dr. T. Jalali', time: '5 days ago', body: 'Any common pitfall when reading DWI?' },
    { role: 'Fellow', name: 'Dr. Z. Rostami', time: '5 days ago', body: 'T2 shine-through is the classic trap — always confirm true restriction on the ADC map before calling acute ischaemia.' },
  ],
  // 3 · Brain Anatomy
  [
    { role: 'Student', name: 'B. Ghorbani', time: '2 days ago', body: 'Which structures do you find most difficult to identify on cross-section?' },
    { role: 'Instructor', name: 'Dr. R. Tabrizi', time: '2 days ago', body: 'The thalamic nuclei and the brainstem tracts trip up most learners. Fix the major landmarks first, then reason inward — relative position is far more reliable than trying to memorise every nucleus in isolation.' },
    { role: 'Resident', name: 'Dr. S. Amiri', time: '4 days ago', body: 'What anatomy is most relevant clinically, day to day?' },
    { role: 'Instructor', name: 'Dr. R. Tabrizi', time: '4 days ago', body: 'The internal capsule, the brainstem cranial-nerve nuclei, and the arterial territories. Together they account for the majority of localisable deficits you will meet on the ward.' },
    { role: 'Student', name: 'M. Khalili', time: '1 week ago', body: 'Is it worth learning the cerebellar peduncles in detail?' },
    { role: 'Fellow', name: 'Dr. P. Ranjbar', time: '1 week ago', body: 'Yes — knowing which peduncle carries what makes cerebellar and brainstem syndromes much easier to reason through.' },
  ],
  // 4 · Neurocritical Care
  [
    { role: 'Resident', name: 'Dr. A. Shirazi', time: '1 day ago', body: 'What is your first-line strategy for an acute rise in ICP?' },
    { role: 'Instructor', name: 'Dr. L. Hashemi', time: '1 day ago', body: 'Optimise the basics first — head up 30°, neck neutral, normocapnia, adequate sedation and analgesia — then escalate to osmotherapy. Hyperosmolar therapy buys time; it never replaces treating the underlying cause.' },
    { role: 'Fellow', name: 'Dr. N. Yazdani', time: '3 days ago', body: 'Hypertonic saline or mannitol for raised ICP?' },
    { role: 'Instructor', name: 'Dr. L. Hashemi', time: '3 days ago', body: 'Either lowers ICP; let volume status decide. Mannitol if euvolaemic with good renal function; hypertonic saline if hypovolaemic or hyponatraemic. Track the osmolar gap and sodium closely either way.' },
    { role: 'Resident', name: 'Dr. H. Mahmoudi', time: '5 days ago', body: 'What do you find hardest about running the neuro-ICU?' },
    { role: 'Attending', name: 'Dr. F. Sadr', time: '5 days ago', body: 'Balancing competing targets — perfusion against oedema, sedation against preserving the neurological examination. Multimodal monitoring helps, but clinical judgement still makes the call.' },
  ],
  // 5 · Neurosurgery
  [
    { role: 'Resident', name: 'Dr. O. Mirzaei', time: '2 days ago', body: 'What is the real role of neuronavigation in routine cases?' },
    { role: 'Instructor', name: 'Dr. M. Saadat', time: '2 days ago', body: 'It is most valuable for planning the trajectory and craniotomy, and for deep or small lesions. Stay aware of brain shift after the dura is opened — re-orient to fixed landmarks and do not trust it blindly late in the case.' },
    { role: 'Student', name: 'D. Akbari', time: '4 days ago', body: 'What goes into surgical planning before a tumour resection?' },
    { role: 'Instructor', name: 'Dr. M. Saadat', time: '4 days ago', body: 'Define the lesion and its relationship to eloquent cortex and vessels on MRI, choose the approach and positioning, and settle the adjuncts — navigation, monitoring, awake mapping — before the patient is anaesthetised.' },
    { role: 'Fellow', name: 'Dr. S. Lotfi', time: '1 week ago', body: 'When do you add intra-operative neuromonitoring?' },
    { role: 'Instructor', name: 'Dr. M. Saadat', time: '1 week ago', body: 'Whenever the approach puts motor, brainstem or cranial-nerve pathways at risk. The trend across the case is more informative than any single reading.' },
  ],
]

/** Discussion thread for the course at `index` (empty array if out of range). */
export const courseDiscussionsAt = (index) => courseDiscussions[index] || []

export default courseDiscussions
