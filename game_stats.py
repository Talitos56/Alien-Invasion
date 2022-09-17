class GameStats:
    """Armazena os dados estatísticos da Invasão Alienígena."""

    def __init__(self, ai_settings):
        """Inicializa os dados estatísticos."""

        self.ai_settings = ai_settings
        self.reset_stats()

        # Inicia a Invasão Alienígena em estado ativo
        self.game_active = False

        # Abrindo o arquivo que possui a pontuação máxima
        # A pontuação máxima jamais deverá ser reiniciada
        filename = 'high_score.txt'
        with open(filename) as file_object:
            self.high_score = int(file_object.read())

    def reset_stats(self):
        """Inicializa os dados estatísticos que podem mudar
            durante o jogo."""

        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 1
