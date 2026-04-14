# Padrões de Migração: Axios → Fetch Nativo

## Mapeamento de Imports

### Antes (axios)

```typescript
import { HttpService } from '@nestjs/axios';
import axios from 'axios';
import { lastValueFrom } from 'rxjs';
```

### Depois (fetch)

```typescript
import { FetchService } from '<caminho-para-fetch-service>';
import { HttpFetchError } from '<caminho-para-http-fetch-error>';
```

> Ajuste os caminhos de import conforme a localização dos arquivos no projeto.

---

## Padrão 1: GET simples com retorno null em erro

Serviços que fazem um GET e retornam `null` em caso de erro (ao invés de lançar exceção).

### Antes (axios)

```typescript
@Injectable()
export class ExemploGetService {
  constructor(
    private readonly httpService: HttpService,
    private readonly logger: WinstonLogger,
  ) {}

  async getResource(resourceId: string): Promise<ExemploResponse | null> {
    try {
      const response = await lastValueFrom(this.httpService.get<ExemploResponse>(`${this.baseUrl}/v1/resources/${resourceId}`));
      return response.data;
    } catch (error) {
      const errorData = axios.isAxiosError(error)
        ? {
            message: `ExemploGetService::getResource - Reason: ${error.message}`,
            data: error.response.data,
            status: error.response.status,
            path: error.request.path,
            resourceId,
          }
        : {
            message: `ExemploGetService::getResource - Reason: ${error.message}`,
            resourceId,
            error,
          };
      this.logger.error(errorData);
      return null;
    }
  }
}
```

### Depois (fetch nativo)

```typescript
@Injectable()
export class ExemploGetService {
  constructor(
    private readonly fetchService: FetchService,
    private readonly logger: WinstonLogger,
  ) {}

  async getResource(resourceId: string): Promise<ExemploResponse | null> {
    try {
      const response = await this.fetchService.get<ExemploResponse>(`${this.baseUrl}/v1/resources/${resourceId}`);
      return response.data;
    } catch (error) {
      const errorData = HttpFetchError.isHttpFetchError(error)
        ? {
            message: `ExemploGetService::getResource - Reason: ${error.message}`,
            data: error.data,
            status: error.status,
            url: error.url,
            resourceId,
          }
        : {
            message: `ExemploGetService::getResource - Reason: ${error.message}`,
            resourceId,
            error,
          };
      this.logger.error(errorData);
      return null;
    }
  }
}
```

**Mudanças-chave:**

- `HttpService` → `FetchService`
- `lastValueFrom(this.httpService.get(...))` → `await this.fetchService.get(...)`
- `axios.isAxiosError(error)` → `HttpFetchError.isHttpFetchError(error)`
- `error.response.data` → `error.data`
- `error.response.status` → `error.status`
- `error.request.path` → `error.url`

---

## Padrão 2: POST com JSON body e lançamento de exceção

Serviços que fazem POST e lançam `InternalServerErrorException` em erro (ex: autenticação).

### Antes (axios)

```typescript
async authenticate(): Promise<string> {
  const cached = await this.cacheManager.get<string>(TOKEN_CACHE_KEY);
  if (cached) return cached;

  try {
    const response = await lastValueFrom(
      this.httpService.post<TokenResponse>(`${this.baseUrl}/api/v1/auth/login`, {
        clientId: this.clientId,
        clientSecret: this.clientSecret,
      }),
    );
    const { accessToken, expiresIn } = response.data;
    this.cacheManager.set(TOKEN_CACHE_KEY, accessToken, expiresIn);
    return accessToken;
  } catch (error) {
    throw new InternalServerErrorException(
      `Unable to get token. Reason: ${error.message}`,
    );
  }
}
```

### Depois (fetch nativo)

```typescript
async authenticate(): Promise<string> {
  const cached = await this.cacheManager.get<string>(TOKEN_CACHE_KEY);
  if (cached) return cached;

  try {
    const response = await this.fetchService.post<TokenResponse>(
      `${this.baseUrl}/api/v1/auth/login`,
      { clientId: this.clientId, clientSecret: this.clientSecret },
    );
    const { accessToken, expiresIn } = response.data;
    this.cacheManager.set(TOKEN_CACHE_KEY, accessToken, expiresIn);
    return accessToken;
  } catch (error) {
    throw new InternalServerErrorException(
      `Unable to get token. Reason: ${error.message}`,
    );
  }
}
```

**Mudanças-chave:**

- `lastValueFrom(this.httpService.post(...))` → `await this.fetchService.post(...)`
- `response.data` permanece igual (o FetchService mantém a mesma estrutura)

---

## Padrão 3: POST com URLSearchParams (OAuth / form-encoded)

Serviços que enviam corpo no formato `application/x-www-form-urlencoded` (ex: OAuth2 client credentials).

### Antes (axios + qs)

```typescript
import qs from 'qs';

const data = qs.stringify({
  client_id: this.clientId,
  client_secret: this.clientSecret,
  grant_type: 'client_credentials',
});

const response = await lastValueFrom(
  this.httpService.post<TokenResponse>(`${this.authBaseUrl}/oauth/token`, data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'x-correlation-id': correlationId,
    },
  }),
);
```

### Depois (fetch nativo — sem qs)

```typescript
// URLSearchParams é nativo — não precisa de qs
const data = new URLSearchParams({
  client_id: this.clientId,
  client_secret: this.clientSecret,
  grant_type: 'client_credentials',
});

const response = await this.fetchService.post<TokenResponse>(`${this.authBaseUrl}/oauth/token`, data, {
  headers: {
    'x-correlation-id': correlationId,
    // Content-Type 'application/x-www-form-urlencoded' é definido automaticamente
  },
});
```

**Mudanças-chave:**

- `qs.stringify({...})` → `new URLSearchParams({...})` (nativo)
- Remover import de `qs` e dependências `qs`/`@types/qs`
- Remover `'Content-Type': 'application/x-www-form-urlencoded'` (automático no `FetchService`)

---

## Padrão 4: POST com URLSearchParams via propriedades de classe

Quando o corpo form-encoded é construído a partir de dados já disponíveis como `URLSearchParams`.

### Antes (axios)

```typescript
private async authenticateRequest(): Promise<string> {
  const { requestBody, requestHeaders, requestURL } = this.authenticateRequestProps();

  try {
    const response = await lastValueFrom(
      this.httpService.post<AuthResponse>(requestURL, requestBody, {
        headers: requestHeaders,
      }),
    );
    const { access_token, expires_in } = response.data;
    await this.cacheManager.set(...);
    return access_token;
  } catch (error) {
    throw new InternalServerErrorException(...);
  }
}
```

### Depois (fetch nativo)

```typescript
private async authenticateRequest(): Promise<string> {
  const { requestBody, requestHeaders, requestURL } = this.authenticateRequestProps();

  try {
    const response = await this.fetchService.post<AuthenticationResponse>(
      requestURL,
      requestBody, // URLSearchParams é suportado nativamente pelo FetchService
      { headers: requestHeaders },
    );
    const { access_token, expires_in } = response.data;
    await this.cacheManager.set(...);
    return access_token;
  } catch (error) {
    throw new InternalServerErrorException(...);
  }
}
```

**Nota**: `URLSearchParams` como body é suportado nativamente pelo `FetchService` — o Content-Type é definido automaticamente.

---

## Padrão 5: GET com query params e headers customizados

Serviços que passam parâmetros de query string e headers via configuração.

### Antes (axios)

```typescript
const response = await lastValueFrom(
  this.httpService.get<SearchResponse[]>(requestURL, {
    headers: { Authorization: `Bearer ${token}` },
    params: { city: 'SP', limit: 10 },
  }),
);
return response.data;
```

### Depois (fetch nativo)

```typescript
const response = await this.fetchService.get<SearchResponse[]>(requestURL, {
  headers: { Authorization: `Bearer ${token}` },
  params: { city: 'SP', limit: 10 },
});
return response.data;
```

> O `FetchService` serializa `params` como query string automaticamente usando `URLSearchParams`.

---

## Mapeamento de Campos de Erro

| Axios (antes)               | Fetch (depois)                           |
| --------------------------- | ---------------------------------------- |
| `axios.isAxiosError(error)` | `HttpFetchError.isHttpFetchError(error)` |
| `error.response.data`       | `error.data`                             |
| `error.response.status`     | `error.status`                           |
| `error.response.statusText` | `error.statusText`                       |
| `error.request.path`        | `error.url`                              |
| `error.message`             | `error.message` (mantém)                 |

## Mapeamento de Métodos

| Axios/HttpService (antes)                                          | FetchService (depois)                                      |
| ------------------------------------------------------------------ | ---------------------------------------------------------- |
| `lastValueFrom(this.httpService.get<T>(url))`                      | `await this.fetchService.get<T>(url)`                      |
| `lastValueFrom(this.httpService.get<T>(url, { headers, params }))` | `await this.fetchService.get<T>(url, { headers, params })` |
| `lastValueFrom(this.httpService.post<T>(url, body))`               | `await this.fetchService.post<T>(url, body)`               |
| `lastValueFrom(this.httpService.post<T>(url, body, { headers }))`  | `await this.fetchService.post<T>(url, body, { headers })`  |
| `response.data`                                                    | `response.data` (mantém)                                   |
| `response.status`                                                  | `response.status` (mantém)                                 |
| `response.headers`                                                 | `response.headers` (Headers nativo)                        |
