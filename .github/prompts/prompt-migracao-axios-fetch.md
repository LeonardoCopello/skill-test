Prompt de migração do axios para o fetch

## Situação
A lib axios tem muitas vantagens. Ao mesmo tempo tem sofrido muitos ataques e deixado muitas vulnerabilidades.

## O que precisamos

Precisamos excluir completamente a lib axios e substituíla pelo fetch nativo javascript. Porém temos implementações de axios em muitos repositórios e gostaríamos de criar uma lib fetchService que tivesse as mesmas implementações do axios, como tratamentos de erros, interceptors e demais itens que facilitam o desenvolvimento.

## Local da lib

A lib deverá ser criada no repositório prodfin-pc-core-node-utils

## Local da implementação da lib substituindo o axios

A implementação da lib, substituindo o axios deverá ser no repositório prodfin-caas-installments-operation-portal
Temos um arquivo de auditoria do axios que é o auditoria.md localizado no repositório prodfin-caas-installments-operation-portal

## CRITÉRIOS DE ACEITE
Não póssuir outras libs transitivas, somente o fetch
A biblioteca deve ser o mais agnóstico possível
Os testes precisam passar
Validação do funcionamento



