from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff


# ---------------------------------------------------------
# Configuração dos pinos
# ---------------------------------------------------------

PINO_LDR = 34
PINO_BOTAO_RESET = 27


# Sensor de luminosidade
ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)


# Botão ligado ao GND.
# Solto = 1
# Pressionado = 0
botao_reset = Pin(
    PINO_BOTAO_RESET,
    Pin.IN,
    Pin.PULL_UP
)


# ---------------------------------------------------------
# Configurações do sistema
# ---------------------------------------------------------

# Valores medidos no Wokwi:
# 800 lux -> aproximadamente 773 no ADC
# 50 lux  -> aproximadamente 2531 no ADC
LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

# Cinco segundos para considerar micro-parada
TEMPO_MICRO_PARADA_MS = 5000

# Tempo para evitar múltiplas leituras do botão
TEMPO_DEBOUNCE_MS = 50


# ---------------------------------------------------------
# Variáveis do sistema
# ---------------------------------------------------------

contador = 0

sensor_bloqueado = False
tempo_inicio_bloqueio = 0
alerta_emitido = False

estado_anterior_botao = 1
tempo_ultima_mudanca_botao = 0


print("Contador de Producao Inicializado")


# ---------------------------------------------------------
# Loop principal
# ---------------------------------------------------------

while True:
    agora = ticks_ms()
    valor_ldr = ldr.read()
    estado_botao = botao_reset.value()

    # -----------------------------------------------------
    # Cenários 1 e 2: sensor de luminosidade
    # -----------------------------------------------------

    # A peça entrou e bloqueou a luz
    if valor_ldr > LIMITE_BLOQUEADO:

        # Executa apenas quando o bloqueio começa
        if not sensor_bloqueado:
            sensor_bloqueado = True
            tempo_inicio_bloqueio = agora
            alerta_emitido = False

        tempo_bloqueado = ticks_diff(
            agora,
            tempo_inicio_bloqueio
        )

        # Cenário 2: peça parada por cinco segundos
        if (
            tempo_bloqueado >= TEMPO_MICRO_PARADA_MS
            and not alerta_emitido
        ):
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    # Cenário 1: a peça saiu e a luz voltou
    elif valor_ldr < LIMITE_LIVRE and sensor_bloqueado:
        contador += 1

        sensor_bloqueado = False
        tempo_inicio_bloqueio = 0
        alerta_emitido = False

        print("Peca detectada! Total:", contador)

    # -----------------------------------------------------
    # Cenário 3: botão de reset
    # -----------------------------------------------------

    # Detecta mudança no estado do botão
    if estado_botao != estado_anterior_botao:
        tempo_ultima_mudanca_botao = agora
        estado_anterior_botao = estado_botao

    # Confirma que o botão permaneceu pressionado
    if (
        estado_botao == 0
        and ticks_diff(
            agora,
            tempo_ultima_mudanca_botao
        ) >= TEMPO_DEBOUNCE_MS
    ):
        contador = 0

        sensor_bloqueado = False
        tempo_inicio_bloqueio = 0
        alerta_emitido = False

        print(
            "Turno resetado com sucesso. "
            "Contadores zerados."
        )

        # Aguarda o botão ser solto para não repetir o reset
        while botao_reset.value() == 0:
            sleep_ms(10)

        estado_anterior_botao = 1
        tempo_ultima_mudanca_botao = ticks_ms()

    sleep_ms(20)