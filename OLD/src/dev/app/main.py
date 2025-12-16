#!/usr/bin/env python3
"""
The Mona - Main Application Entry Point

Initializes and coordinates all system components:
- MQTT client and broker connectivity
- Game engine with state machine
- Web interface (FastAPI + WebSocket)
- Audio service for JBL speaker integration
- Proper shutdown handling and health monitoring
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from mona.audio.service import AudioService
from mona.config.loader import load_config
from mona.game.engine import GameEngine
from mona.mqtt.client import MQTTClient
from mona.util.logging import setup_logging
from mona.web.api import create_app


class MonaApplication:
    """Main application coordinator for The Mona system."""
    
    def __init__(self):
        self.config = load_config()
        self.logger = logging.getLogger("mona.main")
        
        # Core components
        self.mqtt_client: Optional[MQTTClient] = None
        self.game_engine: Optional[GameEngine] = None
        self.audio_service: Optional[AudioService] = None
        self.web_app = None
        
        # Shutdown coordination
        self._shutdown_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
    
    async def startup(self) -> None:
        """Initialize all system components in correct order."""
        self.logger.info("Starting The Mona system...")
        
        try:
            # 1. Audio service (independent)
            self.logger.info("Initializing audio service...")
            self.audio_service = AudioService(self.config.audio)
            await self.audio_service.initialize()
            
            # 2. MQTT client
            self.logger.info("Connecting to MQTT broker...")
            self.mqtt_client = MQTTClient(self.config.mqtt)
            await self.mqtt_client.connect()
            
            # 3. Game engine (depends on MQTT)
            self.logger.info("Starting game engine...")
            self.game_engine = GameEngine(
                self.config.game, 
                self.mqtt_client,
                self.audio_service
            )
            await self.game_engine.start()
            
            # 4. Web interface
            self.logger.info("Creating web application...")
            self.web_app = create_app(
                self.game_engine,
                self.mqtt_client, 
                self.audio_service,
                self.config
            )
            
            # Start background tasks
            self._tasks.extend([
                asyncio.create_task(self._health_monitor(), name="health_monitor"),
                asyncio.create_task(self._cleanup_monitor(), name="cleanup_monitor")
            ])
            
            self.logger.info("The Mona system started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            await self.shutdown()
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        self.logger.info("Shutting down The Mona system...")
        
        # Signal shutdown to all components
        self._shutdown_event.set()
        
        # Cancel background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Shutdown components in reverse order
        if self.game_engine:
            await self.game_engine.stop()
        
        if self.mqtt_client:
            await self.mqtt_client.disconnect()
        
        if self.audio_service:
            await self.audio_service.shutdown()
        
        self.logger.info("The Mona system shutdown complete")
    
    async def _health_monitor(self) -> None:
        """Monitor system health and log status periodically."""
        while not self._shutdown_event.is_set():
            try:
                # Check component health
                mqtt_ok = self.mqtt_client and self.mqtt_client.is_connected
                game_ok = self.game_engine and self.game_engine.is_running
                audio_ok = self.audio_service and await self.audio_service.is_connected()
                
                self.logger.debug(
                    f"Health check - MQTT: {mqtt_ok}, Game: {game_ok}, Audio: {audio_ok}"
                )
                
                await asyncio.sleep(30)  # Health check every 30s
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_monitor(self) -> None:
        """Monitor for cleanup tasks and resource management."""
        while not self._shutdown_event.is_set():
            try:
                # Trigger cleanup in components if needed
                if self.mqtt_client:
                    await self.mqtt_client.cleanup_stale_subscriptions()
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup monitor error: {e}")
                await asyncio.sleep(300)


# Global application instance for signal handlers
_app_instance: Optional[MonaApplication] = None


def setup_signal_handlers() -> None:
    """Setup graceful shutdown on SIGINT/SIGTERM."""
    
    def signal_handler(signum: int, frame) -> None:
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        logging.getLogger("mona.main").info(f"Received {signal_name}, initiating shutdown...")
        
        if _app_instance:
            # Create new event loop if needed (signal handlers run in main thread)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_app_instance.shutdown())
            except RuntimeError:
                # No running loop, create one
                asyncio.run(_app_instance.shutdown())
        
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main() -> None:
    """Main application entry point."""
    global _app_instance
    
    # Setup logging first
    setup_logging()
    logger = logging.getLogger("mona.main")
    
    # Setup signal handlers
    setup_signal_handlers()
    
    try:
        # Create and start application
        _app_instance = MonaApplication()
        await _app_instance.startup()
        
        # Keep running until shutdown
        await _app_instance._shutdown_event.wait()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if _app_instance:
            await _app_instance.shutdown()


if __name__ == "__main__":
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    if project_root.name == "the-mona":
        import os
        os.chdir(project_root)
    
    # Run the application
    asyncio.run(main())