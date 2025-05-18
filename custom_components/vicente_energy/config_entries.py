"""Stub for Home Assistant config entries."""

class ConfigFlow:
    # stub init
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__()

    def async_show_form(self, step_id, data_schema):
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
        }

    def async_create_entry(self, title, data):
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
        }
