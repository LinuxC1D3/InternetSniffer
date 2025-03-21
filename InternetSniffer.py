import psutil
from collections import defaultdict
import os
import time

def monitor_connections(last_ip_count):
    # Sammlung der IP-Adressen, deren Verbindungen, zugehörige Programme und Ports
    ip_count = defaultdict(lambda: {'count': 0, 'programs': set(), 'ports': []})

    # Alle Verbindungen auflisten
    connections = psutil.net_connections(kind='inet')

    # Durch alle Verbindungen iterieren
    for conn in connections:
        remote_ip = conn.raddr.ip if conn.raddr else None
        local_port = conn.laddr.port if conn.laddr else None
        remote_port = conn.raddr.port if conn.raddr else None

        # Wenn eine Remote-IP vorhanden ist und sie nicht 127.0.0.1 ist, zähle die Verbindung
        if remote_ip and remote_ip != "127.0.0.1":
            # Die Prozess-ID (PID) der Verbindung abrufen
            pid = conn.pid
            if pid:
                try:
                    # Der Prozessname anhand der PID
                    process = psutil.Process(pid)
                    program_name = process.name()
                except psutil.NoSuchProcess:
                    program_name = "Unbekannt"

                # Die IP, Ports und das Programm zu der IP hinzufügen
                ip_count[remote_ip]['count'] += 1
                ip_count[remote_ip]['programs'].add(program_name)
                ip_count[remote_ip]['ports'].append((local_port, remote_port))

    # Vergleiche die aktuellen IPs mit den vorherigen, um Änderungen zu erkennen
    if ip_count != last_ip_count:
        # Terminalansicht löschen (damit es übersichtlich bleibt)
        os.system('cls' if os.name == 'nt' else 'clear')

        # Kopfzeile anzeigen
        print(f"{'IP-Adresse':<20} {'Verbindungen':<12} {'Programme':<50} {'Ports (Lokal->Remote)'}")
        print("-" * 100)

        # Sortiere die IP-Adressen und gebe sie aus
        for ip, data in sorted(ip_count.items(), key=lambda item: item[1]['count'], reverse=True):
            programs = ', '.join(data['programs'])
            ports = ', '.join([f"{local}->{remote}" for local, remote in data['ports']])
            
            # Formatiere die Ausgabe so, dass sie übersichtlicher wird
            print(f"{ip:<20} {data['count']:<12} {programs:<50} {ports}")

    return ip_count

def main():
    last_ip_count = defaultdict(lambda: {'count': 0, 'programs': set(), 'ports': []})

    while True:
        last_ip_count = monitor_connections(last_ip_count)
        time.sleep(1)  # Eine Sekunde warten, bevor die Anzeige aktualisiert wird

if __name__ == "__main__":
    main()