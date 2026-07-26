from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff


# ---------------------------------------------------------
# Configuração dos pinos
# ---------------------------------------------------------

PINO_LDR = 34
PINO_BOTAO_RESET = 27

ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)

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
# Estados do sistema
# ---------------------------------------------------------

contador = 0

sensor_bloqueado = False
tempo_inicio_bloqueio = 0
alerta_emitido = False

botao_foi_pressionado = False
tempo_pressao_botao = 0


# ---------------------------------------------------------
# Funções
# ---------------------------------------------------------

def iniciar_bloqueio(agora):
    """Registra o início da passagem ou bloqueio do sensor."""
    global sensor_bloqueado
    global tempo_inicio_bloqueio
    global alerta_emitido

    sensor_bloqueado = True
    tempo_inicio_bloqueio = agora
    alerta_emitido = False


def verificar_micro_parada(agora):
    """Emite um único alerta após cinco segundos de bloqueio."""
    global alerta_emitido

    tempo_bloqueado = ticks_diff(
        agora,
        tempo_inicio_bloqueio
    )

    if (
        tempo_bloqueado >= TEMPO_MICRO_PARADA_MS
        and not alerta_emitido
    ):
        print("Alerta: Micro-parada detectada!")
        alerta_emitido = True


def registrar_peca():
    """Registra uma peça quando o sensor volta ao estado livre."""
    global contador
    global sensor_bloqueado
    global tempo_inicio_bloqueio
    global alerta_emitido

    contador += 1

    sensor_bloqueado = False
    tempo_inicio_bloqueio = 0
    alerta_emitido = False

    print("Peca detectada! Total:", contador)


def verificar_sensor(valor_ldr, agora):
    """
    Controla o sensor utilizando histerese.

    Acima de LIMITE_BLOQUEADO:
        considera o sensor bloqueado.

    Abaixo de LIMITE_LIVRE:
        considera o sensor liberado.

    Entre os limites:
        mantém o estado anterior para evitar oscilações.
    """

    if valor_ldr > LIMITE_BLOQUEADO:

        if not sensor_bloqueado:
            iniciar_bloqueio(agora)

        verificar_micro_parada(agora)

    elif valor_ldr < LIMITE_LIVRE and sensor_bloqueado:
        registrar_peca()


def resetar_turno():
    """Zera o contador e restaura os estados do sistema."""
    global contador
    global sensor_bloqueado
    global tempo_inicio_bloqueio
    global alerta_emitido

    contador = 0

    sensor_bloqueado = False
    tempo_inicio_bloqueio = 0
    alerta_emitido = False

    print("Turno resetado com sucesso. Contadores zerados.")


def verificar_botao(estado_botao, agora):
    """Executa o reset somente após uma pressão válida do botão."""
    global botao_foi_pressionado
    global tempo_pressao_botao

    if estado_botao == 0 and not botao_foi_pressionado:
        botao_foi_pressionado = True
        tempo_pressao_botao = agora

    elif estado_botao == 1 and botao_foi_pressionado:

        tempo_pressionado = ticks_diff(
            agora,
            tempo_pressao_botao
        )

        if tempo_pressionado >= TEMPO_DEBOUNCE_MS:
            resetar_turno()

        botao_foi_pressionado = False


# ---------------------------------------------------------
# Inicialização
# ---------------------------------------------------------

print("Contador de Producao Inicializado")


# ---------------------------------------------------------
# Loop principal
# ---------------------------------------------------------

while True:
    agora = ticks_ms()

    valor_ldr = ldr.read()
    estado_botao = botao_reset.value()

    verificar_sensor(valor_ldr, agora)
    verificar_botao(estado_botao, agora)

    sleep_ms(INTERVALO_LOOP_MS)