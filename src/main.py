from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff


# ---------------------------------------------------------
# Configuração de hardware
# ---------------------------------------------------------

PINO_LDR = 34
PINO_BOTAO_RESET = 27

ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)

# Botão ligado entre o GPIO 27 e o GND:
# solto = 1
# pressionado = 0
botao_reset = Pin(
    PINO_BOTAO_RESET,
    Pin.IN,
    Pin.PULL_UP
)


# ---------------------------------------------------------
# Configurações do sistema
# ---------------------------------------------------------

LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

TEMPO_MICRO_PARADA_MS = 5000
TEMPO_DEBOUNCE_MS = 50
INTERVALO_LOOP_MS = 20


# ---------------------------------------------------------
# Estados do sensor
# ---------------------------------------------------------

ESTADO_SENSOR_LIVRE = 0
ESTADO_SENSOR_BLOQUEADO = 1


class MonitorProducao:
    """
    Controla a contagem de peças, a identificação de microparadas
    e o reset manual do turno.
    """

    def __init__(self, sensor_ldr, botao):
        self.sensor_ldr = sensor_ldr
        self.botao = botao

        self.contador_pecas = 0

        self.estado_sensor = ESTADO_SENSOR_LIVRE
        self.tempo_inicio_bloqueio = 0
        self.alerta_emitido = False

        self.botao_foi_pressionado = False
        self.tempo_pressao_botao = 0

    def iniciar_bloqueio(self, agora):
        """
        Registra a transição do sensor livre para bloqueado.
        """

        self.estado_sensor = ESTADO_SENSOR_BLOQUEADO
        self.tempo_inicio_bloqueio = agora
        self.alerta_emitido = False

    def verificar_micro_parada(self, agora):
        """
        Emite um único alerta quando o bloqueio permanece
        por cinco segundos ou mais.
        """

        tempo_bloqueado = ticks_diff(
            agora,
            self.tempo_inicio_bloqueio
        )

        if (
            tempo_bloqueado >= TEMPO_MICRO_PARADA_MS
            and not self.alerta_emitido
        ):
            print("Alerta: Micro-parada detectada!")
            self.alerta_emitido = True

    def registrar_peca(self):
        """
        Conta uma peça quando o sensor retorna ao estado livre.
        """

        self.contador_pecas += 1

        self.estado_sensor = ESTADO_SENSOR_LIVRE
        self.tempo_inicio_bloqueio = 0
        self.alerta_emitido = False

        print(
            "Peca detectada! Total:",
            self.contador_pecas
        )

    def processar_sensor(self, agora):
        """
        Interpreta a leitura do LDR utilizando dois limites.

        Os dois limites criam uma histerese:
        - acima de LIMITE_BLOQUEADO: sensor bloqueado;
        - abaixo de LIMITE_LIVRE: sensor livre.

        Leituras entre os limites preservam o estado anterior,
        evitando oscilações e falsas contagens.
        """

        valor_ldr = self.sensor_ldr.read()

        if valor_ldr > LIMITE_BLOQUEADO:
            if self.estado_sensor == ESTADO_SENSOR_LIVRE:
                self.iniciar_bloqueio(agora)

            self.verificar_micro_parada(agora)

        elif (
            valor_ldr < LIMITE_LIVRE
            and self.estado_sensor == ESTADO_SENSOR_BLOQUEADO
        ):
            self.registrar_peca()

    def resetar_turno(self):
        """
        Zera a contagem e restaura todos os estados internos.
        """

        self.contador_pecas = 0

        self.estado_sensor = ESTADO_SENSOR_LIVRE
        self.tempo_inicio_bloqueio = 0
        self.alerta_emitido = False

        print(
            "Turno resetado com sucesso. Contadores zerados."
        )

    def processar_botao(self, agora):
        """
        Identifica um ciclo completo de pressionar e soltar o botão.

        O tempo mínimo evita resets causados por ruído elétrico
        ou por alterações muito rápidas no sinal.
        """

        estado_botao = self.botao.value()

        if (
            estado_botao == 0
            and not self.botao_foi_pressionado
        ):
            self.botao_foi_pressionado = True
            self.tempo_pressao_botao = agora

        elif (
            estado_botao == 1
            and self.botao_foi_pressionado
        ):
            tempo_pressionado = ticks_diff(
                agora,
                self.tempo_pressao_botao
            )

            if tempo_pressionado >= TEMPO_DEBOUNCE_MS:
                self.resetar_turno()

            self.botao_foi_pressionado = False
            self.tempo_pressao_botao = 0

    def executar(self):
        """
        Executa continuamente o monitoramento da produção.
        """

        print("Contador de Producao Inicializado")

        while True:
            agora = ticks_ms()

            self.processar_sensor(agora)
            self.processar_botao(agora)

            sleep_ms(INTERVALO_LOOP_MS)


# ---------------------------------------------------------
# Inicialização
# ---------------------------------------------------------

monitor = MonitorProducao(
    sensor_ldr=ldr,
    botao=botao_reset
)

monitor.executar()