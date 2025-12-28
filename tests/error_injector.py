# tests/error_injector.py - 🛡️ CYBERSECURITY & FAULT ROBUSTNESS SUITE
# Simulates attacks and hardware faults to ensure safe recovery

import can
import time
import random
import struct


class FaultInjector:
    def __init__(self):
        try:
            # MUST MATCH gateway + HMI
            self.bus = can.interface.Bus(channel='virtual_ch', interface='virtual')
            print("🔗 Connected to CAN (virtual_ch)")
        except Exception as e:
            print(f"❌ CAN INIT FAILURE: {e}")

    def inject_dos_attack(self, duration=4):
        """Floods the bus with highest priority 0x000"""
        print(f"\n🚨 DoS Attack: Flooding for {duration}s...")
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                msg = can.Message(arbitration_id=0x000, data=[0xFF] * 8, is_extended_id=False)
                self.bus.send(msg)
                count += 1
            except:
                break
        print(f"🛑 DoS Stopped — {count} malicious frames injected.")

    def inject_bit_flipping(self, frames=10):
        """Corrupts steering sensor bytes"""
        print(f"\n👾 Injecting {frames} corrupted frames...")
        for i in range(frames):
            corruption = random.randint(200, 255)
            data = bytearray([corruption, corruption, 0, 0, 0, 0, 0, 0])
            msg = can.Message(arbitration_id=0x100, data=data, is_extended_id=False)
            self.bus.send(msg)
            print(f"⚡ Bit-flip frame #{i+1}: {data.hex()}")
            time.sleep(0.15)

    def inject_heartbeat_loss(self, delay=4):
        """Pretend gateway stops heartbeat"""
        print(f"\n💔 Simulating lost heartbeat for {delay}s...")
        print("🧩 EXPECTED: HMI must switch to ● FAULT mode (RED)")
        time.sleep(delay)

    def inject_heartbeat_corruption(self):
        """Send invalid heartbeat packets"""
        print("\n🤖 Corrupting Heartbeat Packet...")
        for i in range(5):
            fake_data = struct.pack('<B H B 4x', 0x00, 0xFFFF, 255)
            msg = can.Message(arbitration_id=0x7FF, data=fake_data, is_extended_id=False)
            self.bus.send(msg)
            print(f"❌ Invalid heartbeat injected ({i+1}/5)")
            time.sleep(0.3)

    def run_all_faults(self):
        print("\n===== 🔥 AUTOMOTIVE FAULT TEST SUITE START 🔥 =====")
        self.inject_bit_flipping()
        self.inject_heartbeat_loss()
        self.inject_heartbeat_corruption()
        self.inject_dos_attack()
        print("===== 🛡️ FAULT TEST SUITE COMPLETE 🛡️ =====")


if __name__ == "__main__":
    injector = FaultInjector()
    injector.run_all_faults()
