"""
Based on https://github.com/influxdata/influxdb-client-python 1.25.0

Flux employs a basic data model built from basic data types.

The data model consists of tables, records, columns.
"""
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, cast


class FluxStructure:
    """The data model consists of tables, records, columns."""

    pass


class FluxColumn(FluxStructure):
    """A column has a label and a data type."""

    index: Optional[int]
    label: Optional[str]
    data_type: Optional[str]
    group: Optional[bool]
    default_value: Any

    def __init__(
        self,
        index: Optional[int] = None,
        label: Optional[str] = None,
        data_type: Optional[str] = None,
        group: Optional[bool] = None,
        default_value: Any = None,
    ) -> None:
        """Initialize defaults."""
        self.default_value = default_value
        self.group = group
        self.data_type = data_type
        self.label = label
        self.index = index

    def __repr__(self) -> str:
        """Format for inspection."""
        fields = [repr(self.index)] + [
            f'{name}={getattr(self, name)!r}'
            for name in ('label', 'data_type', 'group', 'default_value')
            if getattr(self, name) is not None
        ]
        return f"{type(self).__name__}({', '.join(fields)})"


class FluxRecord(FluxStructure):
    """A record is a tuple of named values and is represented using an object type."""

    table: int
    values: Dict[str, Any]

    def __init__(self, table: int, values: Optional[Dict[str, Any]] = None) -> None:
        """Initialize defaults."""
        if values is None:
            values = {}
        self.table = table
        self.values = values

    def get_start(self) -> datetime:
        """Get '_start' value."""
        return cast(datetime, self["_start"])

    def get_stop(self) -> datetime:
        """Get '_stop' value."""
        return cast(datetime, self["_stop"])

    def get_time(self) -> datetime:
        """Get timestamp."""
        return cast(datetime, self["_time"])

    def get_value(self) -> Any:
        """Get field value."""
        return self["_value"]

    def get_field(self) -> str:
        """Get field name."""
        return cast(str, self["_field"])

    def get_measurement(self) -> str:
        """Get measurement name."""
        return cast(str, self["_measurement"])

    def __getitem__(self, key: str) -> Any:
        """Get value by key."""
        return self.values.__getitem__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set value with key and value."""
        return self.values.__setitem__(key, value)

    def __str__(self) -> str:
        """Return formatted output."""
        cls_name = type(self).__name__
        return f"{cls_name}() table: {str(self.table)}, {str(self.values)}"

    def __repr__(self) -> str:
        """Format for inspection."""
        return f"<{type(self).__name__}: field={self.values.get('_field')}, value={self.values.get('_value')}>"


class FluxTable(FluxStructure):
    """
    A table is set of records with a common set of columns and a group key.

    The table can be serialized into JSON by::

        import json
        from influxdb_client.client.flux_table import FluxStructureEncoder

        output = json.dumps(tables, cls=FluxStructureEncoder, indent=2)
        print(output)

    """

    columns: List[FluxColumn]
    records: List[FluxRecord]

    def __init__(self) -> None:
        """Initialize defaults."""
        self.columns = []
        self.records = []

    def get_group_key(self) -> List[FluxColumn]:
        """
        Group key is a list of columns.

        A table’s group key denotes which subset of the entire dataset is assigned to the table.
        """
        return list(filter(lambda column: (column.group is True), self.columns))

    def __str__(self) -> str:
        """Return formatted output."""
        cls_name = type(self).__name__
        return cls_name + "() columns: " + str(len(self.columns)) + ", records: " + str(len(self.records))

    def __repr__(self) -> str:
        """Format for inspection."""
        return f"<{type(self).__name__}: {len(self.columns)} columns, {len(self.records)} records>"

    def __iter__(self) -> Iterator[FluxRecord]:
        """Iterate over records."""
        return iter(self.records)
