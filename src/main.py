from machine import ADC, Pin
from time import sleep_ms

# Configuração do LDR
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

contador = 0
sensor_bloqueado = False

print("Contador de Producao Inicializado")

while True:
    valor = ldr.read()

    # Peça bloqueando a luz
    if valor > LIMITE_BLOQUEADO:
        sensor_bloqueado = True

    # Peça saiu e a luz voltou
    elif valor < LIMITE_LIVRE and sensor_bloqueado:
        contador += 1
        sensor_bloqueado = False
        print(f"Peca detectada! Total: {contador}")

    sleep_ms(20)