# FetchService — Wrapper NestJS para fetch nativo

## Implementação do FetchService

Criar em um diretório adequado ao projeto (ex: `src/http/services/fetch/fetch.service.ts`, `src/shared/http/fetch.service.ts`). Ajuste os caminhos de import conforme a estrutura do projeto.

```typescript
// Exemplo: src/http/services/fetch/fetch.service.ts
// Ajuste o caminho de import do HttpFetchError conforme a estrutura do seu projeto
import { Injectable } from '@nestjs/common';
import { HttpFetchError } from '../../errors/http-fetch.error'; // ajustar caminho

export interface FetchRequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, string | number>;
  timeout?: number;
}

export interface FetchResponse<T> {
  data: T;
  status: number;
  headers: Headers;
}

@Injectable()
export class FetchService {
  private buildUrl(url: string, params?: Record<string, string | number>): string {
    if (!params || Object.keys(params).length === 0) return url;

    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      searchParams.append(key, String(value));
    }

    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}${searchParams.toString()}`;
  }

  private async request<T>(url: string, options: RequestInit & { params?: Record<string, string | number>; timeout?: number }): Promise<FetchResponse<T>> {
    const { params, timeout = 30_000, ...fetchOptions } = options;
    const finalUrl = this.buildUrl(url, params);

    const response = await fetch(finalUrl, {
      ...fetchOptions,
      signal: AbortSignal.timeout(timeout),
    });

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      throw new HttpFetchError({
        message: `Request failed with status ${response.status}: ${response.statusText}`,
        status: response.status,
        statusText: response.statusText,
        data,
        url: finalUrl,
      });
    }

    return { data: data as T, status: response.status, headers: response.headers };
  }

  async get<T>(url: string, config?: FetchRequestConfig): Promise<FetchResponse<T>> {
    return this.request<T>(url, {
      method: 'GET',
      headers: config?.headers,
      params: config?.params,
      timeout: config?.timeout,
    });
  }

  async post<T>(url: string, body?: unknown, config?: FetchRequestConfig): Promise<FetchResponse<T>> {
    const headers = { ...config?.headers };
    let serializedBody: BodyInit | undefined;

    if (body instanceof URLSearchParams) {
      serializedBody = body;
      headers['Content-Type'] ??= 'application/x-www-form-urlencoded';
    } else if (body !== undefined && body !== null) {
      serializedBody = JSON.stringify(body);
      headers['Content-Type'] ??= 'application/json';
    }

    return this.request<T>(url, {
      method: 'POST',
      headers,
      body: serializedBody,
      params: config?.params,
      timeout: config?.timeout,
    });
  }

  async put<T>(url: string, body?: unknown, config?: FetchRequestConfig): Promise<FetchResponse<T>> {
    const headers = { ...config?.headers };
    let serializedBody: BodyInit | undefined;

    if (body instanceof URLSearchParams) {
      serializedBody = body;
      headers['Content-Type'] ??= 'application/x-www-form-urlencoded';
    } else if (body !== undefined && body !== null) {
      serializedBody = JSON.stringify(body);
      headers['Content-Type'] ??= 'application/json';
    }

    return this.request<T>(url, {
      method: 'PUT',
      headers,
      body: serializedBody,
      params: config?.params,
      timeout: config?.timeout,
    });
  }

  async patch<T>(url: string, body?: unknown, config?: FetchRequestConfig): Promise<FetchResponse<T>> {
    const headers = { ...config?.headers };
    let serializedBody: BodyInit | undefined;

    if (body instanceof URLSearchParams) {
      serializedBody = body;
      headers['Content-Type'] ??= 'application/x-www-form-urlencoded';
    } else if (body !== undefined && body !== null) {
      serializedBody = JSON.stringify(body);
      headers['Content-Type'] ??= 'application/json';
    }

    return this.request<T>(url, {
      method: 'PATCH',
      headers,
      body: serializedBody,
      params: config?.params,
      timeout: config?.timeout,
    });
  }

  async delete<T>(url: string, config?: FetchRequestConfig): Promise<FetchResponse<T>> {
    return this.request<T>(url, {
      method: 'DELETE',
      headers: config?.headers,
      params: config?.params,
      timeout: config?.timeout,
    });
  }
}
```

## Por que um wrapper e não fetch direto?

1. **Injeção de dependência** — permite mockar em testes unitários via NestJS DI
2. **Consistência de interface** — `{ data, status, headers }` familiar para quem vinha do axios
3. **Error handling centralizado** — `HttpFetchError` é lançado automaticamente em respostas não-ok
4. **Timeout padrão** — via `AbortSignal.timeout()`, evita requests pendurados
5. **Serialização automática** — JSON ou URLSearchParams detectados automaticamente

## Registro no Módulo

Adicionar `FetchService` como provider no `AppHttpModule` e exportá-lo:

```typescript
@Module({
  imports: [SettingsModule, CacheModule.register(), LoggingModule],
  providers: [FetchService /* ... demais services */],
  exports: [FetchService /* ... demais services */],
})
export class AppHttpModule {}
```

Para módulos que importam `HttpModule` diretamente (como `StoreModule`), substituir por `FetchService` como provider local ou importar `AppHttpModule`.
