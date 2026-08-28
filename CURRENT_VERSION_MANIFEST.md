# Current version material manifest

Snapshot date: 2026-08-28

Manuscript title: **A Statistically Supported DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark**

## Authoritative manuscript materials

| Material | Path | SHA-256 |
|---|---|---|
| LaTeX source | paper/source.tex | a89c0835641198e860d9797c7e657ececc25fe1c9c8760d519b084112cdc367a |
| Bibliography | paper/ref.bib | 7b423bdcc9e0e976c566dfc0e4f160bddfbd82156df254f03760ebef8a279741 |
| Clean PDF | paper/output/pdf/dqn_variants_satellite_ground_manuscript.pdf | 1616899381269e3e363e6c03f4917dfbc6aaa290ddd9f53697c6f9273c1375cf |
| Chinese--English bilingual PDF | paper/output/pdf/dqn_variants_satellite_ground_manuscript_bilingual_zh_en.pdf | 25eec683d8afd44497f679ae25a8ac7540e2d6d632f397e6cf2b09dc0855f2e9 |
| Compile log | paper/output/pdf/dqn_variants_satellite_ground_manuscript.log | 0dc386b2fe0e5bda83b9cc956f5899e1e785edd9a9454c2dea83ae334528c98d |
| Bilingual compile log | paper/output/pdf/dqn_variants_satellite_ground_manuscript_bilingual_zh_en.log | 06b958a71aea96cbf003250bb367988017e607a09b9a47fdbf20be331b1c602e |

The bilingual reader source and traceability material remain under `paper/bilingual`.

## Distribution-ready reproducibility package

Path: `dqn_family_satellite_ground_reproducibility_2026-08-28`

Neutral Python namespace: `dqn_family_satellite_ground`

The package contains:

- current Python experiment, validation, statistical-reporting, and figure-generation scripts;
- the current MATLAB figure-generation script;
- 120 checkpoints for the six reported DQN objectives;
- 20 contextual-bandit checkpoints;
- 40 centered-full-action preview-mismatch checkpoints;
- 180 corresponding training curves;
- all locked CSV/JSON results and validation metadata used by the current manuscript;
- unit tests and pinned direct dependencies;
- exactly one current English manuscript PDF;
- a package README, verifier, manifest, and SHA-256 checksum inventory.

The package deliberately contains no manuscript images, rendered figures, LaTeX source, bilingual-reader source, reviewer files, superseded result sets, or historical iterations. Its Python and MATLAB scripts generate derived outputs only when run.

Package summary:

- 420 files including the manifest and checksum list;
- 180 `.pth` checkpoints;
- 180 training-curve CSV files;
- 0 manuscript image files;
- 0 LaTeX source files;
- package verification passed across 419 checksum-listed files.

| Package metadata | SHA-256 |
|---|---|
| MANIFEST.tsv | e3319b80be340204a0c3645556454e2cb4ebf405b629b53eb31f955d6bf829ea |
| SHA256SUMS.txt | 56702d405121bbe962e9e61cf956fccd86ae94a9b26a65f06caa09f9a14d01bf |

The public repository is available at [https://github.com/noob32123/dqn_family_satellite_ground](https://github.com/noob32123/dqn_family_satellite_ground). The release licence remains an author input; no licence or DOI has been invented.

## Validation completed

- 22/22 unit tests passed.
- Locked-result validation passed for model seeds 800--819.
- The Python family-summary figure script regenerated successfully from packaged data.
- The MATLAB figure script regenerated successfully from packaged data.
- All 180 checkpoint payloads loaded successfully.
- Embedded model identifiers use the current manuscript terminology.
- Trained tensors were checked as exactly unchanged during the metadata-only identifier migration.
- The previous incorrectly scoped reproduction package was deleted after this package passed validation.

## Current review and revision records

Current reviewer and polishing records remain under `paper/review`. They are author-workspace materials and are not part of the reproducibility package.

## Local build support and history

Local build environments under `.tools` and local configuration under `.codex` are not research-package content. Historical iterations remain under `archive`; they are not required to reproduce the current manuscript.

The concise workspace checksum inventory is `CURRENT_VERSION_SHA256SUMS.txt`. The complete distribution-package inventory is inside the package itself.