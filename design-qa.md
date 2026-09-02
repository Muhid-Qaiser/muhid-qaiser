# Design QA

- Source visual truth: `C:\Users\muhid\.codex\generated_images\01a057ad-c5df-72b3-a66f-5d1c155349a5\exec-48d520a8-3845-42b8-96c8-701b7a5f815b.png`
- Browser-rendered implementation: `C:\Users\muhid\AppData\Local\Temp\claude\C--Users-muhid-Downloads-muhid-qaiser\74ea73fb-9c22-4d82-a039-01c1ca74677f\scratchpad\journey-live.png`
- Combined comparison: `C:\Users\muhid\AppData\Local\Temp\claude\C--Users-muhid-Downloads-muhid-qaiser\74ea73fb-9c22-4d82-a039-01c1ca74677f\scratchpad\journey-compare-final.png`
- Viewport: 1200 x 2200 CSS pixels at device scale factor 1
- Source pixels: 926 x 1698, normalized to 1200 x 2200
- Implementation pixels: 1200 x 2200
- State: default dark profile state after live GitHub-stat refresh on 2026-09-02
- Primary interactions: none; the GitHub README surface is a single responsive image
- Console errors: none applicable; the document contains no JavaScript or external runtime requests

## Full-View Comparison

The implementation preserves the selected composition: quiet masthead, one broken shell, six descending mapped disciplines, one luminous route, one bench, an unmapped AI Security Abyss, four ledger figures, one Soul meter, and one hourly activity chart. Relative section heights and the overall vertical reading order match the source. Live values intentionally differ where GitHub data changed after the concept was generated.

## Fidelity Surfaces

- Fonts and typography: embedded Cinzel capitals and Palatino body text reproduce the source hierarchy and remain legible at the native README width. Labels do not wrap or clip.
- Spacing and layout rhythm: the 300/1050/850 section split maintains the source's open masthead, dominant map, and quieter ledger. No content overlaps the route or page edges.
- Colors and visual tokens: matte near-black, bone, blue-grey, and one cyan chart highlight match the selected restrained palette. No broad gradients or glow filters remain.
- Image quality and asset fidelity: the existing repository-native Knight shell geometry is retained. Caverns, route, bench, Abyss, and Soul meter are recreated as crisp vector silhouettes so the profile remains dynamic and lightweight rather than embedding the raster concept image.
- Copy and content: all selected labels are present and correctly spelled. Region counts and ledger figures are generated from `data/stats.json`.

Focused crops were not required: both artifacts were normalized to the same 1200 x 2200 frame in the combined comparison, and all typography and key motifs remained readable at that scale.

## Comparison History

1. Pass 1 found two P2 issues: cavern outlines resembled rounded UI panels, and the Soul meter read as an octagon. The map paths were made more irregular, stalactite cuts were added, the bench silhouette was refined, and the Soul outline was changed to a curved organic form.
2. Pass 2 found two P2 polish issues: map borders were too blue and prominent, and the Soul meter lacked the source's restrained side framing. Borders were darkened and narrowed, the Abyss ceiling was given a rock silhouette, and simple Soul brackets were added.
3. Final comparison found no actionable P0, P1, or P2 mismatch. The flatter rendering is an intentional performance constraint and the live-data differences are expected behavior.

## Verification

- SVG parses successfully as XML.
- Repeated builds are byte-for-byte deterministic.
- Output: 1200 x 2200, 29.2 KB raw, 12.1 KB gzip.
- Rendering primitives: 52 paths, 25 rectangles, and 37 text nodes.
- Runtime cost: zero SVG filters, one animated element, no JavaScript, and no external asset request other than the SVG namespace declaration.

## Follow-Up Polish

- P3: the Stagway marker can be made slightly more recognizable after review without changing the current density.

final result: passed
