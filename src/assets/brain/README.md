# Home hero brain

`vascular-brain.png` is an artistic composite of the two user-provided references, generated with the built-in image generation tool. Its transparent alpha is preserved. The original references are not required at runtime.

The live flow in `components/LivingBrain.vue` derives a propagation field from the artwork's gold vessel mask, covering fine branches and the cerebellum as well as the main trunk. Artwork, vessel base and flow share the same square frame and 1254 × 1254 coordinate system. The displayed brain is inset 6% on each side. Warm ivory light travels slowly with smooth local intensity changes. `HomeHeroStars.vue` positions the stars across the physical right half of the entire home header, independently of the brain and locale.

## Generation prompt

Use case: compositing.
Asset: transparent anatomical brain artwork for the NeuroTech website hero.
Input 1 IMG_7763.jpeg is the edit target for the single brain silhouette, orientation and cortical folds. Input 2 IMG_7762.jpeg is the supporting vascular image to align and integrate into that same brain.
Create ONE unified brain by artistically registering the angiographic arterial tree of input 2 inside the anatomical brain of input 1. Preserve the recognizable left-facing lateral/slightly three-quarter view, frontal lobe at left, cerebellum lower right and short brainstem. The vessels must belong to the same brain, with one main feeding trunk from the lower center branching organically through the cortex. Intricate curved vascular paths follow the volume of the folds. Avoid two overlapping outlines or duplicated anatomy.
Style: refined anatomical engraving meets sculptural medical illustration. Warm ivory cortical ridges, deep charcoal-blue engraved crevices, elegant muted antique-gold arterial branches embedded into the surface. Vessel paths should be clear, thin, continuous, visually traceable and unglowing, so moving light can later be animated on the website. Fine subtle stippling only on the anatomy, dimensional soft studio shading. Beautiful and restrained luxury editorial finish.
Composition: isolated single brain centered, occupies 85% of a square canvas with comfortable transparent margins, entire brain visible including cerebellum and short stem. Match reference proportions closely, avoid a generic symmetrical front-view brain.
Remove the yellow circles, paper background, skull, face, neck, all text and all background texture. True transparent alpha background, no checkerboard baked in, no background glow or frame, no labels. Do not include any additional objects.


