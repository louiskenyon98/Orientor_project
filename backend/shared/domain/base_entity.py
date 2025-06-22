"""Base classes for Domain-Driven Design entities and value objects."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json


class DomainEvent(ABC):
    """Base class for domain events."""
    
    def __init__(self, aggregate_id: str):
        self.event_id = str(uuid4())
        self.aggregate_id = aggregate_id
        self.occurred_at = datetime.utcnow()
        self.event_type = self.__class__.__name__
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'occurred_at': self.occurred_at.isoformat()
        }


class ValueObject(ABC):
    """Base class for value objects - immutable objects defined by their attributes."""
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self):
        attrs = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


class Entity(ABC):
    """Base class for entities - objects with identity."""
    
    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid4())
        self._domain_events: List[DomainEvent] = []
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def add_domain_event(self, event: DomainEvent):
        """Add a domain event to be dispatched."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return domain events."""
        events = self._domain_events[:]
        self._domain_events.clear()
        return events


class AggregateRoot(Entity):
    """Base class for aggregate roots - entities that serve as consistency boundaries."""
    
    def __init__(self, id: Optional[str] = None):
        super().__init__(id)
        self.version = 0
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_version(self):
        """Increment version for optimistic locking."""
        self.version += 1
        self.updated_at = datetime.utcnow()


class Repository(ABC):
    """Base repository interface."""
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[AggregateRoot]:
        """Find aggregate by ID."""
        pass
    
    @abstractmethod
    async def save(self, aggregate: AggregateRoot) -> None:
        """Save aggregate."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete aggregate by ID."""
        pass


class Specification(ABC):
    """Base class for specifications - encapsulate business rules."""
    
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if candidate satisfies the specification."""
        pass
    
    def and_(self, other: 'Specification') -> 'CompositeSpecification':
        """Create AND specification."""
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'CompositeSpecification':
        """Create OR specification."""
        return OrSpecification(self, other)
    
    def not_(self) -> 'CompositeSpecification':
        """Create NOT specification."""
        return NotSpecification(self)


class CompositeSpecification(Specification):
    """Base class for composite specifications."""
    pass


class AndSpecification(CompositeSpecification):
    """AND specification."""
    
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(CompositeSpecification):
    """OR specification."""
    
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(CompositeSpecification):
    """NOT specification."""
    
    def __init__(self, spec: Specification):
        self.spec = spec
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.spec.is_satisfied_by(candidate)