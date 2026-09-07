"""Poseidon — núcleo de comando hidráulico / dinâmica dos fluidos (CEDAE).

Modelos apenas consultivos. Sem escrita em SCADA. Sem LLM no laço de controle.
Todos os fixtures trafegam no envelope {data, meta} com meta.live=false.
"""

from poseidon.domain import META_FIXTURE, envelope

__version__ = "0.1.0"
__all__ = ["__version__", "envelope", "META_FIXTURE"]
