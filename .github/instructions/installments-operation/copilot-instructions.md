# Copilot Instructions - Installments Operation Portal

Este arquivo contém instruções e boas práticas para desenvolvimento neste repositório. Ele guia assistentes de IA (como Copilot) e desenvolvedores sobre convenções, padrões e fluxos do projeto.

---

## 📋 Visão Geral do Projeto

**Nome:** Jornada de títulos - Visão Operações  
**Tipo:** Microfrontend (MFE) React 18 com Module Federation (Webpack)  
**Descrição:** Repositório do microfrontend responsável pela jornada de títulos no portal de operações do Grupo Boticário.  
**Repositório:** https://github.com/grupoboticario/prodfin-caas-cfd-installments-operation-portal

### URLs de Acesso
| Ambiente       | URL                                                                    |
| -------------- | ---------------------------------------------------------------------- |
| Development    | https://dtitulos-portal-de-operacoes.grupoboticario.com.br            |
| Homologação    | https://htitulos-portal-de-operacoes.grupoboticario.com.br            |
| Produção       | https://titulos-portal-de-operacoes.grupoboticario.com.br             |
| SonarCloud     | https://sonarcloud.io/project/overview?id=...                         |
| Documentação   | https://alquimia.gb.tech/docs/default/component/documentacao-portais-de-credito |
| Kanbanize      | https://grupoboticario.kanbanize.com/ctrl_board/227/                  |

---

## 🛠️ Stack Técnico

### Core
- **React:** v18 (com JSX runtime automático)
- **TypeScript:** ES2022 target, strict mode
- **Module Federation:** Webpack - compartilhamento de dependências entre MFEs
- **Bundler:** Webpack 5 (configurações: dev, prod)

### Bibliotecas Principais
- **Flora:** Design system interno do GB (componentes reutilizáveis)
- **TanStack Query (React Query):** Gerenciamento de estado assíncrono e cache
- **Fetch API:** Requisições HTTP nativas (sem axios/node-fetch)
- **Husky:** Automação de tarefas via git hooks

### Qualidade de Código
- **ESLint:** Linting com Airbnb config + TypeScript plugin
- **Prettier:** Formatação automática
- **Jest:** Testes unitários e de integração
- **React Testing Library:** Testes de componentes (user-centric)

### Ambiente
- **Node.js:** v22 (obrigatório)
- **Package Manager:** Yarn v1 (⚠️ NÃO use npm)
- **OS Suportados:** macOS, Linux (Windows não suportado)

---

## 📁 Estrutura do Projeto

```
prodfin-caas-cfd-installments-operation-portal/
├── src/
│   ├── components/          # Componentes React reutilizáveis
│   │   ├── Button/
│   │   │   ├── index.ts                    # Exportação do componente
│   │   │   ├── Button.tsx                  # Componente principal
│   │   │   ├── Button.styled.ts            # Estilos (Styled Components)
│   │   │   └── Button.test.tsx             # Testes do componente
│   │   └── UserCodeFilter/                 # Agrupamento de componentes relacionados
│   │       ├── index.ts
│   │       └── elements.ts                 # Demais arquivos do componente
│   ├── pages/                              # Páginas/rotas da aplicação
│   │   ├── Home/
│   │   │   ├── index.ts
│   │   │   ├── Home.tsx
│   │   │   ├── Home.test.tsx
│   │   │   └── components/                 # Componentes específicos da página
│   │   └── UserList/
│   │       ├── UserListTable/
│   │       │   ├── index.ts
│   │       │   ├── UserListTable.tsx
│   │       │   ├── UserListTable.styled.ts
│   │       │   └── UserListTable.test.tsx
│   │       ├── index.ts
│   │       ├── UserList.tsx
│   │       └── UserList.test.tsx
│   ├── hooks/                              # Custom hooks reutilizáveis
│   │   ├── localStorage/
│   │   │   ├── useLocalStorage.hook.ts
│   │   │   ├── useLocalStorage.test.ts
│   │   │   └── index.ts
│   │   └── [context]/
│   ├── services/                           # Lógica de API e serviços
│   │   ├── auth.service.ts
│   │   ├── reports.service.ts
│   │   └── index.ts
│   ├── constants/                          # Constantes compartilhadas
│   │   ├── months.constants.ts
│   │   └── index.ts
│   ├── types/                              # Tipos TypeScript globais
│   │   ├── installments.types.ts
│   │   └── index.ts
│   ├── utils/                              # Funções utilitárias
│   │   ├── date/
│   │   │   ├── index.ts
│   │   │   ├── date.util.ts
│   │   │   └── date.test.ts
│   │   └── number/
│   │       ├── index.ts
│   │       ├── number.util.ts
│   │       └── number.test.ts
│   ├── mocks/                              # Configurações MSW
│   │   └── handlers.ts
│   ├── store/                              # Estado global (contexto, zustand, etc)
│   │   └── app.store.ts
│   ├── environment/
│   │   ├── index.ts
│   │   └── environment.ts
│   ├── assets/                             # Assets locais (não Flora)
│   │   ├── images/
│   │   └── videos/
│   ├── styles/                             # Estilos globais
│   │   └── globals.css
│   └── App.tsx                             # Componente raiz
├── public/                                 # Assets estáticos
├── kube/                                   # Configurações Kubernetes
├── .github/                                # Workflows e documentação
│   ├── copilot-instructions.md             # Este arquivo
│   └── skills/                             # Skills do Copilot
├── webpack.*.js                            # Configurações Webpack
├── package.json                            # Dependências e scripts
├── tsconfig.json                           # Configuração TypeScript
├── eslint.config.mjs                       # Configuração ESLint
├── .prettierrc                             # Configuração Prettier
├── jest.config.js                          # Configuração Jest
└── README.md                               # Documentação geral
```

### Princípios de Organização
- ✅ Um arquivo só deve ser movido para a pasta global se for **reutilizável**
- ✅ Máximo **3-4 níveis de pastas** para evitar profundidade excessiva
- ✅ Componentes genéricos devem ser **promovidos para Flora** quando aplicável
- ✅ Começar com estrutura **simples** e incrementar conforme necessidade
- ✅ **Evitar** muitas pastas vazias — manter apenas o necessário

---

## ⚙️ Configuração do Ambiente local

### Pré-requisitos
1. **Node.js v22** instalado
2. **Yarn v1** instalado
3. Conectado à VPN do GB
4. Token GitHub configurado para acessar o npm privado (@grupoboticario/flora)
   - [Guia de configuração do Flora](https://github.com/grupoboticario/flora/wiki/NPM-Registry#github-registry)
   - [Geração de token](https://sites.google.com/grupoboticario.com.br/engenhariadesoftware/ferramentas/github#h.h8s45z5nl27c)

### Instalação
1. Clone o repositório e repositórios dependentes:
   ```bash
   git clone https://github.com/grupoboticario/prodfin-caas-cfd-installments-operation-portal.git
   ```

2. Configure o arquivo `.env.local` (baseado em `.env.example`)

3. Instale as dependências:
   ```bash
   yarn install
   ```

### Com Mocks (MSW - Mock Service Worker)
1. Configure `USE_MSW_MOCKS=true` em `.env.local`
2. Execute setup em todos os repositórios:
   ```bash
   yarn setup-mock
   ```
3. Inicie normalmente:
   ```bash
   yarn start
   ```

---

## 🚀 Scripts Disponíveis

### Desenvolvimento
| Script | Descrição |
| --- | --- |
| `yarn start` | Inicia dev server com hot reload (porta 3000) |
| `yarn build` | Build para desenvolvimento |
| `yarn build:prd` | Build otimizado para produção |
| `yarn serve` | Inicia servidor local com build dev |
| `yarn serve:dev` | Build dev + serve |
| `yarn serve:prd` | Build prod + serve |

### Qualidade de Código
| Script | Descrição |
| --- | --- |
| `yarn lint-check` | Verifica ESLint (máx 10 warnings) |
| `yarn lint-fix` | Corrige problemas ESLint automaticamente |
| `yarn lint-check:report` | Gera relatório ESLint |
| `yarn prettier-check` | Verifica formatação Prettier |
| `yarn prettier-fix` | Formata código com Prettier |
| `yarn check-all` | Executa lint, prettier e testes |

### Testes
| Script | Descrição |
| --- | --- |
| `yarn test` | Executa testes (modo watch) |
| `yarn test:ci` | Testes com coverage para CI/CD |
| `yarn test:watch` | Watch mode |
| `yarn test:watch-all` | Watch all files |
| `yarn test:coverage` | Gera relatório de coverage |

---

## 🏗️ Convenções de Nomenclatura e Organização

### Nomenclatura de Arquivos e Pastas

#### Componentes (PascalCase)
Componentes e suas pastas **devem usar PascalCase**:

```bash
# ✅ Correto
components/Button/Button.tsx
components/SecondaryButton/SecondaryButton.tsx
components/TertiaryButton/TertiaryButton.tsx

# ❌ Evitar
components/button/button.tsx
components/secondary-button/secondary-button.tsx
```

#### Hooks, Utilitários, Serviços (camelCase)
Hooks, utilitários, serviços e pastas devem usar **camelCase com sufixo**:

```bash
# ✅ Correto
hooks/localStorage/useLocalStorage.hook.ts
utils/date/date.util.ts
services/auth.service.ts

# ❌ Evitar
hooks/UseLocalStorage.ts
Utils/LocalStorage.ts
utils/local-storage/local-storage.ts
```

### Extensões de Arquivos Obrigatórias

| Tipo | Extensão | Exemplo |
|------|----------|---------|
| Constantes | `.constants.ts` | `months.constants.ts` |
| Testes | `.test.ts/tsx` | `Button.test.tsx` |
| Styled Components | `.styled.ts` | `Button.styled.ts` |
| Custom Hooks | `.hook.ts` | `useLocalStorage.hook.ts` |
| Serviços | `.service.ts` | `auth.service.ts` |
| Utilitários | `.util.ts` | `date.util.ts` |
| Configurações | `.config.ts` | `featureFlags.config.ts` |
| Stores | `.store.ts` | `user.store.ts` |
| Tipagens | `.types.ts` ou `.d.ts` | `installments.types.ts` |

### Extensões Sem Sufixo Específico

| Tipo | Exemplo |
|------|---------|
| Componente | `Button.tsx` |
| Asset | `image.png` |
| Arquivo index | `index.ts` |

### Exportação via index.ts

#### Para Componentes e Pastas Específicas (✅ Recomendado)
```typescript
// ✅ Correto
import { Button } from '@components/Button'

// Arquivo: src/components/Button/index.ts
export { Button } from './Button';
```

#### Para Pastas Globais (❌ Não Recomendado - Evitar barrel imports)
```typescript
// ❌ Evitar
import { Button } from '@components'

// ✅ Correto - usar direto
import { Button } from '@components/Button'
```

### Conteúdo do arquivo index.ts

**O index.ts deve conter apenas exportações**, não implementação:

```typescript
// ✅ Correto
// src/components/Button/index.ts
export { Button } from './Button';

// Arquivo separado para implementação
// src/components/Button/Button.tsx
export const Button: React.FC<ButtonProps> = ({ ... }) => { ... };

// ❌ Evitar - implementação no index.ts
// src/components/Button/index.ts
export const Button: React.FC<ButtonProps> = ({ ... }) => { ... };
```

---

## 📂 Padrões por Tipo de Arquivo

### Componentes

**Estrutura recomendada:**
```
components/
  Button/
    index.ts                   # Exportação
    Button.tsx                 # Componente
    Button.styled.ts           # Estilos
    Button.test.tsx            # Testes
```

**Regras:**
- Um componente por pasta
- Use index.ts **apenas para exportação**
- Testes no mesmo nível do componente
- Estilos em `.styled.ts` para Styled Components

### Utilitários

**Estrutura recomendada:**
```
utils/
  date/
    index.ts                   # Exportação
    date.util.ts               # Funções
    date.test.ts               # Testes
  number/
    index.ts
    number.util.ts
    number.test.ts
```

**Regras:**
- Agrupar por contexto/tipo
- Um utilitário por pasta
- Testes junto ao utilitário
- Sempre usar `index.ts` para exportação

### Custom Hooks

**Para hooks genéricos (reutilizáveis):**
```
hooks/
  localStorage/
    useLocalStorage.hook.ts    # Hook
    useLocalStorage.test.ts    # Testes
    index.ts                   # Exportação
```

**Para hooks específicos de página:**
```
pages/
  DashboardPage/
    useDashboardPage.hook.ts   # Hook específico dessa página
    DashboardPage.tsx
    DashboardPage.test.ts
```

**Regras:**
- Hooks genéricos na pasta `hooks/` com contexto
- Hooks específicos junto à página que os usa
- Nomear com prefixo `use` + camelCase

### Serviços

**Estrutura recomendada:**
```
services/
  auth.service.ts              # Um serviço por arquivo
  reports.service.ts
  index.ts                     # Exportação (opcional)
```

**Regras:**
- **Não** separar por pastas se houver apenas 1 arquivo por contexto
- Separar só se houver múltiplos arquivos que se relacionam
- Nenhum hook deve estar em `services/`
- Testar apenas se houver lógica específica

### Páginas

**Estrutura recomendada:**
```
pages/
  Home/
    index.ts
    Home.tsx                   # Página principal
    Home.test.tsx
    HomeMenu/                  # Componentes específicos
      index.ts
      HomeMenu.tsx
      menuOptions.util.ts      # Utilitários da página
```

**Regras:**
- **Não** criar subpastas `utils/`, `components/`, `constants/` dentro de páginas
- Componentes específicos como subpastas dentro da página
- Utilitários e constantes junto aos componentes que os usam
- Reutilizar componentes globais quando possível

---

## 📝 Convenções de Código

### TypeScript
- **Target:** ES2022
- **Modo Strict:** Ativado (obrigatório)
- **Path aliases:** Configurados em `tsconfig.json` com baseUrl: `src`
- Sempre tipifique props, estados e retornos de funções
- Use tipos de interface para props de componentes

```typescript
// ✅ Correto
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, disabled }) => {
  return <button onClick={onClick} disabled={disabled}>{label}</button>;
};

// ❌ Evitar
const Button = ({ label, onClick, disabled }) => {
  // ...
};
```

### React & JSX
- **React v18:** Use o JSX runtime automático (sem import React)
- **Functional Components:** Sempre use exports nomeados
- **Hooks:** Respeite as regras dos hooks (ESLint enforcement)
- **Nomes:** PascalCase para componentes, camelCase para funções

```typescript
// ✅ Correto
export const MyComponent: React.FC<Props> = ({ prop }) => {
  const [value, setValue] = useState(null);
  
  useEffect(() => {
    // efeito
  }, [value]); // listar dependências
  
  return <div>{value}</div>;
};

// ❌ Evitar
const MyComponent = (props) => { /* ... */ };
export default MyComponent;
```

### Arquivo & Nomenclatura
- **Componentes:** `ComponentName.tsx`
- **Hooks:** `useHookName.ts`
- **Utilitários:** `utilityName.ts`
- **Tipos/Interfaces:** Defina no mesmo arquivo ou em `types/`
- **Testes:** `ComponentName.test.tsx` ou `__tests__/ComponentName.test.tsx`

### ESLint & Prettier
- **ESLint:** Airbnb config + TypeScript + Prettier integration
- **Prettier:** Configuração compartilhada (`.prettierrc`)
- **Pre-commit:** Husky garante lint/prettier antes de commit
- Máximo de 10 warnings permitidos em CI/CD

### Importações
- **Evite barrel imports** em hot paths (use imports diretos)
- **Agrupe imports:** React/libs externas, internos, types
- **Use path aliases** definidos em `tsconfig.json`
- **Prefira imports nomeados** (não default)

```typescript
// ✅ Correto
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { Button } from 'components/Button';
import { useLocalStorage } from 'hooks/localStorage';
import { API_URL } from 'constants/api.constants';

import type { User } from 'types/user';

// ❌ Evitar
import { Button } from './components';
import * as AllExports from '../file.ts';
import Button from './Button';  // default export
```

### Exportações

**Sempre exporte ao final do arquivo (não inline):**

```typescript
// ✅ Correto
interface ButtonProps {
  label: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ label, onClick }) => (
  <button onClick={onClick}>{label}</button>
);

// Exportações ao final
export { Button };
export type { ButtonProps };

// ❌ Evitar - export inline
export interface ButtonProps { ... }
export const Button: React.FC<ButtonProps> = ...
```

**Regras:**
- Declare componentes, funções, tipos e interfaces primeiro
- Agrupe todas as exportações ao final do arquivo
- Use named exports (evite `export default`)
- Separe `export { }` de `export type { }`

---

## 🧪 Testes

### Setup
- **Framework:** Jest + React Testing Library
- **Modo:** User-centric (simule comportamento do usuário)
- **Coverage:** Mínimo 80% (enforced em CI/CD)
- **Custom DOM:** Configuração JS (via `jsDomEnvironment.config.ts`)

### Localização dos Testes
- **Componentes:** `ComponentName.test.tsx` no mesmo nível do componente
- **Hooks:** `useHookName.test.ts` no mesmo nível do hook
- **Utilitários:** `utilityName.test.ts` no mesmo nível do utilitário
- **Serviços:** Apenas se houver lógica complexa a testar

```bash
# ✅ Correto
components/
  Button/
    Button.tsx
    Button.test.tsx          # Teste junto do componente

utils/
  date/
    date.util.ts
    date.test.ts             # Teste junto do utilitário
```

### Padrões de Testes

#### Nomenclatura
- **Describe:** Nome do componente/função testada
- **It/Test:** Descrever o comportamento esperado com verbo na terceira pessoa do singular

```typescript
// ✅ Correto
describe('Button', () => {
  it('renders button with label', () => { /* ... */ });
  it('calls onClick when clicked', () => { /* ... */ });
});

// ❌ Evitar
describe('test button', () => {
  it('should work', () => { /* ... */ });
});
```

#### Queries - Prioridade de Seleção
Preferir nesta ordem:
1. `getByRole` — Melhor acessibilidade e resiliência
2. `getByLabelText` — Bom para inputs
3. `getByTestId` — Último recurso, menos resiliente
4. `querySelector` — Evitar completamente

```typescript
// ✅ Correto - Role baseado
test('renders button with label', () => {
  render(<Button label="Click me" onClick={jest.fn()} />);
  expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
});

// ✅ Bom - Label
test('accepts user input', () => {
  render(<Input label="Name" />);
  expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
});

// ❌ Evitar - TestId
test('renders button', () => {
  render(<Button data-testid="button" />);
  expect(screen.getByTestId('button')).toBeInTheDocument();
});
```

#### Interações Assíncronas
Use `userEvent` e `waitFor` para simular comportamento real:

```typescript
// ✅ Correto
import { userEvent } from '@testing-library/user-event';

test('submits form', async () => {
  const user = userEvent.setup();
  render(<Form onSubmit={jest.fn()} />);
  
  await user.click(screen.getByRole('button', { name: /submit/i }));
  await waitFor(() => {
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });
});

// ❌ Evitar - fireEvent (menos realista)
fireEvent.click(screen.getByRole('button'));
```

#### Mocks HTTP
Use MSW (Mock Service Worker) para requisições:

```typescript
// ✅ Correto - MSW
import { server } from 'mocks/server';
import { rest } from 'msw';

test('fetches users', async () => {
  server.use(
    rest.get('/api/users', (req, res, ctx) => {
      return res(ctx.json([{ id: 1, name: 'John' }]));
    })
  );
  
  render(<UserList />);
  expect(await screen.findByText('John')).toBeInTheDocument();
});
```

### Coverage Mínimo
- **Componentes:** ≥ 80% de linhas cobertas
- **Hooks:** ≥ 80% de linhas cobertas
- **Utilitários:** ≥ 80% de linhas cobertas
- **Serviços:** Conforme necessário (complexidade)

Verificar com: `yarn test:coverage`

---

## 🎯 Padrões Arquiteturais

### Data Fetching
- **TanStack Query:** Use para queries assíncronas com cache automático
- **Fetch API:** Nativa (não use axios)
- **Services:** Organize chamadas API em arquivos `services/`

```typescript
// ✅ Correto - TanStack Query
const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await fetch('/api/users');
      return response.json();
    },
  });
};

// ❌ Evitar - useState + useEffect
const [users, setUsers] = useState(null);
useEffect(() => {
  fetch('/api/users').then(r => r.json()).then(setUsers);
}, []);
```

### State Management
- **Props Drilling:** Para estados simples
- **Context + useReducer:** Para estado global moderado
- **TanStack Query:** Cache server-side
- **React Hooks:** Preferred para local state

### Component Composition
- **Small & Focused:** Um propósito por componente
- **Composition over Inheritance:** Use children props
- **Custom Hooks:** Extraia lógica em hooks reutilizáveis
- **Memoization:** Use `React.memo` apenas para componentes caros (evite abuse)

```typescript
// ✅ Correto - Composição
export const Dialog: React.FC<DialogProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;
  return <Overlay onClick={onClose}>{children}</Overlay>;
};

export const DeleteDialog: React.FC<DeleteDialogProps> = (props) => (
  <Dialog {...props}>
    <p>Tem certeza que deseja deletar?</p>
    <Button label="Sim" onClick={props.onConfirm} />
  </Dialog>
);
```

---

## ⚡ Performance & Boas Práticas React (Vercel)

### Eliminar Waterfalls (CRÍTICO)
- Use `Promise.all()` para operações independentes
- Inicie promises cedo, await tarde
- Prefira `useTransition` para updates não-urgentes

```typescript
// ✅ Correto
const [data1, data2] = await Promise.all([
  fetch('/api/data1'),
  fetch('/api/data2'),
]);

// ❌ Evitar waterfalls
const data1 = await fetch('/api/data1');
const data2 = await fetch(`/api/data2?id=${data1.id}`);
```

### Otimização Bundle (CRÍTICO)
- **Importações diretas:** Evite barrel files em hot-path
- **Code splitting:** Use `React.lazy()` + `Suspense` para rotas pesadas
- **Dynamic imports:** Para componentes grandes (modais, drawers)
- **Tree-shaking:** Exporte named exports, não default

```typescript
// ✅ Correto - Code splitting
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

export const Page = () => (
  <Suspense fallback={<Spinner />}>
    <HeavyComponent />
  </Suspense>
);
```

### Re-render Optimization (MÉDIO)
- **Evite memorizações desnecessárias** (custo vs. benefício)
- **Extraia estado:** Coloque estado tão embaixo quanto possível (co-locate)
- **useCallback/useMemo:** Apenas para deps estáveis (objetos/arrays)
- **Deferred values:** Use `useDeferredValue` para updates não-críticos

```typescript
// ✅ Correto - Co-locate state
const Parent = () => {
  return (
    <Container>
      <ExpensiveComponent /> {/* não re-renda desnecessariamente */}
      <FormWithLocalState />
    </Container>
  );
};

const FormWithLocalState = () => {
  const [input, setInput] = useState('');
  return <input value={input} onChange={e => setInput(e.target.value)} />;
};
```

### Rendering Performance
- Use classes/classNames para mudar múltiplos estilos (não inline styles)
- `content-visibility: auto` para listas longas
- Evite `&&` para conditionals (use ternário)
- Preload recursos críticos (links, fontes)

```typescript
// ✅ Correto
const hasError = value === '';
return hasError ? <ErrorMessage /> : <SuccessMessage />;

// ❌ Evitar
return hasError && <ErrorMessage />;
```

---

## 🚨 Atenções Críticas

### Observações Importantes sobre Estrutura
- ⚠️ Um arquivo só deve ser movido para a pasta global se for **reutilizável**
- ⚠️ Evite profundidade excessiva — máximo **3-4 níveis de pastas**
- ⚠️ Quando possível, **promova componentes genéricos para Flora**
- ⚠️ **Comece simples** e incremente a estrutura conforme necessidade
- ⚠️ **Evite pastas vazias** — mantenha apenas o necessário

### Dependências
- ⚠️ **Use apenas Yarn v1** para instalar dependências (não npm)
- ⚠️ **Fetch API nativa:** Não instale axios ou node-fetch sem discussão com time
- ⚠️ **Flora:** Respeite versões e peer dependencies do design system

### Module Federation
- Coordene versões de dependências com o Container Portal
- Evite duplicação de libs pesadas (React, React-DOM, TanStack Query)
- Teste compartilhamento em dev com `local-server.js`

### Segurança
- Não comite `.env.local` ou secrets
- Valide inputs do usuário no servidor (não apenas cliente)
- Use CORS headers apropriados
- Evite eval() e dynamic require() desnecessários

### Git & CI/CD
- **Husky:** Bloqueia commits que falham lint/prettier/testes
- **Branch protection:** Main requer reviewers + passing checks
- **SonarCloud:** Análise de qualidade (máximo code smells tolerado)

---

## 📚 Recursos & Documentação

### Internas
- **Flora Design System:** https://github.com/grupoboticario/flora
- **Documentação Portais:** https://alquimia.gb.tech/docs/default/component/documentacao-portais-de-credito
- **Kanbanize Board:** https://grupoboticario.kanbanize.com/ctrl_board/227/
- **Figma Design:** Ver README.md para link

### Externas
- **React 18:** https://react.dev/
- **TypeScript:** https://www.typescriptlang.org/docs/
- **TanStack Query:** https://tanstack.com/query/latest/
- **Jest:** https://jestjs.io/docs/getting-started
- **React Testing Library:** https://testing-library.com/docs/react-testing-library/intro/
- **ESLint:** https://eslint.org/docs/
- **Webpack Module Federation:** https://webpack.js.org/concepts/module-federation/
- **Vercel React Best Practices:** https://vercel.com/blog/...

---

## 🔄 Fluxo de Desenvolvimento

### Modelo para Refinement de Novos Componentes

1. **Antes de refinar o componente:** Deve-se ter uma base com sugestões para iniciar a discussão. Dessa forma, a discussão é guiada e abre menos margem para divagações no tema.

2. **Antes de criar o componente:** Discutir com o time qual a melhor forma para ser feito e como deveria estar estruturado (combinados devem ser feitos preferencialmente no refining). Dessa forma, todos conseguem opinar sobre o problema e será possível chegar na melhor solução.

3. **Antes de considerar colocar um componente no Flora:** Entender o fluxo e validar viabilidade de outros projetos com a/o PD. Um componente só deve ser colocado no Flora se houver necessidade e alinhamento com outros times envolvidos.

### Local Development
```bash
# 1. Start todos os repositórios (ver lista em README.md)
yarn start

# 2. Develop em seu editor (hot reload automático)
# 3. Antes de commit: lint + prettier + testes
yarn check-all

# 4. Se tudo passou, faça commit
git add .
git commit -m "feat: descrição breve"
```

### Build & Deploy
```bash
# Development build
yarn build

# Production build (otimizado)
yarn build:prd

# Local serve para testar
yarn serve:prd
```

### Code Review Checklist
Para revisar código, verifique:
- ✅ ESLint e Prettier formatação
- ✅ Tipos TypeScript corretos
- ✅ Tests inclusos com coverage > 80%
- ✅ Boas práticas React (sem re-renders desnecessários)
- ✅ Sem console.logs em produção
- ✅ Mensagens de commit claras

---

## 📞 Contato & Suporte

- **Tech Lead:** [Name from team]
- **Slack:** #titulo-operacoes ou #engineering
- **Issues:** GitHub Issues neste repositório
- **Docs:** Alquimia documentation portal

---

**Última atualização:** Abril 2026  
**Mantido por:** Grupo Boticário - Engineering Team
