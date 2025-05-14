from central_node.coordinator import CentralNode

def main():
    central_node = CentralNode()
    try:
       while True:
        central_node.start()
    except KeyboardInterrupt:
        print("\n[MAIN] Arrêt demandé par l'utilisateur (Ctrl+C)")
        central_node.stop()
        print("[MAIN] Système arrêté proprement.")

if __name__ == "__main__":
    main()
