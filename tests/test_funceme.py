import json
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import requests
from services import funceme as f


def payload(horario=None, valores=(30, 32, 28)):
    horario = horario or pd.Timestamp.now(tz=f.FUSO).isoformat()
    return {"data": {"list": [
        {"name": str(i), "series": [{"name": horario, "value": v}]}
        for i, v in zip((2, 3, 4), valores)
    ]}}


class TestFunceme(unittest.TestCase):
    def consulta(self, dados, status=200, chunks=None):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status_code = status
        response.iter_content.return_value = chunks if chunks is not None else [json.dumps(dados).encode()]
        return response

    def test_observacao_valida_e_transporte_restrito(self):
        response = self.consulta(payload())
        with patch.object(f.requests, 'get', return_value=response) as get:
            atual = f.obter_temperatura_atual()
        self.assertEqual(atual['temperatura_media'], 30)
        self.assertIsNotNone(atual['data_hora'].tzinfo)
        self.assertFalse(get.call_args.kwargs['allow_redirects'])
        self.assertEqual(get.call_args.kwargs['timeout'], (5, 10))
        self.assertTrue(get.call_args.kwargs['stream'])
        response.__exit__.assert_called_once()

    def test_sensores_numericos(self):
        dados = payload()
        for sensor in dados['data']['list']:
            sensor['name'] = int(sensor['name'])
        with patch.object(f, '_consultar', return_value=dados):
            self.assertEqual(f.obter_temperatura_atual()['temperatura_media'], 30)

    def test_timeout_sem_vazar_detalhes(self):
        with patch.object(f.requests, 'get', side_effect=requests.Timeout('segredo')):
            with self.assertRaises(f.ErroFunceme) as erro:
                f.obter_temperatura_atual()
            self.assertNotIn('segredo', str(erro.exception))

    def test_http_e_redirect(self):
        for status in (301, 302, 404, 429, 500):
            with self.subTest(status=status), patch.object(f.requests, 'get', return_value=self.consulta({}, status)):
                with self.assertRaises(f.ErroFunceme):
                    f.obter_temperatura_atual()

    def test_json_invalido(self):
        with patch.object(f.requests, 'get', return_value=self.consulta({}, chunks=[b'<html>erro</html>'])):
            with self.assertRaises(f.ErroFunceme):
                f.obter_temperatura_atual()

    def test_limite_bytes(self):
        with patch.object(f, 'MAX_BYTES', 10), patch.object(f.requests, 'get', return_value=self.consulta({}, chunks=[b'123456', b'123456'])):
            with self.assertRaises(f.ErroFunceme):
                f.obter_temperatura_atual()

    def test_prazo(self):
        with patch.object(f.time, 'monotonic', side_effect=[0, 21]), patch.object(f.requests, 'get', return_value=self.consulta(payload())):
            with self.assertRaises(f.ErroFunceme):
                f.obter_temperatura_atual()

    def test_estruturas_invalidas(self):
        for dados in (None, [], {}, {'data': None}, {'data': {'list': {}}}, {'data': {'list': [None]}}, {'data': {'list': []}}):
            with self.subTest(dados=dados), patch.object(f, '_consultar', return_value=dados):
                with self.assertRaises(f.ErroFunceme):
                    f.obter_temperatura_atual()

    def test_valores_invalidos_ou_incoerentes(self):
        for valor in (None, True, 'NaN', 'inf', -999, {}, 'abc', 70):
            with self.subTest(valor=valor), patch.object(f, '_consultar', return_value=payload(valores=(valor, 32, 28))):
                with self.assertRaises(f.ErroFunceme):
                    f.obter_temperatura_atual()
        with patch.object(f, '_consultar', return_value=payload(valores=(30, 28, 32))):
            with self.assertRaises(f.ErroFunceme):
                f.obter_temperatura_atual()

    def test_horarios_invalidos_antigos_e_futuros(self):
        agora = pd.Timestamp.now(tz=f.FUSO)
        for horario in ('NaT', 'invalido', '9999-01-01', (agora-pd.Timedelta(hours=4)).isoformat(), (agora+pd.Timedelta(hours=1)).isoformat()):
            with self.subTest(horario=horario), patch.object(f, '_consultar', return_value=payload(horario)):
                with self.assertRaises(f.ErroFunceme):
                    f.obter_temperatura_atual()

    def test_ultima_linha_incompleta_usa_anterior_completa(self):
        dados=payload((pd.Timestamp.now(tz=f.FUSO)-pd.Timedelta(hours=1)).isoformat())
        dados['data']['list'][0]['series'].append({'name': pd.Timestamp.now(tz=f.FUSO).isoformat(), 'value': 31})
        with patch.object(f, '_consultar', return_value=dados):
            self.assertEqual(f.obter_temperatura_atual()['temperatura_media'], 30)

    def test_duplicatas_conflitantes(self):
        dados=payload()
        serie=dados['data']['list'][0]['series']
        serie.append({**serie[0], 'value': 31})
        with patch.object(f, '_consultar', return_value=dados):
            with self.assertRaises(f.ErroFunceme):
                f.obter_temperatura_atual()

    def test_limite_registros(self):
        with patch.object(f, 'MAX_REGISTROS', 2), patch.object(f, '_consultar', return_value=payload()):
            with self.assertRaises(f.ErroFunceme):
                f.obter_temperatura_atual()

    def test_periodo_invalido_nao_acessa_rede(self):
        with patch.object(f.requests, 'get') as get:
            with self.assertRaises(ValueError):
                f.obter_dados_temperatura('https://localhost/')
            get.assert_not_called()
