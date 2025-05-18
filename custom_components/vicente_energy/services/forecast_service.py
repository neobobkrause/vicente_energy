from abc import ABC, abstractmethod


class ForecastService(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def get_forecast_time(self) -> float:
        pass

    @abstractmethod
    async def get_production_now(self) -> float:
        pass

    @abstractmethod
    async def get_production_this_hour(self) -> float:
        pass

    @abstractmethod
    async def get_production_next_hour(self) -> float:
        pass

    @abstractmethod
    async def get_production_today(self) -> float:
        pass

    @abstractmethod
    async def get_production_tomorrow(self) -> float:
        pass

    @abstractmethod
    async def get_production_peak_today(self) -> float:
        pass

    @abstractmethod
    async def get_production_peak_tomorrow(self) -> float:
        pass

    @abstractmethod
    def register_callback(self, callback: Callable[[str, State], None]) -> None:
        pass
