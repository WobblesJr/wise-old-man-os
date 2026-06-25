"""DriveBridge adapter — Limbach WORK files. BLOCKED pending IT; mock only."""
from __future__ import annotations

_MOCK_WORK_FILES = [
    {"id": "f1", "name": "ProjectAlpha_L3_Manpower_v0.3.xlsx", "kind": "spreadsheet",
     "modified": "2h ago", "owner": "Gavin"},
    {"id": "f2", "name": "RFI-014_Mech_Clearances.pdf", "kind": "pdf",
     "modified": "4h ago", "owner": "Gavin"},
    {"id": "f3", "name": "Spec_230500_Common_Work_Results.pdf", "kind": "pdf",
     "modified": "Yesterday", "owner": "Eng of Record"},
    {"id": "f4", "name": "Submittal_Log_ProjectBeta.xlsx", "kind": "spreadsheet",
     "modified": "Yesterday", "owner": "Priya"},
]


class MockDriveBridge:
    def list_files(self, scope: str) -> list[dict]:
        # Work scope only; personal returns empty (uses Google Drive instead).
        return _MOCK_WORK_FILES if scope == "work" else []


# --------------------------------------------------------------------------- #
# TODO(live): LiveDriveBridge — BLOCKED pending IT (NEEDS-FROM-YOU #4)
#   Options once unblocked: MS Graph (LIMBACH_GRAPH_*) drive.items, or a synced
#   path at LIMBACH_DRIVE_ROOT. Implement list_files() with the same shape.
# --------------------------------------------------------------------------- #
