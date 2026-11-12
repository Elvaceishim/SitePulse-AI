from abc import ABC, abstractmethod

from app.models.site import Site
from app.models.risk import RiskAssessment


class RiskDataProvider(ABC):

    @abstractmethod
    def get_sites(self) -> list[Site]:
        pass

    @abstractmethod
    def get_risk_assessments(self) -> list[RiskAssessment]:
        pass