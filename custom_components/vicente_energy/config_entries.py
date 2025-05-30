"""Stub for Home Assistant config entries."""

class ConfigFlow:
    """Simple stub replacement for HA ConfigFlow used in tests."""

    # stub init
    def __init_subclass__(cls, *args, **kwargs):
        """Ignore subclass arguments."""
        super().__init_subclass__()

    def async_show_form(self, step_id, data_schema):
        """Return a fake form result structure."""
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
        }

    def async_create_entry(self, title, data):
        """Return a fake entry result structure."""
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
        }
