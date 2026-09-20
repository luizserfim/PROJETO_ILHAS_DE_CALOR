import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest
from services.funceme import ErroFunceme

APP = str(Path(__file__).resolve().parents[1] / 'main.py')


class TestInterface(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        self.mock = patch('services.funceme.obter_temperatura_atual', side_effect=ErroFunceme('offline'))
        self.consulta = self.mock.start()
        self.addCleanup(self.mock.stop)
        self.addCleanup(st.cache_data.clear)

    def abrir(self):
        app = AppTest.from_file(APP, default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_modo_manual_e_cache_de_falha(self):
        app = self.abrir()
        self.assertEqual(app.number_input[0].value, 30)
        app.number_input[0].set_value(35).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, '35.0 °C')
        self.assertEqual(self.consulta.call_count, 1)

    def test_cobertura_invalida_impede_salvar(self):
        app=self.abrir()
        app.slider(key='vegetacao').set_value(20).run()
        salvar=next(b for b in app.button if b.label == '💾 Salvar')
        self.assertTrue(salvar.disabled)
        self.assertEqual(len(app.exception), 0)

    def test_sem_area_disponivel(self):
        app=self.abrir()
        for key, valor in {'vegetacao':100, 'pavimento':0, 'edificacoes':0, 'solo_exposto':0, 'agua':0}.items():
            app.slider(key=key).set_value(valor)
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('Não há área' in aviso.value for aviso in app.info))

    def test_nome_com_markup_permanece_texto_e_nova_analise_preserva_cenario(self):
        app=self.abrir()
        nome='<script>alert(1)</script> ![x](https://invalid.test/a)'
        app.text_input(key='nome_regiao').set_value(nome).run()
        next(b for b in app.button if b.label == '💾 Salvar').click().run()
        self.assertEqual(app.session_state['cenarios_salvos'][0]['regiao'], nome)
        self.assertTrue(any(nome in t.value for t in app.text))
        self.assertFalse(any(nome in m.value for m in app.markdown))
        next(b for b in app.button if b.label == '➕ Nova análise').click().run()
        self.assertEqual(app.text_input(key='nome_regiao').value, '')
        self.assertEqual(len(app.session_state['cenarios_salvos']), 1)
        self.assertEqual(len(app.exception), 0)

    def test_limite_e_limpeza_de_cenarios(self):
        app=self.abrir()
        app.session_state['cenarios_salvos']=[dict(regiao='x', vegetacao=15,pavimento=40,edificacoes=35,solo_exposto=5,agua=5) for _ in range(50)]
        app.run()
        self.assertTrue(next(b for b in app.button if b.label == '💾 Salvar').disabled)
        next(b for b in app.button if b.label == 'Limpar cenários salvos').click().run()
        self.assertEqual(app.session_state['cenarios_salvos'], [])
        self.assertEqual(len(app.exception), 0)

    def test_dados_automaticos(self):
        self.consulta.side_effect=None
        self.consulta.return_value=dict(temperatura_media=30, temperatura_maxima=32, temperatura_minima=28, estacao='Baturité - APA', data_hora=pd.Timestamp.now(tz='America/Fortaleza'))
        app=self.abrir()
        self.assertEqual(len(app.number_input), 0)
        self.assertTrue(any('FUNCEME — dados disponíveis' == s.value for s in app.success))
