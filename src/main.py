from machine import ADC, Pin
from time import ticks_ms, ticks_diff, sleep_ms


# ============================================================
# Configurações de hardware
# ============================================================

PINO_LDR = 34
PINO_BOTAO = 27

ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)

botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)


# ============================================================
# Configurações do sistema
# ============================================================

LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

TEMPO_MICRO_PARADA_MS = 5000
TEMPO_DEBOUNCE_MS = 50
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