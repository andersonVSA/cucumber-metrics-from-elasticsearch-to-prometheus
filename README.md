## Metricas de testes end-to-end

A idéia deste projeto, é gerar métricas de testes de regressão executados em um pipeline de C.I.

Após executar um teste com o `cucumber` e expor o resultado dos testes como `.json`, atualizamos o json com informações relevantes do build executado no `Jenkins`, e então, enviamos para o `elasticsearch`.

Por sua vez, usamos o `prometheus-es-exporter` para extrair métricas dos documentos criados no elasticsearch.

## Como executar fora do jenkins:

$`python3 ./pipeline-shared-librares/utils/regressive_tests/update_json.py`


Caso ocorrer algum erro na execução, provavelmente é por falta de exportar alguma das variáveis de exemplo que estão em:

`devops-tools/pipeline-shared-librares/utils/regressive_tests/test/.env`


Caso de algum erro por falta no arquivo json_base que ele usa pra fazer o parse, só criar o arquivo reclamado com base no arquivo em:

`devops-tools/pipeline-shared-librares/utils/regressive_tests/test/fixture/test_failed.json`

## Como rodar os testes unitários:

acessar pasta raiz do projeto e executar o arquivo de testes:

$`python3 pipeline-shared-librares/utils/regressive_tests/test/update_json_test.py`

