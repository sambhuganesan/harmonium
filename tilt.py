import time
import math
import asyncio
from winrt.windows.devices.sensors import Inclinometer, Accelerometer, Gyrometer

async def read_sensors():   
    accel = Accelerometer.get_default()
    if accel:
        while True:
            while True:
                reading = accel.get_current_reading()
                x = reading.acceleration_x
                y = reading.acceleration_y
                z = reading.acceleration_z

                if z > 0:
                    pitch1 = math.atan2(math.sqrt(x*x + z*z), y) * (180 / math.pi) - 180
                else: 
                    pitch1 = 180 - math.atan2(math.sqrt(x*x + z*z), y) * (180 / math.pi)

                print(f"Screen tilt angle: {pitch1:.2f}°")
                await asyncio.sleep(0.2)

asyncio.run(read_sensors())