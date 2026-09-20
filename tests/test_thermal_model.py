import random
import unittest
from models.modelo_termico import (
    validar_cobertura, calcular_indice_termico, calcular_anomalia_termica,
    estimar_temperatura, comparar_intervencao,
)


class TestRobustezModelo(unittest.TestCase):
    def test_numeros_invalidos(self):
        for valor in (float('nan'), float('inf'), -float('inf'), True, None, '30', [], 10**1000):
            with self.subTest(tipo=type(valor).__name__):
                for funcao, args in (
                    (estimar_temperatura, (valor, 15, 40, 35, 5, 5)),
                    (calcular_anomalia_termica, (valor,)),
                    (calcular_indice_termico, (valor, 40, 35, 5, 5)),
                    (comparar_intervencao, (30, 15, 40, 35, 5, 5, valor)),
                ):
                    with self.assertRaises(ValueError):
                        funcao(*args)

    def test_tolerancia_nao_pode_burlar_validacao(self):
        for tolerancia in (float('nan'), float('inf'), -1, 100, True):
            with self.assertRaises(ValueError):
                validar_cobertura(15, 40, 35, 5, 5, tolerancia)

    def test_pesos_invalidos(self):
        for pesos in ({}, [], {'vegetacao': float('nan')}):
            with self.assertRaises(ValueError):
                calcular_indice_termico(15, 40, 35, 5, 5, pesos)

    def test_intervencao_invalida(self):
        for tipo in ('inexistente', [], None):
            with self.assertRaises(ValueError):
                comparar_intervencao(30, 15, 40, 35, 5, 5, 10, tipo)

    def test_propriedades_em_500_cenarios(self):
        gerador = random.Random(42)
        origens = {'Pavimento → Vegetação': 1, 'Solo exposto → Vegetação': 3, 'Edificações → Vegetação': 2}
        for _ in range(500):
            cortes = sorted([0, 100] + [gerador.randrange(101) for _ in range(4)])
            coberturas = [b-a for a,b in zip(cortes, cortes[1:])]
            for tipo, origem in origens.items():
                convertido = gerador.uniform(0, coberturas[origem])
                resultado = comparar_intervencao(30, *coberturas, convertido, tipo)
                novas = resultado['coberturas_intervencao']
                self.assertAlmostEqual(sum(novas.values()), 100)
                self.assertTrue(all(0 <= v <= 100 for v in novas.values()))
                self.assertGreaterEqual(resultado['reducao_estimada'], -1e-12)
                self.assertTrue(-2 <= resultado['cenario_intervencao']['anomalia_termica'] <= 3)
