"""
Configurações do modelo térmico urbano didático.

IMPORTANTE:
Os pesos abaixo não representam coeficientes experimentais medidos
em Baturité. Eles compõem um modelo simplificado para fins
educacionais, permitindo comparar diferentes cenários de cobertura
urbana.

As porcentagens das coberturas devem totalizar 100%.
"""

PESOS_TERMICOS = {
    "vegetacao": -0.35,
    "pavimento": 0.40,
    "edificacoes": 0.30,
    "solo_exposto": 0.15,
    "agua": -0.20,
}

# Limites adotados para evitar que o modelo didático produza
# anomalias térmicas exageradas.
DELTA_T_MIN = -2.0
DELTA_T_MAX = 3.0
