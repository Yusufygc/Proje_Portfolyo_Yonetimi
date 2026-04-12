"""services/interfaces/i_service.py — Servis ABC tanımları."""

from abc import ABC, abstractmethod


class IProjectService(ABC):
    @abstractmethod
    def get_all(self): ...

    @abstractmethod
    def get_featured(self): ...

    @abstractmethod
    def get_by_id(self, project_id: int): ...

    @abstractmethod
    def create(self, data: dict): ...

    @abstractmethod
    def update(self, project_id: int, data: dict): ...

    @abstractmethod
    def delete(self, project_id: int): ...


class ICertificateService(ABC):
    @abstractmethod
    def get_all(self): ...

    @abstractmethod
    def create(self, data: dict): ...

    @abstractmethod
    def update(self, cert_id: int, data: dict): ...

    @abstractmethod
    def delete(self, cert_id: int): ...


class IPersonalInfoService(ABC):
    @abstractmethod
    def get(self): ...

    @abstractmethod
    def update(self, data: dict): ...


class IResourceService(ABC):
    @abstractmethod
    def get_all(self): ...

    @abstractmethod
    def create(self, data: dict): ...

    @abstractmethod
    def update(self, resource_id: int, data: dict): ...

    @abstractmethod
    def delete(self, resource_id: int): ...
