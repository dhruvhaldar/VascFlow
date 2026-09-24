# VascFlow rewrite requirements

Status: proposed implementation baseline. Prepared 2026-09-23 from repository inspection and official library documentation. This document specifies the rewrite; it does not claim that the requirements are implemented or tested.

## Objective and scope

Rebuild VascFlow into a reliable, maintainable scientific workspace for importing vascular meshes, assigning boundary conditions, configuring simulations, exporting solver-compatible input packages, and inspecting results. Choose libraries for scientific fidelity, maintainability, interoperability, and measurable performance.

Target audience: researchers and simulation engineers running a local, single-user application on Windows or Linux. First release: a complete, validated configuration and export workflow. Results inspection follows as a separate milestone. Solver execution, segmentation, mesh generation, and clinical decision support are outside the first release. All planned application features run locally.

The first implementation gate is an explicit solver target: svFSI, svFSIplus, or a particular svMultiPhysics release. The upstream svFSIplus repository currently redirects to svMultiPhysics. Do not assume their input dialects are interchangeable. Record the selected solver version and reference examples before implementing the serializer.

## Current evidence and rewrite implications

| Evidence in repository | Implication |
| --- | --- |
| `frontend/package.json`: Svelte 5, Vite, vtk.js, and Playwright; application source uses JavaScript | Keep the useful foundation and introduce strict TypeScript, explicit domain modules, and focused component tests. |
| `backend/models.py` versus `backend/xml_generator.py`: save frequency, restart step, mesh domain type, additional material properties, and BC variable are not serialized; face ID handling is a placeholder | Every supported setting must affect the correct solver output or be rejected as unsupported. Existing XML snapshots alone cannot establish correctness. |
| `frontend/src/App.svelte` checks density and time step differently from `backend/models.py` | Establish one authoritative validation contract and test equivalent boundary cases on both sides. |
| `backend/mesh_service.py`: candidate boundary arrays include `GlobalElementID`; fallback uses connectivity/default surface; face lists can be truncated | Element identifiers and connectivity components must not silently become validated physical boundaries. |
| Visualization conversion copies selected arrays and may decimate geometry in `backend/mesh_service.py` | Preserve boundary identity explicitly; preview simplification must never modify solver geometry or silently invalidate selection. |
| `frontend/src/stores.js`: configuration and metadata live in writable stores | Add versioned project persistence and explicit invalidation when meshes/configuration change. |
| `backend/main.py`: public uploads mount, process-local rate limiting, extensive custom middleware | Define storage lifetime, file access, and deployment trust boundaries; prefer framework/proxy facilities where suitable. |
| `backend/requirements.txt` has unpinned dependencies; multiple JavaScript lockfile formats exist | Standardize installation and verify a clean checkout on supported platforms. |
| Case-colliding `.Jules/palette.md` and `.jules/palette.md` caused the preceding Git issue | Add case-collision checks to repository validation. |

These are static inspection findings. No runtime benchmark or solver validation was performed for this requirements document.

## Recommended stack

Recommendations are architectural judgments, not a claim that one library is universally best. Lock exact mutually compatible stable versions during the foundation milestone after a Windows/Linux installation and representative mesh smoke test.

| Layer | Recommended library/tool | Reason and selection boundary |
| --- | --- | --- |
| Frontend | Svelte 5 + TypeScript + Vite | Retain the existing framework and rewrite feature modules with strict types. A browser-based scientific workspace does not currently justify introducing an additional server-rendered application layer. [Svelte TypeScript](https://svelte.dev/docs/svelte/typescript). |
| UI primitives | Bits UI with shared CSS tokens | Use reusable accessible dialogs, tabs, and selection controls; keep native controls where sufficient. Application keyboard behavior still requires verification. [Bits UI](https://www.bits-ui.com/docs/introduction). |
| Scientific rendering | `@kitware/vtk.js` | Keep VTK data structures and scientific visualization operations in the browser. Evaluate picking and representative meshes before committing to a rendering pipeline. [VTK.js](https://kitware.github.io/vtk-js/docs/). |
| API and validation | FastAPI + Pydantic | Own domain validation and expose the OpenAPI contract in Python. Add cross-field scientific constraints rather than relying on primitive numeric bounds. [FastAPI](https://fastapi.tiangolo.com/features/). |
| Typed API client | `openapi-typescript` + `openapi-fetch` | Generate TypeScript interfaces from the backend contract and centralize requests/errors. Generated types do not provide runtime validation by themselves. [OpenAPI TypeScript](https://openapi-ts.dev/introduction). |
| Mesh processing | PyVista + VTK + NumPy | Retain scientific mesh operations and array semantics. Prefer PyVista for readable orchestration and direct VTK only for demonstrated needs. [PyVista data model](https://docs.pyvista.org/user-guide/data_model.html). |
| XML export | Python standard-library `xml.etree.ElementTree`, behind a solver-specific adapter | Structured serialization is sufficient initially. Add schema tooling only if the selected solver supplies a usable schema; a well-formed document still needs solver validation. |
| Local persistence | Versioned JSON manifests + filesystem assets; standard-library SQLite for job metadata if needed | Preserve portable project files without requiring a database service. Keep storage on the user's machine. |
| Heavy processing | Bounded local Python worker processes behind a job-service interface | Isolate CPU/native mesh operations from API requests; implement timeout, cancellation, and cleanup. Benchmark process startup and memory. Keep processing on the user's machine. |
| Frontend tests | Vitest + Playwright | Test domain state and real user journeys separately. Run the real backend for end-to-end acceptance. [Vitest](https://vitest.dev/guide/), [Playwright](https://playwright.dev/docs/intro). |
| Python tooling | uv, pytest, Ruff, and a Python type checker | Reproducible Python environment, domain tests, linting, and type checks. Select and pin the type checker in the foundation milestone. [uv](https://docs.astral.sh/uv/). |
| JavaScript tooling | One npm lockfile, `svelte-check`, ESLint, Prettier | Use one package manager and one documented toolchain. Remove competing lockfiles as an explicit migration change. |

Do not introduce React/Next.js, a second rendering engine, Redis, Kubernetes, or a state-management framework merely to refresh the stack. Reconsider them only against a documented requirement and a prototype showing a benefit.

## Requirements sheet

Priority: P0 blocks the first release; P1 is the next planned increment; P2 is a later extension. All items start as **Proposed**. Acceptance criteria describe future checks, not current results.

| ID | Priority | Requirement | Acceptance criteria |
| --- | --- | --- | --- |
| SOL-01 | P0 | Pin a solver dialect and supported capability matrix | Record solver name/version, authoritative examples, supported physics/material/BC combinations, and unsupported combinations. Each supported combination has a reviewed fixture. |
| SOL-02 | P0 | Complete, deterministic configuration export | Every exposed field maps to the selected dialect or produces an actionable unsupported-setting error. Fixtures cover restart, output frequency, materials, variables, and boundary references. Identical inputs produce identical content. |
| SOL-03 | P0 | Verify against the actual solver | Exported representative cases pass the selected solver's parser and an available short smoke run. If no validation-only mode exists, document the minimal execution procedure. Record executable version and results. |
| SOL-04 | P0 | Export a portable case package | Include XML, required mesh/boundary assets, relative references, and a manifest with hashes and solver version. Package works from a different directory; no temporary server path is required. |
| MSH-01 | P0 | Preserve supported imports: VTU, VTP, legacy VTK | Valid fixtures load with expected point/cell counts and bounds. Empty, corrupt, mismatched-extension, and unsupported dataset types receive specific errors. A surface-only input cannot be exported as a valid volume case without required volume assets. |
| MSH-02 | P0 | Establish trustworthy boundary identity | Use explicit supported marker arrays or imported face surfaces. Show marker source; inferred regions require explicit review. Never treat `GlobalElementID` as a boundary by default. Missing/ambiguous markers block BC-dependent export. |
| MSH-03 | P0 | Preserve original geometry and boundary mapping | Hash originals before/after preview processing. Decimated previews retain verified source-face mapping, or use a separate unsimplified selection representation. Tests select known faces and recover their original identifiers. |
| MSH-04 | P0 | Handle large boundary sets without silent loss | Paginate/filter the face list. Any imposed limit is visible and blocks incomplete export; never silently drop boundaries. Test more than 1,000 face identifiers. |
| MSH-05 | P0 | Bound upload and processing resources | Stream with an actual byte limit, validate content, cap decoded size/work and processing time, clean failed uploads, and show retryable errors. Retain the current 50 MiB file limit initially; multipart overhead is a separate documented limit. |
| VIS-01 | P0 | Provide a usable 3D mesh workspace | Rotate, pan, zoom, reset, resize, and recover from unavailable WebGL. Show loading/error states and an accessible metadata alternative. Repeated mesh replacement releases resources. |
| VIS-02 | P0 | Link face selection and BC editing | Selecting a listed face highlights the same face in 3D and vice versa. Labels remain stable after sorting, renaming, and reload. Provide a keyboard-operable face list. |
| CFG-01 | P0 | Use explicit units and validated physics | Show the selected unit system and units for every physical input. Reject nonfinite numbers, invalid signs, and incompatible material/physics/BC combinations. Verify any conversions with reference cases; do not assume inherited defaults are universal. |
| CFG-02 | P0 | Centralize validation semantics | Backend domain models own constraints; frontend presents matching errors with field paths. Shared valid/invalid fixture cases agree across layers, including zero, negative, blank, and boundary values. |
| CFG-03 | P0 | Create, edit, and remove boundary conditions | Associate BCs with stable mesh/face IDs and selected solver semantics. Validate conflicts and required coverage; do not assume every physics permits only one condition per face. |
| CFG-04 | P0 | Prevent stale configuration and exports | Mesh replacement invalidates affected assignments; configuration changes mark generated output stale. Old async responses cannot replace newer state. Export requires current validation. |
| PRJ-01 | P0 | Save, reopen, and transfer a project | Versioned manifest preserves settings, mesh hashes, boundary mappings, and solver target. Round-trip fixture projects compare equal semantically. Missing assets trigger relinking; unknown schema versions are rejected safely. |
| PRJ-02 | P0 | Protect work from interruptions | Atomic saves preserve the last valid project after an interrupted write. Show saved/unsaved status and recovery information; destructive project changes require an appropriate confirmation or undo path. |
| API-01 | P0 | Define a typed, versioned API | Typed request/response/error schemas cover every route. Generate the frontend client in CI and fail on uncommitted contract drift. Centralize base URL, timeout, cancellation, and error translation. |
| JOB-01 | P0 | Make mesh work observable and cancellable | Jobs expose queued/running/succeeded/failed/cancelled status, meaningful stages, and bounded resource use. Cancelling terminates or safely abandons work and removes partial outputs. No fabricated percentage progress. |
| SEC-01 | P0 | Restrict file access and unsafe paths | Server-generated asset IDs resolve within a configured project root. Traversal, symlink escape, and cross-project access tests fail safely. Bind the local API to loopback only. |
| SEC-02 | P0 | Define storage retention and deployment controls | Active saved assets survive cleanup; abandoned uploads expire. Document CORS, trusted proxies, upload limits, and disk quotas. Test configured origin rejection and actual body limits. Rate limits must match the chosen worker topology. |
| UX-01 | P0 | Build a consistent scientific workflow | Project, mesh, physics, BCs, validation, and export states are clearly visible. Errors identify the failing field/face and recovery action. Dense forms remain usable at 1280×720 and 200% zoom. |
| UX-02 | P0 | Preserve keyboard and assistive access | Keyboard-only completion of configuration/export succeeds. Verify visible focus, dialog focus return, error descriptions, status announcements, and shortcut exclusion in text/select controls. Automated checks plus manual review cover key screens. |
| PERF-01 | P0 | Establish and meet performance budgets | On a recorded reference machine, target p95 ordinary form feedback below 100 ms and median orbit rendering at least 30 FPS on a 100k-triangle preview. Measure 1/10/50 MiB import fixtures over at least 20 runs; choose processing timeout budgets from this baseline before release. |
| PERF-02 | P0 | Prevent resource accumulation | After warm-up, 20 upload/replace cycles show no monotonic retained viewer-memory growth beyond a documented tolerance. Bound worker concurrency; verify cancellation and API responsiveness during a large import. |
| QA-01 | P0 | Provide meaningful regression coverage | CI runs type checks, lint, unit/API tests, production build, actual-backend end-to-end tests, and solver fixtures. Cover malformed files, sparse/negative/noninteger marker arrays, stale requests, persistence failures, and unsupported settings. |
| DX-01 | P0 | Make clean installations reproducible | Document pinned runtime versions and single-command setup/test entry points. Frozen installs and core smoke tests pass on Windows and Linux. Fail CI on case-colliding tracked paths and unintended generated/backup artifacts. |
| OPS-01 | P0 | Make failures diagnosable | Structured logs include request/job ID, processing stage, duration, and error category. UI errors reference a support ID. Health/readiness checks distinguish a running API from unavailable processing/storage. Avoid logging mesh contents. |
| RES-01 | P1 | Inspect imported simulation results | Load agreed VTK result fixtures and select scalar/vector components, point/cell association, and time step. Show units/range and missing-array errors. Values at known points agree with source fixtures within documented tolerance. |
| RES-02 | P1 | Add scientific inspection tools | Clipping/slicing, probes, time controls, and image export preserve displayed time, field, units, and color range. Verify probe/interpolation behavior against reference data. |
| PRJ-03 | P1 | Add reusable presets and undo/redo | Named validated presets and configuration undo/redo survive ordinary workflow changes without restoring incompatible mesh assignments. |
| RUN-01 | P2 | Integrate local solver execution | Separate design must define local executable management, resource limits, job cancellation, logs, and restart behavior on the user's machine. Requires SOL-01 through SOL-04 before implementation. |

## Architecture requirements

Keep frontend UI, project state, API access, and viewer lifecycle in separate modules. Keep backend transport, validation/domain models, mesh processing, project storage, job execution, and solver serialization separate. Domain logic must be testable without a browser or HTTP server.

The canonical project contains a schema version, solver target, unit system, original asset hashes, stable domain/face references, configuration, and export provenance. Server paths and viewer objects are implementation details and must not be persisted as project identity. The API owns persisted scientific state; UI state and unsaved edits remain explicit.

Use a solver adapter boundary so adding a second dialect does not spread serializer conditionals through UI components. Use a storage boundary to isolate local project files, atomic saves, and schema migrations from the scientific domain model.

## Delivery sequence and release gates

| Milestone | Deliverable | Exit gate |
| --- | --- | --- |
| 0 — Compatibility baseline | Selected solver version, fixture corpus, capability matrix, reference hardware, dependency compatibility check | Reviewed supported-case matrix and agreed benchmarks; solver executable available for validation. |
| 1 — Foundation | Typed Svelte frontend, modular FastAPI backend, generated API contract, locked toolchains, CI | Clean Windows/Linux installs; contract/type/build checks pass. |
| 2 — Correct vertical slice | Import one supported mesh case, identify faces, assign BCs, validate, export portable package | Actual solver accepts the representative package; original geometry and IDs remain intact. |
| 3 — Complete configuration workspace | Remaining supported physics/BCs, project save/reopen, jobs, error handling, accessibility | All applicable P0 functional fixtures pass, including failure and cancellation cases. |
| 4 — First release | Performance/resource verification, deployment documentation, migration instructions | All P0 requirements pass with recorded evidence; no known invalid scientific exports. |
| 5 — Results workspace | P1 results inspection and reproducibility features | Numerical/display reference checks pass independently of export acceptance. |

Migrate by working vertical slices, keeping the existing application runnable until the replacement passes its acceptance gates. Reuse verified domain fixtures and useful components. Preserve intended behavior, but correct confirmed scientific defects rather than reproducing them for superficial parity. Record any intentionally removed capability and the migration path.

## Decisions to settle before implementation

| Decision | Proposed default | Why it matters |
| --- | --- | --- |
| Solver family/version | Select one explicitly in milestone 0 | Determines XML tags, assets, physics, and validation commands. |
| Supported physics | Validated fluid workflow first; expand only with reference cases | Current UI/model labels alone do not establish working Structure/FSI support. |
| Deployment | Local single-user Windows/Linux | Package the UI, loopback API, storage, and processing for use on one machine. |
| Unit convention | Explicit project unit system chosen against solver examples | Existing density/viscosity defaults cannot establish a universally correct convention. |
| Mesh scale | 50 MiB initial upload limit; separate decoded geometry budget | Compressed file size does not bound memory or rendering cost. |
| Results formats/fields | Agree on representative solver output fixtures in milestone 5 | Avoids implementing unverified time-series and association assumptions. |

Each requirement should move from Proposed to Accepted, In progress, Verified, or Deferred, with a linked implementation change and acceptance evidence. Deferring a P0 item requires explicitly revising first-release scope; it must not silently disappear.

## Sources

Repository evidence is identified in the current-evidence table. Library recommendations link to their official documentation above. Solver lineage reference: [SimVascular svMultiPhysics repository](https://github.com/SimVascular/svMultiPhysics), reached from the svFSIplus repository on 2026-09-23. Exact version compatibility, performance targets, and solver-output correctness remain implementation verification gates.
