---
name: migrate-axios-to-fetch
description: "Migrar integrações HTTP de axios/@nestjs/axios para fetch nativo do Node.js. Use quando: remover axios, substituir HttpService por fetch, migrar chamadas HTTP, eliminar dependência axios, supply chain security, migrar para native fetch."
applyTo: "**/*.service.ts,**/*.adapter.ts,**/*.module.ts"
argument-hint: 'Nome do serviço/adapter a migrar ou "all" para migrar todos'
---

# Migração Axios → Fetch Nativo (Node.js)

## Contexto

O pacote `axios` sofreu um ataque de supply chain em Março/2026 (CVE via phantom dependency `plain-crypto-js`).
Esta skill guia a migração completa de `@nestjs/axios` + `axios` para o `fetch` nativo do Node.js **em qualquer aplicação NestJS**.

**Requisito mínimo**: Node.js >= 18 (fetch nativo disponível sem flags experimentais).

## Quando Usar

- Migrar qualquer serviço/adapter que use `HttpService` do `@nestjs/axios`
- Remover dependência do pacote `axios`
- Substituir `axios.isAxiosError()` por tratamento de erro nativo

## Como Identificar Arquivos Afetados

Antes de iniciar, mapeie todos os arquivos que precisam ser alterados:

```bash
# Todos os arquivos TypeScript que importam axios ou @nestjs/axios
grep -rl "@nestjs/axios\|from 'axios'\|lastValueFrom" src/ --include="*.ts"

# Módulos que importam HttpModule
grep -rl "HttpModule" src/ --include="*.ts"

# Fixtures/mocks com AxiosResponse
grep -rl "AxiosResponse\|AxiosError" src/ --include="*.ts"
```

Organize os resultados nas categorias:

| Categoria           | Padrão a buscar                               | Prioridade |
| ------------------- | --------------------------------------------- | ---------- |
| Serviços HTTP       | `HttpService` no constructor                  | Alta       |
| Adapters HTTP       | `HttpService` no constructor                  | Alta       |
| Módulo central HTTP | `HttpModule` + providers de serviços HTTP     | Alta       |
| Módulos de domínio  | `HttpModule` importado diretamente            | Média      |
| Testes unitários    | `HttpModule`, `HttpService`, `AxiosResponse`  | Alta       |
| Fixtures de teste   | `AxiosResponse`, `AxiosError`                 | Alta       |
| `package.json`      | `@nestjs/axios`, `axios`, `qs` (se aplicável) | Alta       |

## Procedimento de Migração

Siga as etapas na ordem para garantir que cada passo seja validável com testes.

### Etapa 1: Criar helper de erro HTTP customizado

Substituir `axios.isAxiosError()` por um helper próprio. Criar onde fizer sentido no projeto (ex: `src/common/errors/` ou `src/shared/errors/`):

```typescript
// <caminho-de-erros>/http-fetch.error.ts
export class HttpFetchError extends Error {
  public readonly status: number;
  public readonly statusText: string;
  public readonly data: unknown;
  public readonly url: string;

  constructor(params: {
    message: string;
    status: number;
    statusText: string;
    data: unknown;
    url: string;
  }) {
    super(params.message);
    this.name = "HttpFetchError";
    this.status = params.status;
    this.statusText = params.statusText;
    this.data = params.data;
    this.url = params.url;
  }

  static isHttpFetchError(error: unknown): error is HttpFetchError {
    return error instanceof HttpFetchError;
  }
}
```

Se o projeto usar barrel exports, exportar no arquivo `index.ts` correspondente.

### Etapa 2: Criar wrapper NestJS para fetch

Substituir o `HttpService` do `@nestjs/axios` por um serviço próprio injetável via NestJS DI. Consulte o guia completo em [./references/fetch-service.md](./references/fetch-service.md).

O serviço deve:

- Ser `@Injectable()` e registrado em um módulo NestJS
- Expor métodos `get<T>()`, `post<T>()`, `put<T>()`, `patch<T>()`, `delete<T>()`
- Retornar `Promise<{ data: T; status: number; headers: Headers }>` (mantendo a interface similar à do axios)
- Lançar `HttpFetchError` quando `response.ok === false`
- Aceitar configuração de headers, params (query string), body e timeout via `AbortSignal.timeout()`

### Etapa 3: Registrar FetchService no módulo HTTP

Localize o módulo NestJS responsável pelos serviços HTTP (geralmente chamado `HttpModule`, `AppHttpModule` ou similar). Substitua o `HttpModule` do `@nestjs/axios` por `FetchService`:

```typescript
// Exemplo genérico de módulo HTTP
import { Module } from "@nestjs/common";
import { FetchService } from "./services/fetch/fetch.service";
import { ExemploHttpService } from "./services/exemplo/exemplo.service";

@Module({
  // Remover: imports: [HttpModule] — do @nestjs/axios
  providers: [FetchService, ExemploHttpService /* ... outros serviços HTTP */],
  exports: [FetchService, ExemploHttpService /* ... outros serviços HTTP */],
})
export class AppHttpModule {}
```

**IMPORTANTE**: Remover o import de `HttpModule` do `@nestjs/axios` de todos os módulos onde ele estava registrado. Verificar módulos de domínio (ex: `StoreModule`, `OrderModule`) que importavam `HttpModule` diretamente.

### Etapa 4: Migrar cada serviço/adapter HTTP

Para cada arquivo afetado, aplique as transformações descritas em [./references/migration-patterns.md](./references/migration-patterns.md).

**Ordem recomendada** (do mais simples ao mais complexo):

1. Serviços com apenas GET simples e retorno `null` em erro
2. Serviços com POST de JSON e lançamento de exceção
3. Serviços com fluxo de autenticação + cache de token
4. Adapters com `URLSearchParams` (OAuth/form-encoded) e `params` de query string

**Para cada serviço/adapter:**

1. Substituir `HttpService` por `FetchService` no constructor
2. Remover imports de `@nestjs/axios`, `axios`, `lastValueFrom`, `rxjs`
3. Substituir `lastValueFrom(this.httpService.method(...))` por `await this.fetchService.method(...)`
4. Substituir `axios.isAxiosError(error)` por `HttpFetchError.isHttpFetchError(error)`
5. Adaptar campos de erro: `error.response.data` → `error.data`, `error.response.status` → `error.status`, `error.request.path` → `error.url`

### Etapa 5: Migrar os testes

Consulte [./references/test-migration.md](./references/test-migration.md) para detalhes.

> **IMPORTANTE**: `nock` v13 **NÃO intercepta** o fetch nativo (que usa `undici` internamente). Apenas o nock v14+ suporta intercepção de fetch. Para testes unitários, mockar o `FetchService` diretamente via `jest.spyOn()` é a abordagem recomendada e mais rápida.

- Atualizar mocks unitários para injetar `FetchService` no lugar de `HttpService`
- Ajustar assertions que verificavam `axios.isAxiosError`, `error.response.data`, `error.request.path`
- Se o projeto usa nock para testes de integração, atualizar para nock v14+: `npm install --save-dev nock@latest`

### Etapa 6: Atualizar módulos de domínio

Nos módulos de domínio que importavam `HttpModule` do `@nestjs/axios` diretamente, substituir pelo módulo HTTP do projeto (que agora exporta `FetchService`):

```typescript
// Antes
import { HttpModule } from '@nestjs/axios';
@Module({ imports: [HttpModule, ...] })

// Depois
import { AppHttpModule } from '../http/http.module'; // caminho varia por projeto
@Module({ imports: [AppHttpModule, ...] })
```

Se o projeto usa um arquivo de configuração de módulos de teste (ex: `modules.config.ts`), atualizar também.

### Etapa 7: Remover dependências do package.json

```bash
npm uninstall @nestjs/axios axios
```

Verificar se `qs` ainda é necessário. Se o único uso era para serializar corpos de requisição form-encoded, substituir por `new URLSearchParams(params)` nativo e remover `qs` também:

```bash
npm uninstall qs @types/qs
```

### Etapa 8: Validação final

1. `npm run build` (ou equivalente) — garantir zero erros de compilação
2. `npm run test` — garantir todos os testes passando
3. `npm run test:integration` (se existir) — garantir integrações funcionando
4. Grep por referências residuais:
   ```bash
   grep -r "axios\|@nestjs/axios\|HttpService\|lastValueFrom\|AxiosResponse\|AxiosError" src/ --include="*.ts"
   ```
5. Verificar `package-lock.json` — confirmar que `axios` não aparece como dependência instalada

## Regras

- **Nunca** adicionar `axios` de volta como dependência
- **Sempre** usar `AbortSignal.timeout()` para timeout em chamadas fetch
- **Sempre** verificar `response.ok` antes de processar a resposta
- **Sempre** lançar `HttpFetchError` em respostas não-ok para manter consistência no error handling
- **Nunca** usar bibliotecas HTTP de terceiros (got, node-fetch, ky, superagent) — usar apenas fetch nativo
- Manter a assinatura de retorno dos serviços idêntica para não quebrar consumidores
