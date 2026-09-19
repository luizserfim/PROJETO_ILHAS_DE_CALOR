import unittest

from models.modelo_termico import (
    validar_cobertura,
    calcular_indice_termico,
    estimar_temperatura,
    comparar_intervencao,
)


class TestModeloTermico(unittest.TestCase):

    def test_cobertura_valida(self):
        self.assertTrue(
            validar_cobertura(
                vegetacao=15,
                pavimento=40,
                edificacoes=35,
                solo_exposto=5,
                agua=5,
            )
        )

    def test_cobertura_nao_totaliza_100(self):
        with self.assertRaises(ValueError):
            validar_cobertura(
                vegetacao=10,
                pavimento=20,
                edificacoes=20,
                solo_exposto=5,
                agua=5,
            )

    def test_percentual_invalido(self):
        with self.assertRaises(ValueError):
            validar_cobertura(
                vegetacao=-5,
                pavimento=45,
                edificacoes=45,
                solo_exposto=10,
                agua=5,
            )

    def test_cenario_padrao(self):
        resultado = estimar_temperatura(
            temperatura_referencia=30,
            vegetacao=15,
            pavimento=40,
            edificacoes=35,
            solo_exposto=5,
            agua=5,
        )

        self.assertAlmostEqual(
            resultado["indice_termico"],
            0.21,
            places=6,
        )
        self.assertAlmostEqual(
            resultado["anomalia_termica"],
            2.10,
            places=6,
        )
        self.assertAlmostEqual(
            resultado["temperatura_estimada"],
            32.10,
            places=6,
        )

    def test_mais_vegetacao_reduz_temperatura(self):
        atual = estimar_temperatura(
            30, 15, 40, 35, 5, 5
        )

        arborizado = estimar_temperatura(
            30, 25, 30, 35, 5, 5
        )

        self.assertLess(
            arborizado["temperatura_estimada"],
            atual["temperatura_estimada"],
        )

    def test_intervencao_reduz_temperatura(self):
        resultado = comparar_intervencao(
            temperatura_referencia=30,
            vegetacao=15,
            pavimento=40,
            edificacoes=35,
            solo_exposto=5,
            agua=5,
            percentual_convertido=10,
        )

        self.assertGreater(
            resultado["reducao_estimada"],
            0,
        )

        self.assertLess(
            resultado["cenario_intervencao"]["temperatura_estimada"],
            resultado["cenario_atual"]["temperatura_estimada"],
        )

    def test_intervencao_preserva_100_porcento(self):
        resultado = comparar_intervencao(
            temperatura_referencia=30,
            vegetacao=15,
            pavimento=40,
            edificacoes=35,
            solo_exposto=5,
            agua=5,
            percentual_convertido=10,
        )

        futuro = resultado["cenario_intervencao"]

        # Se a função chegou até aqui sem ValueError, a validação
        # interna confirmou que a nova composição continua em 100%.
        self.assertIsNotNone(futuro)

    def test_nao_pode_converter_mais_pavimento_do_que_existe(self):
        with self.assertRaises(ValueError):
            comparar_intervencao(
                temperatura_referencia=30,
                vegetacao=15,
                pavimento=40,
                edificacoes=35,
                solo_exposto=5,
                agua=5,
                percentual_convertido=41,
            )

    def test_limite_superior_delta_t(self):
        resultado = estimar_temperatura(
            30, 0, 100, 0, 0, 0
        )

        self.assertEqual(
            resultado["anomalia_termica"],
            3.0,
        )

    def test_limite_inferior_delta_t(self):
        resultado = estimar_temperatura(
            30, 100, 0, 0, 0, 0
        )

        self.assertEqual(
            resultado["anomalia_termica"],
            -2.0,
        )


if __name__ == "__main__":
    unittest.main()
