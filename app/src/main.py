# - Imports
import asyncio
import json
import logging
import signal

from velocitas_sdk.util.log import (  # type: ignore
    get_opentelemetry_log_factory,
    get_opentelemetry_log_format,
)
from velocitas_sdk.vdb.reply import DataPointReply
from velocitas_sdk.vehicle_app import VehicleApp, subscribe_topic, subscribe_data_points
from vehicle import Vehicle, vehicle  # type: ignore

# - Logging
logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel("INFO")
logger = logging.getLogger(__name__)


# - App Class
class CrashDetectUIApp(VehicleApp):
    APP = "crash_detector/"
    SPEED = {
        "ID": "Speed",
        "FULLID": "Vehicle.Speed",
        "DATABROKER": f"{APP}currentSpeed/",
        "REQUEST": f"{APP}getSpeed/",
        "RESPONSE": f"{APP}getSpeed/response",
    }

    def __init__(self, vehicle_client: Vehicle):
        super().__init__()
        self.Vehicle = vehicle_client
        self.SPEED_OBJ = self.Vehicle.Speed

    async def on_start(self):
        print("CrashDetectUIApp on_started launched")

    @subscribe_data_points(SPEED["FULLID"])
    async def speed_subscription(self, data: DataPointReply):
        topic = self.SPEED["REQUEST"]
        data = {self.SPEED["ID"]: data.get(self.SPEED_OBJ).value}  # type: ignore
        await self.publish_mqtt_event(topic, json.dumps(data))

    @subscribe_topic(SPEED["REQUEST"])
    async def on_speed_request_received(self, data: str) -> None:
        data = json.loads(data)
        logger.debug(
            "PubSub event for the Topic: %s -> is received with the data: %s",
            self.SPEED["REQUEST"],
            data,
        )
        topic = self.SPEED["RESPONSE"]
        value = {"requetID": data["requestId"], "result": {}}  # type: ignore
        await self.publish_event(
            topic,
            json.dumps({"result": {"status": 0, "message": f"{topic} = {value}"}}),
        )


# - Main
async def main():
    """
    Main function
    """
    logger.info("Starting Car Crash Detect UI Application ...")
    app = CrashDetectUIApp(vehicle)
    await app.run()


# - Loop
LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())
LOOP.close()
