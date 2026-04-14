---
name: migrate-axios-to-fetch-front
description: 'Migrar integrações HTTP de axios para fetch nativo em micro frontends React/Next.js. Use quando: remover axios, migrar interceptors, migrar serviços HTTP para fetch, eliminar dependência axios, supply chain security, modernizar requisições HTTP em React.'
applyTo: '**/*.service.ts,**/*.config.ts,**/*.hook.ts,**/api.config.ts'
argument-hint: 'Nome do serviço/hook a migrar ou "all" para migrar todos'
---

# Migração Axios → Fetch Nativo (React/Next.js Micro Frontends)

## Contexto

O pacote `axios` sofreu um ataque de supply chain em Março/2026 (CVE via phantom dependency `plain-crypto-js`).
Esta skill guia a migração completa de `axios` para o `fetch` nativo do navegador **em micro frontends React/Next.js**.

Esta skill é otimizada para projetos que usam:
- React 18+
- TanStack Query (React Query) v5+
- TypeScript
- Module Federation / Micro frontends
- MSW (Mock Service Worker) para testes

**Boas Práticas**: Segue as recomendações do [Vercel React Best Practices](https://vercel.com/docs/optimization/react) para performance, bundle size e client-side data fetching.

## Quando Usar

- Migrar instâncias de `axios.create()` e interceptors para fetch wrappers
- Remover dependência do pacote `axios`
- Migrar serviços HTTP (`*.service.ts`) que usam axios
- Migrar hooks customizados que chamam axios diretamente (anti-pattern)
- Substituir `axios.isAxiosError()` por tratamento de erro nativo
- Atualizar testes de MSW e mocks do jest

## Como Identificar Arquivos Afetados

Antes de iniciar, mapeie todos os arquivos que precisam ser alterados:

```bash
# Arquivos que importam axios
grep -rl "from 'axios'\|import axios" src/ --include="*.ts" --include="*.tsx"

# Configurações de API com interceptors
grep -rl "axios.create\|interceptors" src/ --include="*.ts"

# Serviços HTTP
grep -rl "api\.(get|post|put|patch|delete)" src/services/ --include="*.ts"

# Mocks do axios em testes
grep -rl "jest.mock('axios')\|AxiosResponse\|AxiosError" src/ --include="*.ts"
```

Organize os resultados nas categorias:

| Categoria              | Padrão a buscar                                  | Prioridade | Exemplo                             |
| ---------------------- | ------------------------------------------------ | ---------- | ----------------------------------- |
| Configuração API       | `axios.create()`, `interceptors`                 | **Alta**   | `src/config/api.config.ts`          |
| Serviços HTTP          | `api.get()`, `api.post()`                        | **Alta**   | `src/services/*.service.ts`         |
| Hooks customizados     | `useQuery`, `useMutation` com serviços           | Média      | `src/hooks/**/*.hook.ts`            |
| Setup de testes        | `jest.mock('axios')`                             | **Alta**   | `jest.setup.ts`                     |
| MSW resolvers          | Validar consistência de contratos                | Média      | `src/mocks/resolvers/*.ts`          |
| Telemetry interceptors | Interceptors customizados (se existir)           | Alta       | `src/telemetry/interceptors.ts`     |
| `package.json`         | `axios`, `@types/axios`                          | **Alta**   | `package.json`                      |

## Arquitetura Alvo

Após a migração, o projeto terá a seguinte estrutura:

```
src/
├── config/
│   ├── api.config.ts              # API client com fetch + interceptors
│   └── fetch.config.ts            # Utilitários base do fetch
├── services/
│   ├── *.service.ts               # Serviços que usam API client
│   └── queryClient.config.ts     # TanStack Query config
├── hooks/
│   └── */*.hook.ts                # useQuery/useMutation (sem mudanças)
├── types/
│   └── http.types.ts              # Tipos de erro e resposta HTTP
└── tests/
    └── __mocks__/                 # Mocks (sem axios)
```

## Procedimento de Migração

Siga as etapas na ordem para garantir que cada passo seja validável com testes.

### Etapa 1: Criar tipos de erro HTTP customizados

Criar arquivo para centralizar tipos e tratamento de erro HTTP:

```typescript
// src/types/http.types.ts ou src/utils/http-error.ts
export class HttpError extends Error {
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
    this.name = 'HttpError';
    this.status = params.status;
    this.statusText = params.statusText;
    this.data = params.data;
    this.url = params.url;
  }

  static isHttpError(error: unknown): error is HttpError {
    return error instanceof HttpError;
  }
}

export interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  headers: Headers;
}
```

### Etapa 2: Criar utilitários base do fetch

Criar helpers genéricos para fetch (sem lógica de negócio):

```typescript
// src/config/fetch.config.ts
import { ApiResponse, HttpError } from '../types/http.types';

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
  timeout?: number;
}

/**
 * Wrapper base do fetch com tratamento de erro e query params
 * 
 * Segue boas práticas Vercel:
 * - client-swr-dedup: Usar com TanStack Query para deduplicação automática
 * - bundle-size: Fetch nativo = 0 bytes (axios = ~14KB)
 */
export const fetchWrapper = async <T = unknown>(
  url: string,
  options: FetchOptions = {}
): Promise<ApiResponse<T>> => {
  const { params, timeout = 30000, ...fetchOptions } = options;

  // Query params
  const queryString = params
    ? '?' + new URLSearchParams(params as Record<string, string>).toString()
    : '';
  const fullUrl = url + queryString;

  // Timeout via AbortController
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(fullUrl, {
      ...fetchOptions,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Parse response
    const contentType = response.headers.get('content-type');
    const data = contentType?.includes('application/json')
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      throw new HttpError({
        message: `HTTP Error ${response.status}: ${response.statusText}`,
        status: response.status,
        statusText: response.statusText,
        data,
        url: fullUrl,
      });
    }

    return {
      data: data as T,
      status: response.status,
      headers: response.headers,
    };
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof HttpError) {
      throw error;
    }

    // Network error ou timeout
    throw new HttpError({
      message: error instanceof Error ? error.message : 'Network request failed',
      status: 0,
      statusText: 'Network Error',
      data: null,
      url: fullUrl,
    });
  }
};
```

### Etapa 3: Migrar configuração da API e interceptors

**PONTO CRÍTICO**: Interceptors do axios precisam ser reimplementados como wrappers de função.

#### PADRÃO ATUAL (axios):

```typescript
// src/config/api.config.ts (ANTES)
import axios from 'axios';

const api = axios.create({
  baseURL: environment.baseURL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

// Interceptor de request: adiciona token
api.interceptors.request.use((request) => {
  if (request.url !== AUTH_PATH) {
    request.headers.Authorization = getAuthToken();
  }
  return request;
});

// Interceptor de response: refresh token em 401
api.interceptors.response.use(
  (response) => response,
  async (err) => {
    const { config, response } = err;
    const isTokenExpired = response?.status === 401;

    if (isTokenExpired && config.retry > 0) {
      config.retry -= 1;
      const newToken = await refreshToken();
      updateToken(newToken);
      return api(config);
    }

    return Promise.reject(err);
  }
);
```

#### NOVO PADRÃO (fetch com interceptors):

```typescript
// src/config/api.config.ts (DEPOIS)
import { fetchWrapper } from './fetch.config';
import { ApiResponse, HttpError } from '../types/http.types';
import { environment } from '../environment';
import { extranetAuth } from '../modules/ExtranetModule';
import { getFromLocalStorage, setInLocalStorage } from '../utils/localStorage';

interface ApiRequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>;
  timeout?: number;
  retry?: number;
  retryDelay?: number;
}

const AUTH_PATH = 'v1/auth';
const ALLOWLIST = ['/authentication'];
const POLICY = 'B2C_1A_JIT_SIGNUPORSIGNIN_PRD';

// Cache do token para evitar leituras repetidas do localStorage
// Segue: js-cache-storage (Vercel Best Practices)
let cachedToken: string | null = null;
let tokenCacheTime = 0;
const TOKEN_CACHE_DURATION = 5000; // 5 segundos

const getAuthToken = () => {
  const now = Date.now();
  
  // js-early-exit: retornar cache se válido
  if (cachedToken && (now - tokenCacheTime) < TOKEN_CACHE_DURATION) {
    return cachedToken;
  }
  
  const currentToken = getFromLocalStorage('CURRENT_TOKEN');
  const token = currentToken ? `Bearer ${currentToken}` : '';
  
  // Atualizar cache
  cachedToken = token;
  tokenCacheTime = now;
  
  return token;
};

// Função para invalidar cache (chamar após logout ou token refresh)
export const invalidateTokenCache = () => {
  cachedToken = null;
  tokenCacheTime = 0;
};

/**
 * API client com interceptors reimplementados como wrappers
 * 
 * Funcionalidades:
 * - Injeção automática de token de autenticação
 * - Refresh token automático em 401
 * - Retry com exponential backoff
 * - TypeScript type-safe
 */
class ApiClient {
  private baseURL: string;
  private defaultHeaders: HeadersInit;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Request interceptor: adiciona autenticação
   * Segue: js-early-exit (Vercel Best Practices)
   */
  private addAuthHeaders(url: string, headers: HeadersInit = {}): HeadersInit {
    // Early-exit: se não precisa auth, retorna logo
    const needsAuth = !url.includes(AUTH_PATH) && !ALLOWLIST.some((path) => url.includes(path));
    
    if (!needsAuth) {
      return headers;
    }

    return {
      ...headers,
      Authorization: getAuthToken(),
    };
  }

  /**
   * Response interceptor: handle token refresh em 401
   * Segue: js-early-exit (Vercel Best Practices)
   */
  private async handleAuthError<T>(
    error: unknown,
    retryRequest: () => Promise<ApiResponse<T>>,
    retriesLeft: number
  ): Promise<ApiResponse<T>> {
    // Early-exit: não é HttpError
    if (!HttpError.isHttpError(error)) {
      throw error;
    }

    // Early-exit: não é 401 ou sem retries
    if (error.status !== 401 || retriesLeft <= 0) {
      throw error;
    }

    // Apenas continua se for 401 com retries disponíveis
    {
      const { token, policy, updateToken } = extranetAuth();
      const isPolicyValid = token && policy.toUpperCase() !== POLICY;

      if (isPolicyValid) {
        const user = await updateToken();
        const newToken = user.token;
        const isNewTokenValid = newToken && !user.expired;

        if (isNewTokenValid) {
          setInLocalStorage('CURRENT_TOKEN', newToken);
          
          // IMPORTANTE: invalidar cache do token
          invalidateTokenCache();

          // Retry request com novo token
          await new Promise((resolve) => setTimeout(resolve, 1000));
          return retryRequest();
        }
      }
    }

    throw error;
  }

  /**
   * Método genérico para requisições HTTP
   */
  private async request<T = unknown>(
    method: string,
    endpoint: string,
    config: ApiRequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const { retry = 3, retryDelay = 1000, headers = {}, ...fetchOptions } = config;
    const url = `${this.baseURL}${endpoint}`;

    // Aplicar interceptors de request
    const requestHeaders = this.addAuthHeaders(url, {
      ...this.defaultHeaders,
      ...headers,
    });

    const makeRequest = async (retriesLeft: number): Promise<ApiResponse<T>> => {
      try {
        return await fetchWrapper<T>(url, {
          ...fetchOptions,
          method,
          headers: requestHeaders,
          credentials: 'include', // equivalente a withCredentials: true
        });
      } catch (error) {
        // Aplicar interceptor de response
        return this.handleAuthError(error, () => makeRequest(retriesLeft - 1), retriesLeft);
      }
    };

    return makeRequest(retry);
  }

  // Métodos públicos
  async get<T = unknown>(endpoint: string, config?: ApiRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, config);
  }

  async post<T = unknown>(
    endpoint: string,
    body?: unknown,
    config?: ApiRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, {
      ...config,
      body: JSON.stringify(body),
    });
  }

  async put<T = unknown>(
    endpoint: string,
    body?: unknown,
    config?: ApiRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', endpoint, {
      ...config,
      body: JSON.stringify(body),
    });
  }

  async patch<T = unknown>(
    endpoint: string,
    body?: unknown,
    config?: ApiRequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', endpoint, {
      ...config,
      body: JSON.stringify(body),
    });
  }

  async delete<T = unknown>(endpoint: string, config?: ApiRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', endpoint, config);
  }
}

// Instâncias exportadas
export const api = new ApiClient(environment.baseURL);
export const newApi = new ApiClient(environment.baseURLNew); // se houver múltiplas baseURLs

// Manter configuração global se necessário
export const globalConfig = {
  retry: 3,
  retryDelay: 1000,
};
```

**IMPORTANTE**: Se o projeto tiver interceptors de telemetry (ex: `src/telemetry/interceptors.ts`), eles também precisam ser migrados. Integrar no método `request` da classe `ApiClient`.

### Etapa 4: Migrar serviços HTTP

Os serviços HTTP geralmente NÃO precisam de mudanças significativas, apenas ajustes na extração de `data`:

#### ANTES (axios):

```typescript
// src/services/featureFlags.service.ts (ANTES)
import { api } from '../config/api.config';

export const getAllFeatureFlags = async (): Promise<FeatureFlagsResponse> => {
  const response = await api.get(ROUTES.FEATURE_FLAGS);
  return response?.data?.data; // axios: response.data contém o corpo
};
```

#### DEPOIS (fetch):

```typescript
// src/services/featureFlags.service.ts (DEPOIS)
import { api } from '../config/api.config';

export const getAllFeatureFlags = async (): Promise<FeatureFlagsResponse> => {
  const response = await api.get(ROUTES.FEATURE_FLAGS);
  // fetch: response.data JÁ É o corpo parseado
  return response.data?.data ?? response.data;
};
```

#### Tratamento de erro em serviços:

```typescript
// ANTES (axios)
import axios from 'axios';

export const getData = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Status:', error.response?.status);
    }
    throw error;
  }
};
```

```typescript
// DEPOIS (fetch)
import { HttpError } from '../types/http.types';

export const getData = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    if (HttpError.isHttpError(error)) {
      console.error('Status:', error.status);
    }
    throw error;
  }
};
```

### Etapa 5: Validar hooks (TanStack Query)

**BOA NOTÍCIA**: Hooks com TanStack Query **não precisam de mudanças** se os serviços mantiveram a mesma assinatura.

```typescript
// src/hooks/featureFlags/useGetFeatureFlagByKey.hook.ts
import { useQuery } from '@tanstack/react-query';
import { getFeatureFlagByKey } from '../../services/featureFlags.service';

/**
 * Hook para buscar feature flag por chave
 * 
 * Segue boas práticas Vercel:
 * - client-swr-dedup: TanStack Query deduplica requisições automaticamente
 * - rerender-dependencies: queryKey usa primitives (string)
 */
export const useGetFeatureFlagByKey = (key: string) => {
  return useQuery({
    queryKey: ['featureFlags', key],
    queryFn: () => getFeatureFlagByKey(key),
    // Configurações recomendadas para evitar re-fetches desnecessários
    staleTime: 1000 * 60 * 5, // 5 minutos
    gcTime: 1000 * 60 * 10,   // 10 minutos (antigo cacheTime)
  });
};

// ✅ Nenhuma mudança necessária na lógica!
// ✅ Apenas adicionar configurações de cache opcionais
```

**IMPORTANTE**: Se hooks usarem objetos como dependências, considerar memoização:

```typescript
// ❌ EVITAR: objeto recriado a cada render
export const useGetData = (filters: DataFilters) => {
  return useQuery({
    queryKey: ['data', filters], // objeto não é estável
    queryFn: () => getData(filters),
  });
};

// ✅ BOM: usar valores primitivos ou memo
import { useMemo } from 'react';

export const useGetData = (filters: DataFilters) => {
  // rerender-dependencies: usar primitives
  const queryKey = useMemo(
    () => ['data', filters.status, filters.page],
    [filters.status, filters.page]
  );
  
  return useQuery({
    queryKey,
    queryFn: () => getData(filters),
  });
};
```

### Etapa 6: Migrar testes

#### 6.1: Remover mocks do axios no jest.setup.ts

**ANTES:**

```typescript
// jest.setup.ts (ANTES)
jest.mock('axios', () => {
  return {
    ...jest.requireActual('axios'),
    create: () => ({
      interceptors: {
        request: { eject: jest.fn(), use: jest.fn() },
        response: { eject: jest.fn(), use: jest.fn() },
      },
    }),
  };
});
```

**DEPOIS:**

```typescript
// jest.setup.ts (DEPOIS)
// ✅ Remover completamente o mock do axios
```

#### 6.2: Validar MSW resolvers

MSW usa `fetch` por baixo, então **não precisa de mudanças**:

```typescript
// src/mocks/resolvers/getFeatureFlagByKey.ts
import { http, HttpResponse } from 'msw';

export const setFeatureFlagByKeyResolver = ({ status = 200, response = {} } = {}) => {
  return http.get('*/feature-flags/:key', () => {
    return HttpResponse.json({ data: response }, { status });
  });
};

// ✅ MSW já intercepta fetch nativamente
```

### Etapa 7: Remover dependências

```bash
npm uninstall axios
```

### Etapa 8: Validação final

1. **Build**: `npm run build`
2. **Testes**: `npm run test`
3. **Grep por referências residuais**:
   ```bash
   grep -r "from 'axios'\|import axios\|AxiosResponse\|AxiosError" src/ --include="*.ts" --include="*.tsx"
   ```
4. **Verificar bundle size reduzido** (~14KB menos)

## Checklist de Migração

- [ ] **Etapa 1**: Criar `src/types/http.types.ts` com `HttpError`
- [ ] **Etapa 2**: Criar `src/config/fetch.config.ts` com `fetchWrapper`
- [ ] **Etapa 3**: Migrar `src/config/api.config.ts` (API client + interceptors)
- [ ] **Etapa 4**: Migrar todos os serviços em `src/services/*.service.ts`
- [ ] **Etapa 5**: Validar hooks (geralmente sem mudanças)
- [ ] **Etapa 6**: Migrar testes (remover mock axios, validar MSW)
- [ ] **Etapa 7**: Remover `axios` do `package.json`
- [ ] **Etapa 8**: Validação final (build, testes, grep, bundle size)

## Otimizações Avançadas (Opcional)

### 1. Telemetria com WeakMap para performance

Se o projeto tiver telemetria, usar WeakMap para rastrear timing sem memory leak:

```typescript
// src/telemetry/fetch-telemetry.ts
import { ApiResponse, HttpError } from '../types/http.types';

// WeakMap permite garbage collection automático
// Segue: advanced-use-latest (Vercel Best Practices)
const requestTimings = new WeakMap<object, number>();

export const withTelemetry = async <T>(
  mfeName: string,
  fetchFn: () => Promise<ApiResponse<T>>,
  requestInfo: { url: string; method: string }
): Promise<ApiResponse<T>> => {
  const startTime = Date.now();
  const requestId = {}; // objeto único para usar como key
  
  requestTimings.set(requestId, startTime);

  try {
    const response = await fetchFn();
    const duration = Date.now() - startTime;

    // Track success sem bloquear o fluxo
    // Segue: js-request-idle-callback (Vercel Best Practices)
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        telemetry.trackRequest({
          url: requestInfo.url,
          method: requestInfo.method,
          status: response.status,
          duration,
          mfe: mfeName,
        });
      });
    } else {
      // Fallback para ambientes que não suportam requestIdleCallback
      setTimeout(() => {
        telemetry.trackRequest({
          url: requestInfo.url,
          method: requestInfo.method,
          status: response.status,
          duration,
          mfe: mfeName,
        });
      }, 0);
    }

    return response;
  } catch (error) {
    const duration = Date.now() - startTime;

    if (HttpError.isHttpError(error)) {
      // Track error de forma não-bloqueante
      if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
          telemetry.trackError(error, {
            url: requestInfo.url,
            method: requestInfo.method,
            status: error.status,
            duration,
            mfe: mfeName,
          });
        });
      }
    }

    throw error;
  }
};
```

### 2. Debounce de chamadas de API

Para filtros/busca, usar debounce para reduzir requisições:

```typescript
// src/hooks/search/useSearchDebounced.ts
import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { searchItems } from '@/services/search.service';

/**
 * Hook com debounce para evitar requisições desnecessárias
 * Segue: client-swr-dedup + rerender-use-deferred-value
 */
export const useSearchDebounced = (searchTerm: string, delay = 300) => {
  // Debounce manual com useMemo
  const debouncedSearchTerm = useDebouncedValue(searchTerm, delay);
  
  return useQuery({
    queryKey: ['search', debouncedSearchTerm],
    queryFn: () => searchItems(debouncedSearchTerm),
    enabled: debouncedSearchTerm.length >= 3, // mínimo 3 caracteres
  });
};

// Helper de debounce
const useDebouncedValue = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
};
```

### 3. Prefetch em hover para perceived performance

```typescript
// src/components/LinkWithPrefetch.tsx
import { useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';

/**
 * Link que faz prefetch ao hover
 * Segue: bundle-preload (Vercel Best Practices)
 */
export const LinkWithPrefetch = ({ to, fetchFn, queryKey, children }) => {
  const queryClient = useQueryClient();
  
  const handleMouseEnter = () => {
    // Prefetch nos dados ao passar o mouse
    queryClient.prefetchQuery({
      queryKey,
      queryFn: fetchFn,
    });
  };
  
  return (
    <Link 
      to={to} 
      onMouseEnter={handleMouseEnter}
      onFocus={handleMouseEnter} // também no focus (acessibilidade)
    >
      {children}
    </Link>
  );
};
```

### 4. Request deduplication manual (se não usar TanStack Query)

Apenas se não puder usar TanStack Query:

```typescript
// src/config/request-deduplicator.ts
// Segue: client-swr-dedup
const pendingRequests = new Map<string, Promise<any>>();

export const deduplicatedFetch = async <T>(
  key: string,
  fetchFn: () => Promise<T>
): Promise<T> => {
  // Se já existe requisição pendente, retorna a mesma Promise
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)!;
  }

  // Criar nova requisição
  const promise = fetchFn().finally(() => {
    // Limpar após completar
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, promise);
  return promise;
};

// Uso
const fetchUserData = (userId: string) => {
  return deduplicatedFetch(`user-${userId}`, () => 
    api.get(`/users/${userId}`)
  );
};
```

## Padrões Anti-pattern a Evitar

### Erro: "Headers is not defined" em testes

**Solução**: Adicionar polyfill de fetch no jest:

```bash
npm install --save-dev whatwg-fetch
```

```typescript
// jest.setup.ts
import 'whatwg-fetch';
```

### Erro: Refresh token não funciona

**Solução**: Garantir que `setInLocalStorage` foi chamado ANTES do retry:

```typescript
if (isNewTokenValid) {
  setInLocalStorage('CURRENT_TOKEN', newToken); // ← ANTES do retry
  invalidateTokenCache(); // ← IMPORTANTE: limpar cache
  return retryRequest();
}
```

### Erro: Requisições duplicadas após migração

**Causa**: TanStack Query pode não estar configurado corretamente.

**Solução**: Configurar o QueryClient com deduplicação:

```typescript
// src/services/queryClient.config.ts
import { QueryClient } from '@tanstack/react-query';

// Segue: client-swr-dedup (Vercel Best Practices)
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,     // 5 min: dados "fresh"
      gcTime: 1000 * 60 * 10,       // 10 min: manter em cache
      retry: 1,                      // Tentar 1x em caso de erro
      refetchOnWindowFocus: false,  // Evitar refetch ao focar janela
      refetchOnReconnect: false,    // Evitar refetch ao reconectar
    },
    mutations: {
      retry: 0, // Não retry em mutations
    },
  },
});
```

### Erro: Performance degradada em listas grandes

**Causa**: Re-renders desnecessários ao atualizar dados.

**Solução**: Usar seletores do TanStack Query:

```typescript
// ❌ EVITAR: re-render toda vez que qualquer campo muda
const { data } = useQuery({
  queryKey: ['items'],
  queryFn: getItems,
});

// ✅ BOM: re-render apenas quando os IDs mudam (rerender-derived-state)
const itemIds = useQuery({
  queryKey: ['items'],
  queryFn: getItems,
  select: (data) => data.map(item => item.id), // derivar durante render
});
```

### Erro: Token cache não invalida após logout

**Solução**: Chamar `invalidateTokenCache()` ao fazer logout:

```typescript
// src/hooks/auth/useLogout.ts
import { invalidateTokenCache } from '@/config/api.config';

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  const logout = () => {
    // Limpar localStorage
    removeFromLocalStorage('CURRENT_TOKEN');
    
    // IMPORTANTE: invalidar cache
    invalidateTokenCache();
    
    // Limpar todas as queries
    queryClient.clear();
    
    // Redirecionar
    navigate('/login');
  };
  
  return { logout };
};
```

## Padrões Anti-pattern a Evitar

### ❌ Anti-pattern 1: useEffect + fetch direto

**NUNCA fazer:**

```typescript
// ❌ ANTI-PATTERN: useEffect com fetch manual
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchData = async () => {
    setLoading(true);
    const response = await api.get('/data');
    setData(response.data);
    setLoading(false);
  };
  fetchData();
}, []);
```

**Fazer:**

```typescript
// ✅ BOM: usar TanStack Query
const { data, isLoading } = useQuery({
  queryKey: ['data'],
  queryFn: () => getData(),
});
```

### ❌ Anti-pattern 2: Objeto não memoizado em queryKey

**NUNCA fazer:**

```typescript
// ❌ ANTI-PATTERN: objeto inline causa re-fetch infinito
const filters = { status: 'active', page: 1 };
const { data } = useQuery({
  queryKey: ['items', filters], // objeto sempre diferente!
  queryFn: () => getItems(filters),
});
```

**Fazer:**

```typescript
// ✅ BOM: usar primitives ou useMemo
const { data } = useQuery({
  queryKey: ['items', filters.status, filters.page],
  queryFn: () => getItems(filters),
});

// OU com useMemo
const queryKey = useMemo(
  () => ['items', filters],
  [filters.status, filters.page]
);
```

### ❌ Anti-pattern 3: Fetch em loop sem cache

**NUNCA fazer:**

```typescript
// ❌ ANTI-PATTERN: leitura repetida do localStorage
const MyComponent = () => {
  return items.map(item => {
    const token = getFromLocalStorage('TOKEN'); // lido N vezes!
    return <Item key={item.id} token={token} />;
  });
};
```

**Fazer:**

```typescript
// ✅ BOM: cache de localStorage (js-cache-storage)
const MyComponent = () => {
  const token = getFromLocalStorage('TOKEN'); // lido 1 vez
  return items.map(item => (
    <Item key={item.id} token={token} />
  ));
};
```

### ❌ Anti-pattern 4: Componentes inline que causam re-renders

**NUNCA fazer:**

```typescript
// ❌ ANTI-PATTERN: componente inline recriado a cada render
const List = ({ items }) => {
  const ItemComponent = ({ item }) => <div>{item.name}</div>; // recriado!
  
  return items.map(item => <ItemComponent key={item.id} item={item} />);
};
```

**Fazer:**

```typescript
// ✅ BOM: componente fora (rerender-no-inline-components)
const ItemComponent = ({ item }) => <div>{item.name}</div>;

const List = ({ items }) => {
  return items.map(item => <ItemComponent key={item.id} item={item} />);
};
```

## Boas Práticas Vercel Aplicadas

Esta skill implementa as seguintes otimizações do Vercel React Best Practices:

### Bundle Size Optimization (CRITICAL)

✅ **`bundle-defer-third-party`**: Fetch nativo = **0 bytes** (axios = ~14KB)
- Redução imediata de bundle
- Melhora no First Load JS

✅ **`bundle-barrel-imports`**: Importar diretamente
```typescript
// ❌ Evitar
import { api } from '@/config';

// ✅ Preferir
import { api } from '@/config/api.config';
```

### Client-Side Data Fetching (MEDIUM-HIGH)

✅ **`client-swr-dedup`**: TanStack Query deduplica requisições automaticamente
- Múltiplos componentes chamando a mesma query = 1 request
- Cache compartilhado entre componentes

✅ **`client-event-listeners`**: Interceptors como funções puras
- Sem side effects globais
- Garbage collection eficiente

### JavaScript Performance (LOW-MEDIUM)

✅ **`js-cache-storage`**: Cache de token do localStorage
```typescript
let cachedToken: string | null = null;
const getAuthToken = () => {
  if (cachedToken) return cachedToken;
  cachedToken = getFromLocalStorage('CURRENT_TOKEN');
  return cachedToken;
};
```

✅ **`js-early-exit`**: Retornar cedo de funções
```typescript
private addAuthHeaders(url: string, headers: HeadersInit) {
  if (!needsAuth) return headers; // early-exit
  return { ...headers, Authorization: getAuthToken() };
}
```

✅ **`js-cache-function-results`**: Cache de resultados computados
- Token cache com TTL
- Evita re-computação

### Re-render Optimization (MEDIUM)

✅ **`rerender-dependencies`**: Usar primitives em queryKey
```typescript
// ✅ Bom
queryKey: ['data', id, status]

// ❌ Ruim
queryKey: ['data', { id, status }]
```

✅ **`rerender-derived-state-no-effect`**: Derivar durante render
- TanStack Query já retorna estado derivado (isLoading, isError)
- Não precisa useEffect para estados derivados

## Regras

- **Nunca** adicionar `axios` de volta como dependência
- **Sempre** usar `AbortController` para timeout quando necessário
- **Sempre** lançar `HttpError` em respostas não-ok para consistência
- **Nunca** mockar `fetch` globalmente em testes (usar MSW)
- **Sempre** usar TanStack Query para data fetching (nunca `useEffect` + `fetch`)
- **Sempre** tipificar respostas com generics: `api.get<Type>(url)`
- **Sempre** cachear valores do localStorage para evitar leituras repetidas
- **Sempre** usar early-exit em funções para melhor performance
- **Sempre** invalidar cache de token após refresh
- Seguir boas práticas do Vercel para bundle size e performance

## Referências

### Documentação Oficial

- [Vercel React Best Practices](https://vercel.com/docs/optimization/react) - Guia completo de otimização
- [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) - Client-side state management
- [MSW (Mock Service Worker)](https://mswjs.io/) - API mocking para testes
- [Fetch API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) - Documentação completa da Fetch API
- [AbortController - MDN](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) - Cancelamento de requests

### Regras Vercel Específicas Aplicadas

- **Bundle Size**: [bundle-defer-third-party](https://vercel.com/docs/optimization/react#bundle-defer-third-party)
- **Client Dedup**: [client-swr-dedup](https://vercel.com/docs/optimization/react#client-swr-dedup)
- **Cache Storage**: [js-cache-storage](https://vercel.com/docs/optimization/react#js-cache-storage)
- **Early Exit**: [js-early-exit](https://vercel.com/docs/optimization/react#js-early-exit)
- **Dependencies**: [rerender-dependencies](https://vercel.com/docs/optimization/react#rerender-dependencies)
- **No Inline Components**: [rerender-no-inline-components](https://vercel.com/docs/optimization/react#rerender-no-inline-components)

### Artigos e Recursos Adicionais

- [React Query vs SWR](https://tanstack.com/query/latest/docs/framework/react/comparison) - Comparação de bibliotecas
- [Web Vitals](https://web.dev/vitals/) - Métricas de performance web
- [JavaScript Performance](https://developer.mozilla.org/en-US/docs/Web/Performance) - Guia de performance MDN
