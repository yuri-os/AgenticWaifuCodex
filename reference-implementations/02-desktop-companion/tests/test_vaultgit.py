"""Vault file moves recover cleanly when an old onboarding target already exists."""
from __future__ import annotations

from app import vaultgit


def test_force_move_replaces_a_stale_bootstrap_archive(tmp_path):
    vault = tmp_path / "vault"
    source = vault / "soul" / "BOOTSTRAP.md"
    target = vault / "soul" / "onboarded" / "BOOTSTRAP.done.md"
    source.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    source.write_text("current bootstrap", encoding="utf-8")
    target.write_text("stale archive", encoding="utf-8")
    vaultgit.ensure_repo(vault)
    vaultgit.commit(vault, "seed")

    vaultgit.mv(vault, "soul/BOOTSTRAP.md", "soul/onboarded/BOOTSTRAP.done.md",
                force=True)

    assert not source.exists()
    assert target.read_text(encoding="utf-8") == "current bootstrap"
