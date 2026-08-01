/**
 * userProgress — mock learner state for the Neural Pathway Progress Tree.
 *
 * Drives the entire <NeuralProgressTree> sidebar: which courses exist, the
 * modules branching off each, completion status, and which node the learner is
 * currently on ("You are here"). Swap this object for a live API payload of the
 * same shape and the component re-renders unchanged.
 *
 * Shape
 *   user            string   — display name in the panel header
 *   currentNodeId   string   — id of the active node (course OR module); pulses
 *   courses[]       Course   — main nodes, top → bottom on the trunk
 *     id            string   — stable id (used by currentNodeId)
 *     code          string   — catalog code shown on hover (see utils/catalog)
 *     title         string
 *     field         string   — neurology · psychEmergency · general
 *     status        string   — 'completed' | 'in-progress' | 'locked'
 *     modules[]     Module   — sub-nodes branching off the course
 *       id          string
 *       title       string
 *       status      string   — same enum as course
 *
 * Status note: the gold fill travels with scroll regardless of status; status
 * styles the node ring/glyph and damps `locked` nodes so they stay subdued even
 * as the fill front passes them.
 */
export const userProgress = {
  user: 'Dr. Elena Vasquez',
  currentNodeId: 'nro-201-m2',
  courses: [
    {
      id: 'nro-101',
      code: 'NRO-101',
      title: 'Foundations of Clinical Neuroanatomy',
      field: 'neurology',
      status: 'completed',
      modules: [
        { id: 'nro-101-m1', title: 'The Neuron & the Synapse', status: 'completed' },
        { id: 'nro-101-m2', title: 'Cortical Organisation', status: 'completed' },
        { id: 'nro-101-m3', title: 'Ascending Sensory Pathways', status: 'completed' },
      ],
    },
    {
      id: 'nro-201',
      code: 'NRO-201',
      title: 'Acute Ischaemic Stroke Protocols',
      field: 'neurology',
      status: 'in-progress',
      modules: [
        { id: 'nro-201-m1', title: 'The Ischaemic Cascade', status: 'completed' },
        // ── currentNodeId points here: the pulsing "You are here" node ──
        { id: 'nro-201-m2', title: 'The Thrombolysis Window', status: 'in-progress' },
        { id: 'nro-201-m3', title: 'Endovascular Triage', status: 'locked' },
      ],
    },
    {
      id: 'psy-204',
      code: 'PSY-204',
      title: 'Psychiatric Emergencies',
      field: 'psychEmergency',
      status: 'locked',
      modules: [
        { id: 'psy-204-m1', title: 'De-escalating Acute Agitation', status: 'locked' },
        { id: 'psy-204-m2', title: 'Structured Suicide-Risk Assessment', status: 'locked' },
      ],
    },
  ],
}

export default userProgress
