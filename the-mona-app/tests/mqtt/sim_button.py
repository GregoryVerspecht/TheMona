# tools/sim_button.py
import time, json, argparse
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--id", default="btn100")

args = parser.parse_args()

cid = f"sim-{args.id}"
c = mqtt.Client(client_id=cid)
c.connect(args.host, args.port, 30)

prefix = "the-mona"
def pub(topic, obj, retain=False, qos=1):
    c.publish(topic, json.dumps(obj), qos=qos, retain=retain)

# retained status
pub(f"{prefix}/buttons/{args.id}/status", {
    "online": True, "fw": "1.0.0", "capabilities": ["rgb","press"], "mac": "AA:BB"
}, retain=True)

# heartbeat + press loop
for i in range(50):
    ts = int(time.time())
    pub(f"{prefix}/buttons/{args.id}/heartbeat", {"ts": ts}, retain=False, qos=0)
    time.sleep(1)
    pub(f"{prefix}/buttons/{args.id}/events", {"type":"press","ts": ts+1}, retain=False, qos=1)
    time.sleep(2)

c.disconnect()
print("Done.")
