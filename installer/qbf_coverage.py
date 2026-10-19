"""Ferramentas de inspeção QBF1 sem redistribuir fontes do jogo ou SingleScreen.

Esta etapa apenas examina metadados de uma fonte fornecida localmente pelo usuário.
Não produz uma fonte HD nem altera a ROM.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct

PTBR_CHARS = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
QBF_HEADER_SIZE = 16
QBF_ENTRY_SIZE = 8


@dataclass(frozen=True)
class QbfCoverage:
    glyph_count: int
    glyph_codes: frozenset[int]
    missing_ptbr: tuple[str, ...]

    @property
    def covers_ptbr(self) -> bool:
        return not self.missing_ptbr


def inspect_qbf_coverage(data: bytes) -> QbfCoverage:
    """Lê somente o cabeçalho e os códigos dos glifos QBF1.

    Não interpreta os bitmaps nem assume que a presença de um código
    garante a qualidade visual do glifo.
    """
    if len(data) < QBF_HEADER_SIZE or data[:4] != b"QBF1":
        raise ValueError("Fonte QBF1 inválida ou truncada")
    count = struct.unpack_from("<H", data, 4)[0]
    end = QBF_HEADER_SIZE + count * QBF_ENTRY_SIZE
    if count == 0 or end > len(data):
        raise ValueError("Tabela de glifos QBF1 inválida ou truncada")
    codes = [struct.unpack_from("<H", data, QBF_HEADER_SIZE + i * QBF_ENTRY_SIZE)[0]
             for i in range(count)]
    if len(set(codes)) != len(codes):
        raise ValueError("Tabela QBF1 contém códigos de glifos duplicados")
    present = frozenset(codes)
    missing = tuple(ch for ch in PTBR_CHARS if ord(ch) not in present)
    return QbfCoverage(count, present, missing)
