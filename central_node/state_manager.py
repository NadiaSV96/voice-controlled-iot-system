class StateManager:
    def __init__(self):
        self.mode_actif = 'manual'

    def update_mode(self, new_mode):
        """ Mettre à jour l'état du mode """
        self.mode_actif = new_mode


