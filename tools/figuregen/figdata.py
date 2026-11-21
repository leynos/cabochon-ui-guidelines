"""Load and validate the shared figure catalogue.

The module holds no file I/O at import. `load_document` reads and parses the
JSON document at a caller-supplied path, `Catalogue.from_document` validates
its four catalogue sections, and `load_catalogue` returns the parsed
`Catalogue`. `figuregen.cli` resolves `DATA_PATH`, loads the catalogue once and
threads it through the builders that draw states. `OUT` names the committed
`figures` directory.
"""

from __future__ import annotations

import dataclasses
import json
import typing as typ
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

OUT = ROOT / "figures"

DATA_PATH = ROOT / "tools" / "figure-data.json"

# ``from`` is a Python keyword, so the transition record is declared with the
# functional TypedDict syntax that keeps the document's own field name.
LiveTransition = typ.TypedDict(
    "LiveTransition",
    {
        "id": str,
        "from": list[str],
        "event": str,
        "to": str,
        "owner": str,
    },
)

_TRANSITION_TEXT_FIELDS = ("id", "event", "to", "owner")

# The fields `figuregen.ornaments.state_chip` reads from a state record, and
# the fields `figuregen.production.annotate` reads from a figure specification.
_STATE_FIELDS = ("word", "colour", "id", "mark", "role")
_SPEC_FIELDS = ("class", "scale", "components", "profile", "states")
_SPEC_CLASSES = {"schematic", "editorial", "production"}


class ContractError(Exception):
    """Report a figure contract that cannot be used.

    The error covers a contract file that cannot be read, decoded or parsed as
    JSON, and a parsed document whose catalogue sections are missing or
    structurally invalid. The message names the offending path or key and the
    underlying error where one exists.
    """


@dataclasses.dataclass(frozen=True)
class StateTables:
    """Hold the live and resolution state records read from the contract.

    Attributes
    ----------
    live : dict[str, dict[str, str]]
        The live state records, keyed by state name.
    resolution : dict[str, dict[str, str]]
        The resolution state records, keyed by state name.
    """

    live: dict[str, dict[str, str]]
    resolution: dict[str, dict[str, str]]


@dataclasses.dataclass(frozen=True)
class Catalogue:
    """Hold the validated sections of ``tools/figure-data.json``.

    Attributes
    ----------
    live_states : dict[str, dict[str, str]]
        The live state records.
    live_transitions : list[LiveTransition]
        The legal live-state transitions.
    resolution_states : dict[str, dict[str, str]]
        The resolution state records.
    figure_specs : dict[str, dict[str, object]]
        The declared figure specifications, keyed by figure name.
    """

    live_states: dict[str, dict[str, str]]
    live_transitions: list[LiveTransition]
    resolution_states: dict[str, dict[str, str]]
    figure_specs: dict[str, dict[str, object]]

    @property
    def states(self) -> StateTables:
        """The live and resolution state records.

        Returns
        -------
        StateTables
            The two state tables, ready for `figuregen.ornaments.state_chip`.
        """
        return StateTables(live=self.live_states, resolution=self.resolution_states)

    @classmethod
    def from_document(cls, document: object) -> Catalogue:
        """Validate a parsed contract document and return its catalogue.

        Parameters
        ----------
        document : object
            The value decoded from the contract file.

        Returns
        -------
        Catalogue
            The four validated catalogue sections.

        Raises
        ------
        ContractError
            If ``document`` is not a JSON object, if it lacks one of the
            ``live_states``, ``live_transitions``, ``resolution_states`` or
            ``figures`` sections, or if a section has the wrong structure.
        """
        mapping = _require_mapping(document, name="top level")
        return cls(
            live_states=_string_table(
                _section(mapping, "live_states"), name="live_states"
            ),
            live_transitions=_transitions(_section(mapping, "live_transitions")),
            resolution_states=_string_table(
                _section(mapping, "resolution_states"), name="resolution_states"
            ),
            figure_specs=_spec_table(_section(mapping, "figures")),
        )


def _section(mapping: dict[str, object], key: str) -> object:
    """Return one required section of the contract document.

    Parameters
    ----------
    mapping : dict[str, object]
        The parsed contract document.
    key : str
        The section name to retrieve.

    Returns
    -------
    object
        The section value, which the caller validates.

    Raises
    ------
    ContractError
        If the section is absent.
    """
    if key not in mapping:
        raise ContractError(f"figure contract is missing the {key!r} section")
    return mapping[key]


def _require_mapping(value: object, *, name: str) -> dict[str, object]:
    """Return ``value`` as a JSON object or raise `ContractError`.

    Parameters
    ----------
    value : object
        The candidate JSON value.
    name : str
        The key path used in the error message.

    Returns
    -------
    dict[str, object]
        The value, typed as a JSON object.

    Raises
    ------
    ContractError
        If ``value`` is not a JSON object.
    """
    if not isinstance(value, dict):
        raise ContractError(f"figure contract {name} is not a JSON object")
    return typ.cast("dict[str, object]", value)


def _string_table(value: object, *, name: str) -> dict[str, dict[str, str]]:
    """Validate a mapping of state names to string records.

    Parameters
    ----------
    value : object
        The candidate section value.
    name : str
        The section name used in error messages.

    Returns
    -------
    dict[str, dict[str, str]]
        The validated state records.

    Raises
    ------
    ContractError
        If the section is not an object, if a record is not an object, or if a
        record holds a non-string value.
    """
    table = _require_mapping(value, name=name)
    records: dict[str, dict[str, str]] = {}
    for state_name, record_value in table.items():
        record = _require_mapping(record_value, name=f"{name}.{state_name}")
        missing = [field for field in _STATE_FIELDS if field not in record]
        if missing:
            raise ContractError(
                f"figure contract {name}.{state_name} lacks {missing}"
            )
        if not all(isinstance(item, str) for item in record.values()):
            raise ContractError(
                f"figure contract {name}.{state_name} has a non-string value"
            )
        records[str(state_name)] = {str(key): str(item) for key, item in record.items()}
    return records


def _transitions(value: object) -> list[LiveTransition]:
    """Validate the live transition records.

    Parameters
    ----------
    value : object
        The candidate ``live_transitions`` section.

    Returns
    -------
    list[LiveTransition]
        The validated transition records.

    Raises
    ------
    ContractError
        If the section is not an array, or if a record is missing a string
        field or holds a ``from`` value that is not an array of strings.
    """
    if not isinstance(value, list):
        raise ContractError("figure contract live_transitions is not a JSON array")
    transitions: list[LiveTransition] = []
    for index, record_value in enumerate(value):
        record = _require_mapping(record_value, name=f"live_transitions[{index}]")
        for field in _TRANSITION_TEXT_FIELDS:
            if not isinstance(record.get(field), str):
                raise ContractError(
                    f"figure contract live_transitions[{index}].{field} is not a string"
                )
        sources = record.get("from")
        if not isinstance(sources, list) or not all(
            isinstance(source, str) for source in sources
        ):
            raise ContractError(
                f"figure contract live_transitions[{index}].from "
                "is not an array of strings"
            )
        transitions.append(typ.cast("LiveTransition", record))
    return transitions


def _spec_table(value: object) -> dict[str, dict[str, object]]:
    """Validate the declared figure specifications.

    Parameters
    ----------
    value : object
        The candidate ``figures`` section.

    Returns
    -------
    dict[str, dict[str, object]]
        The validated figure specifications, keyed by figure name.

    Raises
    ------
    ContractError
        If the section is not an object, if a specification is not an object,
        if a specification omits a field `annotate` reads, if its class is not
        a string, or if it declares a class other than ``schematic``,
        ``editorial`` or ``production``.
    """
    table = _require_mapping(value, name="figures")
    specs: dict[str, dict[str, object]] = {}
    for figure_name, spec_value in table.items():
        spec = dict(_require_mapping(spec_value, name=f"figures.{figure_name}"))
        missing = [field for field in _SPEC_FIELDS if field not in spec]
        if missing:
            raise ContractError(f"figure contract figures.{figure_name} lacks {missing}")
        figure_class = spec["class"]
        if not isinstance(figure_class, str):
            raise ContractError(
                f"figure contract figures.{figure_name}.class is not a string"
            )
        if figure_class not in _SPEC_CLASSES:
            raise ContractError(
                f"figure contract figures.{figure_name}.class "
                f"is not a known class: {figure_class!r}"
            )
        specs[str(figure_name)] = spec
    return specs


def load_document(path: Path) -> dict[str, object]:
    """Read and decode the figure contract at ``path``.

    Parameters
    ----------
    path : Path
        The contract file to read as UTF-8 JSON.

    Returns
    -------
    dict[str, object]
        The decoded JSON object.

    Raises
    ------
    ContractError
        If the file cannot be read, is not valid UTF-8, is not valid JSON or
        does not hold a JSON object. The message names ``path`` and the
        underlying error.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ContractError(f"cannot read figure contract {path}: {error}") from error
    except UnicodeDecodeError as error:
        raise ContractError(f"cannot decode figure contract {path}: {error}") from error
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise ContractError(f"cannot parse figure contract {path}: {error}") from error
    return _require_mapping(document, name=str(path))


def load_catalogue(path: Path) -> Catalogue:
    """Load and validate the figure contract at ``path``.

    Parameters
    ----------
    path : Path
        The contract file to load.

    Returns
    -------
    Catalogue
        The validated catalogue.

    Raises
    ------
    ContractError
        If `load_document` or `Catalogue.from_document` rejects the contract.
    """
    return Catalogue.from_document(load_document(path))
