# Checklist de Migração Axios → Fetch

Use esta checklist para acompanhar o progresso da migração em qualquer projeto NestJS.

## Pré-requisitos

- [ ] Verificar Node.js >= 18 (`node -v`)
- [ ] Identificar todos os arquivos afetados com `grep -rl "@nestjs/axios\|from 'axios'\|lastValueFrom" src/ --include="*.ts"`
- [ ] Criar `HttpFetchError` no diretório de erros compartilhados do projeto
- [ ] Exportar `HttpFetchError` no(s) barrel(s) `index.ts` correspondente(s)
- [ ] Criar `FetchService` (ver [fetch-service.md](./fetch-service.md))
- [ ] Criar `fetch.service.spec.ts` com testes unitários do `FetchService`
- [ ] Verificar versão do nock: `npm list nock` — se v13, testes unitários devem mockar `FetchService` diretamente

## Migração por Arquivo

Para cada serviço/adapter identificado na fase de mapeamento:

### Padrão GET simples (retorno null em erro)

- [ ] Substituir `HttpService` por `FetchService` no constructor
- [ ] Remover imports: `@nestjs/axios`, `axios`, `lastValueFrom`, `rxjs`
- [ ] Migrar chamada: `lastValueFrom(httpService.get(...))` → `await fetchService.get(...)`
- [ ] Migrar error handling: `axios.isAxiosError` → `HttpFetchError.isHttpFetchError`
- [ ] Atualizar campos de erro: `error.response.data/status` → `error.data/status`, `error.request.path` → `error.url`
- [ ] Atualizar testes unitários (mockar `FetchService` em vez de `HttpService`)

### Padrão POST com autenticação (lança exceção)

- [ ] Substituir `HttpService` por `FetchService` no constructor
- [ ] Remover imports: `@nestjs/axios`, `axios`, `lastValueFrom`, `rxjs`
- [ ] Migrar chamada: `lastValueFrom(httpService.post(...))` → `await fetchService.post(...)`
- [ ] Atualizar testes unitários

### Padrão OAuth / form-encoded (qs.stringify → URLSearchParams)

- [ ] Substituir `qs.stringify({...})` por `new URLSearchParams({...})`
- [ ] Remover `'Content-Type': 'application/x-www-form-urlencoded'` dos headers (automático no FetchService)
- [ ] Remover import de `qs`
- [ ] Atualizar testes unitários

### Padrão GET com headers e params de query string

- [ ] Verificar que `params` é passado como objeto (não como query string manual)
- [ ] Migrar chamada mantendo `{ headers, params }` na config
- [ ] Atualizar testes unitários

## Módulos

- [ ] Módulo central HTTP — Remover `HttpModule` do `@nestjs/axios`, adicionar `FetchService` como provider e export
- [ ] Módulos de domínio que importavam `HttpModule` diretamente — substituir pelo módulo HTTP do projeto
- [ ] Arquivo de configuração de testes (ex: `modules.config.ts`) — atualizar imports

## Fixtures e Mocks de Teste

- [ ] Substituir `AxiosResponse<T>` por `FetchResponse<T>` (importado do `FetchService`)
- [ ] Remover campos axios-específicos: `statusText` em fixtures (ou manter com valor real), `config`, `request`
- [ ] Adicionar `headers: new Headers()` onde necessário

## Cleanup

- [ ] `npm uninstall @nestjs/axios axios`
- [ ] Verificar se `qs` pode ser removido: `npm uninstall qs @types/qs`
- [ ] `npm run build` — zero erros de compilação
- [ ] `npm run test` — todos os testes passando
- [ ] `npm run test:integration` (se existir) — todos passando
- [ ] Grep por referências residuais:
  ```bash
  grep -r "axios\|@nestjs/axios\|HttpService\|lastValueFrom\|AxiosResponse\|AxiosError" src/ --include="*.ts"
  ```
  Resultado esperado: **zero resultados**
- [ ] Verificar `package-lock.json`: `grep -c '"axios"' package-lock.json` deve retornar `0`
- [ ] Verificar `package-lock.json` — axios não aparece
