from machine import ADC, Pin
<<<<<<< HEAD
from time import ticks_ms, ticks_diff, sleep_ms


# ============================================================
# Configurações de hardware
# ============================================================

PINO_LDR = 34
PINO_BOTAO = 27
=======
from time import sleep_ms, ticks_ms, ticks_diff


# ---------------------------------------------------------
# Configuração de hardware
# ---------------------------------------------------------

PINO_LDR = 34
PINO_BOTAO_RESET = 27
>>>>>>> master

ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)

<<<<<<< HEAD
botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)


# ============================================================
# Configurações do sistema
# ============================================================
=======
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
>>>>>>> master

LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

TEMPO_MICRO_PARADA_MS = 5000
TEMPO_DEBOUNCE_MS = 50
<<<<<<< HEAD
INTERVALO_LEITURA_MS = 20


# ============================================================
# Estado do sistema
# ============================================================

total_pecas = 0

sensor_bloqueado = False
tempo_inicio_bloqueio = 0
alerta_emitido = False

ultima_leitura_botao = botao.value()
estado_botao_estavel = ultima_leitura_botao
tempo_ultima_mudanca_botao = ticks_ms()


# ============================================================
# Funções relacionadas ao sensor
# ============================================================

def iniciar_bloqueio_sensor(tempo_atual):
    """
    Registra o momento em que uma peça bloqueia o sensor.
    """

    global sensor_bloqueado
    global tempo_inicio_bloqueio
    global alerta_emitido

    sensor_bloqueado = True
    tempo_inicio_bloqueio = tempo_atual
    alerta_emitido = False


def registrar_peca():
    """
    Incrementa o contador quando a peça libera o sensor.
    """

    global total_pecas
    global sensor_bloqueado
    global alerta_emitido

    total_pecas += 1
    sensor_bloqueado = False
    alerta_emitido = False

    print("Peca detectada! Total:", total_pecas)


def verificar_sensor(tempo_atual):
    """
    Aplica histerese para identificar o bloqueio e a liberação
    do sensor sem gerar contagens duplicadas.
    """

    leitura = ldr.read()

    if not sensor_bloqueado and leitura >= LIMITE_BLOQUEADO:
        iniciar_bloqueio_sensor(tempo_atual)

    elif sensor_bloqueado and leitura <= LIMITE_LIVRE:
        registrar_peca()


# ============================================================
# Funções relacionadas à micro-parada
# ============================================================

def verificar_micro_parada(tempo_atual):
    """
    Emite apenas um alerta quando o sensor permanece bloqueado
    por tempo superior ao limite configurado.
    """

    global alerta_emitido

    if not sensor_bloqueado or alerta_emitido:
        return

    tempo_bloqueado = ticks_diff(
        tempo_atual,
        tempo_inicio_bloqueio
    )

    if tempo_bloqueado >= TEMPO_MICRO_PARADA_MS:
        print("Alerta: Micro-parada detectada!")
        alerta_emitido = True


# ============================================================
# Funções relacionadas ao reset
# ============================================================

def resetar_turno():
    """
    Zera os contadores e restaura o estado inicial do sistema.
    """

    global total_pecas
    global sensor_bloqueado
    global tempo_inicio_bloqueio
    global alerta_emitido

    total_pecas = 0
    sensor_bloqueado = False
    tempo_inicio_bloqueio = 0
    alerta_emitido = False

    print("Turno resetado com sucesso. Contadores zerados.")


def verificar_botao_reset(tempo_atual):
    """
    Executa debounce por estabilização de estado.

    O botão só é considerado pressionado quando a leitura
    permanece estável durante o tempo definido.
    """

    global ultima_leitura_botao
    global estado_botao_estavel
    global tempo_ultima_mudanca_botao

    leitura_atual = botao.value()

    if leitura_atual != ultima_leitura_botao:
        ultima_leitura_botao = leitura_atual
        tempo_ultima_mudanca_botao = tempo_atual

    tempo_estavel = ticks_diff(
        tempo_atual,
        tempo_ultima_mudanca_botao
    )

    if (
        tempo_estavel >= TEMPO_DEBOUNCE_MS
        and leitura_atual != estado_botao_estavel
    ):
        estado_botao_estavel = leitura_atual

        # Pin.PULL_UP: valor 0 significa botão pressionado.
        if estado_botao_estavel == 0:
            resetar_turno()


# ============================================================
# Programa principal
# ============================================================

print("Contador de Producao Inicializado")

while True:
    agora = ticks_ms()

    verificar_sensor(agora)
    verificar_micro_parada(agora)
    verificar_botao_reset(agora)

    sleep_ms(INTERVALO_LEITURA_MS)
=======
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
>>>>>>> master
