from app.domain.ports.health_probe import HealthProbe


class HealthService:
    def __init__(self, probes: list[HealthProbe]) -> None:
        self._probes = probes

    def check(self) -> dict[str, str]:
        results: dict[str, str] = {}
        for probe in self._probes:
            try:
                probe.check()
                results[probe.name] = "ok"
            except Exception:
                results[probe.name] = "unavailable"
        return results
