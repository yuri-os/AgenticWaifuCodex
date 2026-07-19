"""memory-lab: the companion memory subsystem, extracted to run on its own.

A teaching extract of Build #1's memory core (→ book ch. 15, ch. 31), with no
web server, no LLM API, and no git required. Import the pieces you want:

    from memory.store import FileMemoryStore, Record
    from memory.embed import HashingEmbedder
    from memory.partner import KeywordExtractor
"""
