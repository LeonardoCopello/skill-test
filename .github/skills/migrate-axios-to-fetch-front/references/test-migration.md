# Migração de Testes: Axios → Fetch Nativo

## IMPORTANTE: Compatibilidade com nock

O `fetch` nativo do Node.js usa `undici` internamente — **não** o módulo `http`/`https` que o `axios` (e versoes antigas do `node-fetch`) usavam.

| Versão do nock | Intercepta fetch nativo? |
| -------------- | ------------------------ |
| nock v13       | **NÃO**                  |
| nock v14+      | **SIM** (via undici)     |

**Consequência prática:**

- Se o projeto usa **nock v13**: testes unitários precisam mockar o `FetchService` diretamente (abordagem recomendada neste guia)
- Se o projeto usa **nock v14+**: testes de integração com nock continuam funcionando sem alteração
- Para atualizar: `npm install --save-dev nock@latest`

**Verificar a versão do nock no projeto:**

```bash
npm list nock
```

---

## Testes Unitários (Jest) — Abordagem recomendada

Mockar o `FetchService` diretamente é mais rápido, isolado e não depende da versão do nock.

### Antes: Mock do HttpService via NestJS Testing

```typescript
import { HttpModule } from '@nestjs/axios';

const module = await Test.createTestingModule({
  imports: [HttpModule /* ou AppHttpModule */],
  providers: [ExemploHttpService],
}).compile();
```

### Depois: Mock do FetchService

```typescript
import { FetchService } from '<caminho-para-fetch-service>';

const module = await Test.createTestingModule({
  imports: [
    /* demais módulos necessários (Settings, Logging, Cache, etc.) */
  ],
  providers: [
    ExemploHttpService,
    {
      provide: FetchService,
      useValue: {
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn(),
        patch: jest.fn(),
        delete: jest.fn(),
      },
    },
  ],
}).compile();

const fetchService = module.get(FetchService);
```

### Mock de respostas bem-sucedidas

```typescript
jest.spyOn(fetchService, 'post').mockResolvedValue({
  data: mockCreateOrderResponseFixture,
  status: 200,
  headers: new Headers(),
});
```

### Mock de erros HTTP (substituindo AxiosError)

```typescript
import { HttpFetchError } from '../../../common/errors/http-fetch.error';

jest.spyOn(fetchService, 'post').mockRejectedValue(
  new HttpFetchError({
    message: 'Request failed with status 500: Internal Server Error',
    status: 500,
    statusText: 'Internal Server Error',
    data: { message: 'Error' },
    url: '/api/endpoint',
  }),
);
```

### Mock de erros de rede (timeout, DNS, etc.)

```typescript
jest.spyOn(fetchService, 'get').mockRejectedValue(new TypeError('fetch failed'));
```

---

### Assertions de Erro — Migração

### Antes (verificando AxiosError)

```typescript
expect(spyLogger).toHaveBeenCalledWith(
  expect.objectContaining({
    message: expect.stringContaining('ExemploHttpService'),
    data: { message: 'Bad Request' },
    status: 400,
    path: '/api/v1/algum-endpoint',
  }),
);
```

### Depois (verificando HttpFetchError)

```typescript
expect(spyLogger).toHaveBeenCalledWith(
  expect.objectContaining({
    message: expect.stringContaining('ExemploHttpService'),
    data: { message: 'Bad Request' },
    status: 400,
    url: expect.stringContaining('/api/v1/algum-endpoint'),
  }),
);
```

**Mudança**: campo `path` → `url`

---

## Testes do FetchService

Criar testes unitários para o `FetchService` junto ao arquivo de implementação (ex: `fetch.service.spec.ts`):

```typescript
import { FetchService } from './fetch.service';
import { HttpFetchError } from '<caminho-para-http-fetch-error>'; // ajustar caminho

describe('FetchService', () => {
  let service: FetchService;

  beforeEach(() => {
    service = new FetchService();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('get', () => {
    it('should return parsed JSON on success', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ id: 1 }),
      });

      const result = await service.get<{ id: number }>('https://api.example.com/data');
      expect(result.data).toEqual({ id: 1 });
      expect(result.status).toBe(200);
    });

    it('should throw HttpFetchError on non-ok response', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ message: 'Not found' }),
      });

      await expect(service.get('https://api.example.com/missing')).rejects.toThrow(HttpFetchError);
    });

    it('should append query params to URL', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({}),
      });

      await service.get('https://api.example.com/data', {
        params: { page: 1, limit: 10 },
      });

      expect(global.fetch).toHaveBeenCalledWith('https://api.example.com/data?page=1&limit=10', expect.any(Object));
    });
  });

  describe('post', () => {
    it('should send JSON body', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 201,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ created: true }),
      });

      await service.post('https://api.example.com/data', { name: 'test' });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/data',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'test' }),
        }),
      );
    });

    it('should send URLSearchParams body', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ token: 'abc' }),
      });

      const params = new URLSearchParams({ client_id: 'id', client_secret: 'secret' });
      await service.post('https://auth.example.com/token', params);

      expect(global.fetch).toHaveBeenCalledWith(
        'https://auth.example.com/token',
        expect.objectContaining({
          method: 'POST',
          body: params,
        }),
      );
    });
  });
});
```

---

## Checklist de Migração de Testes

- [ ] Atualizar `nock` para v14+ (`npm install --save-dev nock@latest`)
- [ ] Criar testes do `FetchService` (`fetch.service.spec.ts`)
- [ ] Substituir `HttpModule` por mock de `FetchService` nos testes unitários
- [ ] Substituir mocks que usam `AxiosError` por `HttpFetchError`
- [ ] Atualizar assertions: `path` → `url`, `response.data` → `data`
- [ ] Rodar `npm run test` — todos devem passar
- [ ] Rodar `npm run test:integration` — todos devem passar
- [ ] Grep por referências residuais: `grep -r "axios\|AxiosError\|HttpService\|@nestjs/axios" src/ test/`
