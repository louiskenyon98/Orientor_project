"""Event bus implementation using RabbitMQ for microservices communication."""

import json
import asyncio
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import aio_pika
from aio_pika import Message, Connection, Channel, Exchange, Queue
import logging

logger = logging.getLogger(__name__)


class Event:
    """Base event class for all domain events."""
    
    def __init__(self, data: Dict[str, Any], event_type: Optional[str] = None):
        self.event_id = data.get('event_id', '')
        self.event_type = event_type or data.get('event_type', self.__class__.__name__)
        self.aggregate_id = data.get('aggregate_id', '')
        self.occurred_at = data.get('occurred_at', datetime.utcnow().isoformat())
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'occurred_at': self.occurred_at,
            **self.data
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventBus:
    """RabbitMQ-based event bus for pub/sub messaging."""
    
    def __init__(self, amqp_url: str = "amqp://guest:guest@localhost/"):
        self.amqp_url = amqp_url
        self._connection: Optional[Connection] = None
        self._channel: Optional[Channel] = None
        self._exchange: Optional[Exchange] = None
        self._handlers: Dict[str, List[Callable]] = {}
        self._queues: Dict[str, Queue] = {}
    
    async def connect(self):
        """Connect to RabbitMQ."""
        try:
            self._connection = await aio_pika.connect_robust(self.amqp_url)
            self._channel = await self._connection.channel()
            
            # Declare topic exchange for event routing
            self._exchange = await self._channel.declare_exchange(
                'orientor.events',
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            logger.info("Connected to RabbitMQ event bus")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from RabbitMQ."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            self._exchange = None
            logger.info("Disconnected from RabbitMQ event bus")
    
    async def publish(self, event: Event, routing_key: Optional[str] = None):
        """Publish an event to the event bus."""
        try:
            if not self._exchange:
                await self.connect()
            
            # Use event type as routing key if not specified
            if not routing_key:
                routing_key = f"event.{event.event_type.lower()}"
            
            message = Message(
                body=event.to_json().encode(),
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={
                    'event_type': event.event_type,
                    'aggregate_id': event.aggregate_id
                }
            )
            
            await self._exchange.publish(message, routing_key=routing_key)
            logger.debug(f"Published event {event.event_type} with routing key {routing_key}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def subscribe(
        self, 
        event_types: List[str], 
        handler: Callable[[Event], None],
        queue_name: Optional[str] = None
    ):
        """Subscribe to specific event types."""
        try:
            if not self._channel:
                await self.connect()
            
            # Create unique queue name if not provided
            if not queue_name:
                queue_name = f"orientor.{'.'.join(event_types)}.{id(handler)}"
            
            # Declare queue
            queue = await self._channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': 3600000,  # 1 hour TTL
                    'x-max-length': 10000  # Max 10k messages
                }
            )
            
            # Bind queue to exchange for each event type
            for event_type in event_types:
                routing_key = f"event.{event_type.lower()}"
                await queue.bind(self._exchange, routing_key=routing_key)
                
                # Store handler
                if event_type not in self._handlers:
                    self._handlers[event_type] = []
                self._handlers[event_type].append(handler)
            
            # Start consuming messages
            await queue.consume(self._process_message)
            
            self._queues[queue_name] = queue
            logger.info(f"Subscribed to events {event_types} on queue {queue_name}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to events: {e}")
            raise
    
    async def _process_message(self, message: aio_pika.IncomingMessage):
        """Process incoming message."""
        async with message.process():
            try:
                # Parse message
                data = json.loads(message.body.decode())
                event_type = data.get('event_type', '')
                
                # Create event object
                event = Event(data, event_type)
                
                # Call handlers
                handlers = self._handlers.get(event_type, [])
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Handler error for event {event_type}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                # Reject message and don't requeue on parse errors
                await message.reject(requeue=False)


class EventPublisher:
    """Simplified event publisher interface."""
    
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
    
    async def publish_career_recommended(self, user_id: str, career_id: str, score: float):
        """Publish career recommendation event."""
        event = Event({
            'event_type': 'CareerRecommended',
            'aggregate_id': user_id,
            'user_id': user_id,
            'career_id': career_id,
            'recommendation_score': score,
            'occurred_at': datetime.utcnow().isoformat()
        })
        await self._event_bus.publish(event)
    
    async def publish_skill_assessed(self, user_id: str, skill_id: str, level: int):
        """Publish skill assessment event."""
        event = Event({
            'event_type': 'SkillAssessed',
            'aggregate_id': user_id,
            'user_id': user_id,
            'skill_id': skill_id,
            'proficiency_level': level,
            'occurred_at': datetime.utcnow().isoformat()
        })
        await self._event_bus.publish(event)
    
    async def publish_test_completed(self, user_id: str, test_type: str, results: Dict[str, Any]):
        """Publish test completion event."""
        event = Event({
            'event_type': 'TestCompleted',
            'aggregate_id': user_id,
            'user_id': user_id,
            'test_type': test_type,
            'results': results,
            'occurred_at': datetime.utcnow().isoformat()
        })
        await self._event_bus.publish(event)
    
    async def publish_user_profile_updated(self, user_id: str, changes: Dict[str, Any]):
        """Publish user profile update event."""
        event = Event({
            'event_type': 'UserProfileUpdated',
            'aggregate_id': user_id,
            'user_id': user_id,
            'changes': changes,
            'occurred_at': datetime.utcnow().isoformat()
        })
        await self._event_bus.publish(event)
    
    async def publish_match_found(self, user_id: str, match_type: str, match_id: str, score: float):
        """Publish match found event."""
        event = Event({
            'event_type': 'MatchFound',
            'aggregate_id': user_id,
            'user_id': user_id,
            'match_type': match_type,
            'match_id': match_id,
            'match_score': score,
            'occurred_at': datetime.utcnow().isoformat()
        })
        await self._event_bus.publish(event)


# Singleton instances
_event_bus: Optional[EventBus] = None
_event_publisher: Optional[EventPublisher] = None


def get_event_bus(amqp_url: str = "amqp://guest:guest@localhost/") -> EventBus:
    """Get or create event bus singleton."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus(amqp_url)
    return _event_bus


def get_event_publisher(amqp_url: str = "amqp://guest:guest@localhost/") -> EventPublisher:
    """Get or create event publisher singleton."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher(get_event_bus(amqp_url))
    return _event_publisher