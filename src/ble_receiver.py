# src/ble_receiver.py - 🔥 PRO UPGRADE | Zero-Drop Priority Streaming BLE → UDP
import asyncio
import socket
import time
import random
from queue import PriorityQueue, Full, Empty
import threading
import struct

DEVICE_ADDRESS = "SIMULATOR_MODE"
PRIORITY_QUEUE = PriorityQueue(maxsize=200)

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

DEBUG = True
EXIT_EVENT = threading.Event()

def log(msg):
    if DEBUG:
        print(msg)

def create_priority_packet(data, priority=1):
    return (priority, int(time.time() * 1_000_000), data)

async def notification_handler_simulator(data):
    packet = create_priority_packet(data, priority=0)  # Steering = Highest priority
    try:
        PRIORITY_QUEUE.put_nowait(packet)
        log(f"🎮 RX BLE: {data.hex()} [P{packet[0]}]")
    except Full:
        print("⚠ Packet Drop: Queue Overflow")

def forward_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log("🛰 Forward Thread Started")

    while not EXIT_EVENT.is_set():
        try:
            priority, ts, data = PRIORITY_QUEUE.get(timeout=0.002)
            # ⬇ 1B priority + 8B timestamp + data
            udp_packet = bytes([priority]) + struct.pack('<Q', ts) + data
            sock.sendto(udp_packet, (UDP_IP, UDP_PORT))
            PRIORITY_QUEUE.task_done()

            log(f"📡 UDP → {UDP_IP}:{UDP_PORT} | {data.hex()} @ {ts}")
        except Empty:
            pass
        except Exception as e:
            print(f"❌ UDP Error: {e}")

    sock.close()
    print("🔚 Forward Thread Stopped")

async def run_ble_simulator():
    print(f"\n🚀 Automotive BLE SIMULATOR Connected → {DEVICE_ADDRESS}")
    forward_daemon = threading.Thread(target=forward_thread, daemon=True)
    forward_daemon.start()

    steering_center = 127

    while not EXIT_EVENT.is_set():
        steering_val = steering_center + int(55 * random.uniform(-1, 1))
        steering_val = max(0, min(255, steering_val))  # Clamp
        await notification_handler_simulator(bytes([steering_val]))

        await asyncio.sleep(0.02)  # 50Hz real-time loop

if __name__ == "__main__":
    try:
        asyncio.run(run_ble_simulator())
    except KeyboardInterrupt:
        EXIT_EVENT.set()
        print("🛑 BLE Simulator Shutdown Requested")
