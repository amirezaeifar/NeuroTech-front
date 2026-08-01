/**
 * Corporate Documentation & Technical References — approved content.
 *
 * These documents are presented EXACTLY as supplied: document IDs, field names
 * and wording are verbatim and must not be rewritten, summarised or trimmed.
 * Only their visual presentation (cards, detail pages, market-report layout) is
 * defined elsewhere — this module is the single source of truth for the text.
 *
 * Each document carries a flexible `groups` array so its detail page can render
 * any mix of bullet lists (`items`), key/value pairs (`pairs`) or single
 * statements (`text`) while keeping every original field name intact.
 */

export const documentationOverview =
  'This section presents selected technical, operational, and market documentation developed through healthcare technology assessment, infrastructure planning, logistics coordination, and technology integration activities. The documents reflect professional experience in medical technology evaluation, deployment planning, infrastructure readiness assessment, and healthcare market analysis.'

export const documentationDisclaimer =
  'The documentation presented in this section is intended for professional reference purposes and reflects technical assessments, infrastructure evaluations, deployment planning activities, logistics coordination, and healthcare market analysis conducted within the scope of professional engagements and technology-related consulting activities.'

export const documents = [
  {
    id: 'STD-IR-MHD-2025-001',
    docType: 'Technical Infrastructure Assessment Report',
    title: 'Advanced MRI Infrastructure Assessment Program',
    partner: 'Siemens',
    category: 'Medical Imaging Equipment',
    location: 'Mashhad, Iran',
    groups: [
      {
        label: 'Scope of Work',
        kind: 'list',
        items: [
          'Technical specification review',
          'Infrastructure assessment',
          'Installation readiness analysis',
          'Electrical compatibility review',
          'Documentation coordination',
        ],
      },
      {
        label: 'Logistics Profile',
        kind: 'pairs',
        pairs: [
          { k: 'Origin', v: 'Germany' },
          { k: 'Destination', v: 'Mashhad, Iran' },
          { k: 'Transportation Method', v: 'Air Freight + Ground Delivery' },
          { k: 'Estimated Cargo Weight', v: '7,200 kg' },
        ],
      },
      { label: 'Implementation Period', kind: 'text', text: '14 Weeks' },
      {
        label: 'Operational Considerations',
        kind: 'list',
        items: [
          'Import documentation review',
          'Facility preparation',
          'Equipment room requirements',
        ],
      },
      {
        label: 'Outcome',
        kind: 'text',
        text: 'Completion of technical planning and deployment readiness activities.',
      },
    ],
  },
  {
    id: 'STD-IR-MHD-2025-002',
    docType: 'Medical Technology Deployment Documentation',
    title: 'Diagnostic Imaging Technology Deployment Program',
    partner: 'GE Healthcare',
    category: 'Diagnostic Imaging Systems',
    groups: [
      {
        label: 'Project Activities',
        kind: 'list',
        items: [
          'Equipment evaluation',
          'Technical consultation',
          'Documentation analysis',
          'Logistics coordination',
        ],
      },
      {
        label: 'Performance Indicators',
        kind: 'pairs',
        pairs: [
          { k: 'Planning Completion', v: '95%' },
          { k: 'Documentation Readiness', v: '100%' },
          { k: 'Infrastructure Readiness', v: '91%' },
        ],
      },
      { label: 'Duration', kind: 'text', text: '12 Weeks' },
      {
        label: 'Outcome',
        kind: 'text',
        text: 'Successful completion of operational assessment and deployment planning activities.',
      },
    ],
  },
  {
    id: 'STD-IR-MHD-2025-003',
    docType: 'Surgical Technology Evaluation Documentation',
    title: 'Image-Guided Neurosurgery Technology Evaluation',
    partner: 'Brainlab',
    category: 'Surgical Navigation Systems',
    groups: [
      {
        label: 'Scope',
        kind: 'text',
        text: 'Assessment of navigation technologies for advanced neurosurgical environments.',
      },
      {
        label: 'Services Performed',
        kind: 'list',
        items: [
          'Workflow analysis',
          'Operating room evaluation',
          'Integration planning',
          'Technical documentation support',
        ],
      },
      { label: 'Implementation Timeline', kind: 'text', text: '10 Weeks' },
      {
        label: 'Key Considerations',
        kind: 'list',
        items: [
          'System compatibility',
          'Training requirements',
          'Infrastructure limitations',
        ],
      },
      {
        label: 'Outcome',
        kind: 'text',
        text: 'Improved readiness for future technology integration and deployment planning.',
      },
    ],
  },
  {
    id: 'STD-IR-MHD-2025-004',
    docType: 'Research Infrastructure Assessment Documentation',
    title: 'Clinical Research Technology Assessment',
    partner: 'Oxford',
    category: 'Research Technologies',
    region: 'Mashhad Research Centers',
    groups: [
      {
        label: 'Activities',
        kind: 'list',
        items: [
          'Research workflow analysis',
          'Technical assessment',
          'Infrastructure planning',
          'Documentation review',
        ],
      },
      { label: 'Duration', kind: 'text', text: '16 Weeks' },
      {
        label: 'Outcome',
        kind: 'text',
        text: 'Enhanced research infrastructure planning and technology evaluation capabilities.',
      },
    ],
  },
  {
    id: 'STD-IR-MHD-2025-005',
    docType: 'Technology Integration Assessment Documentation',
    title: 'Healthcare Technology Solutions Evaluation',
    partner: 'Verin',
    category: 'Healthcare Technology Solutions',
    groups: [
      {
        label: 'Scope of Work',
        kind: 'list',
        items: [
          'Technical review',
          'Integration planning',
          'Operational assessment',
          'Documentation support',
        ],
      },
      {
        label: 'Outcome',
        kind: 'text',
        text: 'Enhanced technology implementation readiness and operational planning capability.',
      },
    ],
  },
  {
    id: 'STD-IR-MHD-2025-006',
    docType: 'Healthcare Infrastructure Materials Documentation',
    title: 'Healthcare Infrastructure Materials Assessment',
    partner: 'Forbo',
    category: 'Clinical Environment Solutions',
    location: 'Mashhad, Iran',
    groups: [
      {
        label: 'Services Performed',
        kind: 'list',
        items: [
          'Material evaluation',
          'Environmental planning',
          'Facility assessment',
          'Compliance review',
        ],
      },
      {
        label: 'Performance Indicators',
        kind: 'pairs',
        pairs: [
          { k: 'Environmental Performance', v: 'High' },
          { k: 'Maintenance Efficiency', v: 'Excellent' },
          { k: 'Operational Compatibility', v: 'Verified' },
        ],
      },
      {
        label: 'Outcome',
        kind: 'text',
        text: 'Improved healthcare facility planning and infrastructure readiness.',
      },
    ],
  },
]

/**
 * Market Intelligence Documentation — verbatim approved content, rendered with
 * an analytical market-report layout.
 */
export const marketReport = {
  title: 'Medical Technology Procurement Trends – Iran Regional Market',
  reportingPeriod: '2024–2025',
  groups: [
    {
      label: 'Key Market Drivers',
      items: [
        'Growth of neurological services',
        'Expansion of diagnostic facilities',
        'Healthcare infrastructure modernization',
      ],
    },
    {
      label: 'Procurement Priorities',
      items: [
        'Technical support',
        'Regulatory compliance',
        'Lifecycle cost management',
        'Service availability',
      ],
    },
    {
      label: 'Emerging Technologies',
      items: [
        'AI-assisted diagnostics',
        'Surgical navigation systems',
        'Advanced imaging platforms',
        'Integrated healthcare technologies',
      ],
    },
  ],
  marketOutlook:
    'Continued investment in diagnostic technologies, healthcare infrastructure modernization, and advanced clinical systems across regional healthcare markets.',
}

export const documentById = (id) => documents.find((d) => d.id === id)
