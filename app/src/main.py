# Copyright (c) 2022 Robert Bosch GmbH and Microsoft Corporation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

# ------------------------------------------------------------------------------
import asyncio
import json
import logging
import signal

from vehicle import Vehicle, vehicle  # type: ignore
from velocitas_sdk.util.log import (  # type: ignore
    get_opentelemetry_log_factory,
    get_opentelemetry_log_format,
)
from velocitas_sdk.vdb.reply import DataPointReply
from velocitas_sdk.vehicle_app import VehicleApp, subscribe_topic

# ------------------------------------------------------------------------------
logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel("DEBUG")
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
APP = "sampleapp/"
GET_TOPIC = {
    "Speed": {
        "REQUEST": f"{APP}getSpeed/",
        "RESPONSE": f"{APP}getSpeed/response"
    },
    "AverageSpeed": {
        "REQUEST": f"{APP}getAverageSpeed/",
        "RESPONSE": f"{APP}getAverageSpeed/response",
    },
    "IsMoving": {
        "REQUEST": f"{APP}getIsMoving/",
        "RESPONSE": f"{APP}getIsMoving/response"
    },
}
DATABROKER_TOPIC = {
    "Speed": f"{APP}currentSpeed/",
    "AverageSpeed": f"{APP}currentAverageSpeed/",
    "IsMoving": f"{APP}currentIsMoving/",
}


# ------------------------------------------------------------------------------
class SampleApp(VehicleApp):
    # --------------------------------------------------------------------------
    def __init__(self, vehicle_client: Vehicle):
        super().__init__()
        self.Vehicle = vehicle_client

    async def on_start(self):
        await self.Vehicle.Speed.subscribe(self.on_change_speed)
        await self.Vehicle.AverageSpeed.subscribe(self.on_change_averagespeed)
        await self.Vehicle.IsMoving.subscribe(self.on_change_ismoving)

    # --------------------------------------------------------------------------
    async def on_change_speed(self, data: DataPointReply):
        subject = "Speed"
        value = data.get(self.Vehicle.Speed).value
        await self.publish_event(
            DATABROKER_TOPIC[subject],
            json.dumps({DATABROKER_TOPIC[subject]: value}),
        )

    async def on_change_averagespeed(self, data: DataPointReply):
        subject = "AverageSpeed"
        value = data.get(self.Vehicle.Speed).value
        await self.publish_event(
            DATABROKER_TOPIC[subject],
            json.dumps({DATABROKER_TOPIC[subject]: value}),
        )

    async def on_change_ismoving(self, data: DataPointReply):
        subject = "IsMoving"
        value = data.get(self.Vehicle.Speed).value
        await self.publish_event(
            DATABROKER_TOPIC[subject],
            json.dumps({DATABROKER_TOPIC[subject]: value}),
        )

    # --------------------------------------------------------------------------
    @subscribe_topic(GET_TOPIC["AverageSpeed"]["REQUEST"])
    async def on_get_average_speed_request_received(self, data: str) -> None:
        logger.debug(
            "PubSub event for the Topic: %s -> is received with the data: %s",
            GET_TOPIC["AverageSpeed"]["REQUEST"],
            data,
        )
        value = (await self.Vehicle.AverageSpeed.get()).value
        await self.publish_event(
            GET_TOPIC["AverageSpeed"]["Response"],
            json.dumps(
                {
                    "result": {
                        "status": 0,
                        "message": f"AverageSpeed = {value}",
                    },
                }
            ),
        )

    @subscribe_topic(GET_TOPIC["Speed"]["REQUEST"])
    async def on_get_speed_request_received(self, data: str) -> None:
        logger.debug(
            "PubSub event for the Topic: %s -> is received with the data: %s",
            GET_TOPIC["Speed"]["REQUEST"],
            data,
        )
        value = (await self.Vehicle.Speed.get()).value
        await self.publish_event(
            GET_TOPIC["Speed"]["Response"],
            json.dumps(
                {
                    "result": {
                        "status": 0,
                        "message": f"speed = {value}",
                    },
                }
            ),
        )
    
    @subscribe_topic(GET_TOPIC["IsMoving"]["REQUEST"])
    async def on_get_is_moving_request_received(self, data: str) -> None:
        logger.debug(
            "PubSub event for the Topic: %s -> is received with the data: %s",
            GET_TOPIC["IsMoving"]["REQUEST"],
            data,
        )
        value = (await self.Vehicle.IsMoving.get()).value
        await self.publish_event(
            GET_TOPIC["IsMoving"]["Response"],
            json.dumps(
                {
                    "result": {
                        "status": 0,
                        "message": f"IsMoving = {value}",
                    },
                }
            ),
        )


# ------------------------------------------------------------------------------
async def main():
    logger.info("Starting SampleApp...")
    vehicle_app = SampleApp(vehicle)
    await vehicle_app.run()


# ------------------------------------------------------------------------------
LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())
LOOP.close()
