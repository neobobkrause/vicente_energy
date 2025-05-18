
async def async_register_services(hass, domain, session_manager, state_manager):
    async def handle_set_power(call):
        power_kw = call.data.get("power_level_kw")
        if power_kw is not None:
            session_manager.set_power_level(power_kw)
            # Force an update of the Power Level sensor
            await hass.helpers.entity_component.async_update_entity(f"sensor.{domain}_power_level")

    async def handle_reset_history(call):
        # Reset all bias and history data
        state_manager.data["solar_bias"] = 0.0
        state_manager.data["load_bias"] = 0.0
        state_manager.data["session_bias"] = 0.0
        state_manager.data["last_session_kwh"] = 0.0
        state_manager.data["last_raw_session_kwh"] = None
        state_manager.data["forecast_error_history"] = {"solar_errors": [], "load_errors": []}
        state_manager.data["session_bias_history"] = []
        await state_manager.async_save()

    hass.services.async_register(domain, "set_power_level", handle_set_power)
    hass.services.async_register(domain, "reset_history", handle_reset_history)

