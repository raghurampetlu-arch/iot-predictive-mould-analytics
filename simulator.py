import time
import json
import random
import datetime
from azure.iot.device import IoTHubDeviceClient

CONNECTION_STRING = "HostName=hub-mould-analytics-raghu-iot.azure-devices.net;DeviceId=simulated_housing_sensor_01;SharedAccessKey=/xXWO0prfDRq7ryaXsGyiHRKVDKvj3nEWWcBYm6Vbng="

def generate_telemetry(device_id, step):
    base_temp = 19.0
    base_humidity = 55.0
    
    # Inject dynamic environmental anomaly to trigger the ML alerts
    if step > 20:
        temperature = base_temp - random.uniform(2.0, 4.0)
        humidity = base_humidity + random.uniform(20.0, 30.0)
    else:
        temperature = base_temp + random.uniform(-1.5, 1.5)
        humidity = base_humidity + random.uniform(-5.0, 5.0)

    # Magnus-Tetens framework for dynamic dew point approximation
    gamma = ((17.27 * temperature) / (237.7 + temperature)) + (humidity / 100.0)
    dew_point = (237.7 * gamma) / (17.27 - gamma)
    
    mould_risk_score = 100 if (humidity > 70.0 and (temperature - dew_point) < 3.0) else 0

    return {
        "device_id": device_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "dew_point": round(dew_point, 2),
        "mould_risk_score": mould_risk_score
    }


def main():
    print("Starting simulated UK Housing IoT Sensor Device...")
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    
    step = 0
    try:
        while True:
            step += 1
            data = generate_telemetry("simulated_housing_sensor_01", step)
            message_json = json.dumps(data)
            print(f"Sending telemetry packet: {message_json}")
            client.send_message(message_json)
            time.sleep(5)  # Sends a new reading to your Azure hub every 5 seconds
    except KeyboardInterrupt:
        print("Simulator stopped manually.")
    finally:
        client.shutdown()

if __name__ == "__main__":
    main()
