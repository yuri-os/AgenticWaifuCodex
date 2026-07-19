"""The forget covenant (§6.7, §13.3): supersede, not delete. The fact leaves
the working files and every future prompt — but `git log` still shows it ever
existed."""
from __future__ import annotations

import subprocess

from app import vaultgit
from app.memory.partner import Op, apply_ops
from app.memory.store import Record


def git_log_S(vault, needle: str) -> str:
    """Commits whose diffs ever touched `needle` (the auditability check)."""
    return subprocess.run(
        ["git", "-C", str(vault), "log", "-S", needle, "--oneline"],
        capture_output=True, text=True).stdout


async def test_forget_supersedes_not_deletes(vault, store):
    # she learns a fact (USER.md) and lives a moment that mentions it (journal)
    vaultgit.atomic_write(
        store.user_md_path,
        apply_ops(store.read_user_md(),
                  [Op("Don't forget", "anniversary: 14 Feb", "add", 1.0)]))
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="our anniversary is 14 Feb",
                                reply="the fourteenth — kept."))
    vaultgit.commit(vault, "turn s:0")
    assert "anniversary" in store.read_user_md()
    assert store.recall("when is our anniversary?", k=3)

    # "forget that" — the covenant (ch. 15)
    count = store.forget("anniversary", why="you asked")
    assert count >= 1

    # (a) gone from the working tree…
    assert "anniversary" not in store.read_user_md()
    # (b) …tombstoned in the ledger…
    ledger = store.forgotten_path.read_text()
    assert "forgot: anniversary" in ledger and "you asked" in ledger
    # (c) …gone from every future prompt: recall never resurfaces it (§6.7)
    assert all("anniversary" not in m.text
               for m in store.recall("when is our anniversary?", k=6))
    # (d) …but history is not rewritten: git still knows it existed
    assert git_log_S(vault, "anniversary: 14 Feb").strip(), \
        "the old value must survive in git log (auditability, §4.2)"


async def test_assembly_never_reads_the_ledger(vault, store):
    """forgotten.md is a suppression list, not a prompt block (§6.7)."""
    from app.core import assemble as asm
    from app.core.soul import SoulLoader

    store.forget("the old flame", why="asked")
    soul = SoulLoader(vault / "soul").load()
    prompt = asm.assemble(soul, user_md=store.read_user_md(),
                          summary="", memories=[], lore=[], window=[],
                          user_msg="hey")
    assert "the old flame" not in prompt.system


def test_forget_returns_zero_on_no_match(store):
    assert store.forget("a thing she never knew") == 0
    # the ask itself is still ledgered — the covenant is append-only
    assert "a thing she never knew" in store.forgotten_path.read_text()
