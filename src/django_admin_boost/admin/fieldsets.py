from typing import Iterable


def add_to_fieldset(self, name: str, fields: Iterable[str]):
    """Add fields to a fieldset by name. Create the fieldset if it doesn't exist."""
    if self.fieldsets is None:
        self.fieldsets = []

    fieldset_dict = None

    for fieldset in self.fieldsets:
        if fieldset[0] == name:
            fieldset_dict = fieldset[1]
            break

    if fieldset_dict is None:
        fieldset_dict = {"fields": []}
        self.fieldsets.append((name, fieldset_dict))
    else:
        if "fields" not in fieldset_dict:
            fieldset_dict["fields"] = []
        elif isinstance(fieldset_dict["fields"], tuple):
            fieldset_dict["fields"] = list(fieldset_dict["fields"])

    fieldset_dict["fields"].extend(fields)


def remove_from_fieldset(self, name: str, fields: Iterable[str]):
    """Remove fields from a fieldset by name."""
    if self.fieldsets is None:
        return

    for fieldset in self.fieldsets:
        if fieldset[0] == name:
            fieldset_dict = fieldset[1]
            if "fields" in fieldset_dict:
                for field in fields:
                    if field in fieldset_dict["fields"]:
                        fieldset_dict["fields"].remove(field)
            break
